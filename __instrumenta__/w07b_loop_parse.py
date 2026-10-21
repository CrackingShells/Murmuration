# Parses session transcripts (a PI main .jsonl and its subagents/agent-*.jsonl) in parallel into one JSON per agent holding, per request (turn), model time, tool-phase time, client overhead, tokens, USD at list price, and per tool call its class, latency, result size, permission decision and a dependency-free test for batching; inputs: WAVE=LABEL=MAIN_JSONL triples, outputs: <outdir>/<label>_<agent>.json. Usage: w07b_loop_parse.py OUTDIR LABEL=MAIN_JSONL [LABEL=MAIN_JSONL ...]  (workers read from <MAIN_JSONL minus .jsonl>/subagents)
import json, sys, os, glob, re, datetime, time
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L

SKIP = ('{"type": "api-request-blob"', '{"type": "api-request-shape"')
TOK = re.compile(r"[A-Za-z0-9_@%+=:,~./-]{4,}")
READ_TOOLS = {"Read", "Glob", "Grep", "ToolSearch", "WebFetch", "WebSearch"}
FILE_TOOLS = {"Write", "Edit", "NotebookEdit"}
RO_WORDS = {"ls", "cat", "sed", "head", "tail", "wc", "grep", "rg", "stat", "file", "nl", "awk", "echo", "pwd", "test", "date", "jq", "diff", "cut", "sort", "uniq", "tr", "basename", "dirname", "realpath", "which", "du", "df", "uname", "sysctl", "printf", "true", "[", "column", "nproc", "id", "whoami", "env", "readlink", "md5", "shasum", "tree", "xxd", "od", "cd", "ps", "pgrep", "lsof"}
GIT_RO = {"log", "show", "diff", "status", "rev-parse", "branch", "ls-files", "blame", "cat-file", "shortlog", "describe", "remote", "config", "rev-list", "ls-tree", "stash"}
WRITE_VERB = re.compile(r"(^|[\s;&|(])(rm|mv|cp|mkdir|touch|chmod|tee|kill|sed\s+-i|git\s+(add|commit|push|checkout|merge|reset|rebase|apply|stash\s+(push|pop|apply|drop)|worktree|restore|clean|switch|pull|fetch))\b")


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def text_of(c):
    if isinstance(c, str):
        return c
    out = []
    for b in c or []:
        if isinstance(b, dict):
            if b.get("type") == "text":
                out.append(b.get("text", ""))
            elif b.get("type") == "tool_result":
                out.append(text_of(b.get("content")))
    return "\n".join(out)


def bash_readonly(cmd):
    """True when every pipeline segment starts with a read-only word and nothing is redirected to a file."""
    c = re.sub(r"\d?>\s*&\d|\d?>\s*/dev/null|2>&1", " ", cmd or "")
    if ">" in c.replace("->", "") and "<<" not in c.split(">")[0][-3:]:
        if re.search(r"(?<![<-])>", c):
            return False
    if WRITE_VERB.search(c):
        return False
    segs = re.split(r"&&|\|\||;|\||\n", c)
    for s in segs:
        w = s.strip().split()
        while w and re.match(r"^[A-Za-z_]+=\S*$", w[0]):
            w = w[1:]
        if not w:
            continue
        if w[0] == "git":
            rest = [x for x in w[1:] if not x.startswith("-")]
            if not rest or rest[0] not in GIT_RO:
                return False
            continue
        if w[0] in ("python3", "python", "uv", "bash", "sh", "node", "make", "claude", "cargo"):
            return False
        if w[0] not in RO_WORDS and not w[0].startswith("$(") and w[0] not in ("for", "do", "done", "if", "then", "fi", "while", "{", "}", "(", ")"):
            return False
    return True


def nseg(cmd):
    """Statements in a shell command: heredoc bodies and quoted strings removed, then split on && ; and newlines."""
    c = re.sub(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\b", " ", cmd or "", flags=re.S)
    c = re.sub(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"", "Q", c, flags=re.S)
    return len([x for x in re.split(r"&&|;|\n", c) if x.strip()])


def classify(name, inp):
    if name in READ_TOOLS:
        return "R"
    if name.startswith("mcp__") and re.search(r"(search|find_files|expand|list|status|read|query|resolve|get_|doctor)", name):
        return "R"
    if name in FILE_TOOLS:
        return "F"
    if name == "Bash":
        return "R" if bash_readonly(inp.get("command", "")) else "X"
    return "X"


def specific_tokens(text):
    out = set()
    for t in TOK.findall(text or ""):
        t = t.strip(".,:;=")
        if len(t) < 4:
            continue
        if "/" in t or re.search(r"[A-Za-z0-9]\.[A-Za-z]{1,5}$", t) or len(t) >= 12:
            out.add(t)
    return out


def call_text(name, inp):
    if name == "Bash":
        return inp.get("command", "")
    return " ".join(str(v) for v in inp.values() if isinstance(v, (str, int)))


def parse_one(args):
    label, path, agent = args
    t0 = time.time()
    reqs, msgs, order, results, events = {}, {}, [], {}, []
    prompts = []  # (ts, text)
    hooks = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(SKIP):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            t = r.get("type")
            if t == "api-request":
                reqs[r["id"]] = {"ts": ts(r["timestamp"]), "src": r.get("querySource")}
            elif t == "assistant" and isinstance(r.get("message"), dict):
                m = r["message"]
                if m.get("model") == "<synthetic>":
                    continue
                mid = m.get("id")
                e = msgs.get(mid)
                tt = ts(r["timestamp"])
                if e is None:
                    e = msgs[mid] = {"ref": r.get("requestRef"), "first": tt, "last": tt, "calls": [], "usage": {}, "model": m.get("model"), "stop": None, "think_ms": 0, "text_chars": 0, "sid": r.get("isSidechain")}
                    order.append(mid)
                e["last"] = max(e["last"], tt)
                if m.get("stop_reason"):
                    e["stop"] = m["stop_reason"]
                L.merge_usage(e["usage"], m.get("usage") or {})
                e["think_ms"] += int(r.get("thinkingDurationMs") or 0)
                for b in m.get("content") or []:
                    if b.get("type") == "tool_use":
                        e["calls"].append({"id": b["id"], "name": b["name"], "input": b.get("input") or {}, "ts": tt})
                    elif b.get("type") == "text":
                        e["text_chars"] += len(b.get("text") or "")
                        e.setdefault("texts", []).append(b.get("text") or "")
            elif t == "user":
                c = (r.get("message") or {}).get("content")
                tt = ts(r["timestamp"])
                got = False
                if isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "tool_result":
                            got = True
                            txt = text_of(b.get("content"))
                            pd = r.get("permissionDecision") or {}
                            results[b["tool_use_id"]] = {"ts": tt, "chars": len(txt), "err": bool(b.get("is_error")), "text": txt[:200000],
                                                         "pd": "%s/%s/%s" % (pd.get("decision"), pd.get("source"), pd.get("reasonType")) if pd else None,
                                                         "cls": bool(r.get("serverClassifierContext"))}
                if not got:
                    txt = text_of(c)
                    prompts.append((tt, txt, bool(r.get("isMeta"))))
            elif t == "attachment":
                a = r.get("attachment") or {}
                at = a.get("type")
                if at in ("hook_success", "hook_cancelled"):
                    hooks.append({"ts": ts(r["timestamp"]), "event": a.get("hookEvent"), "name": a.get("hookName"), "ms": int(a.get("durationMs") or 0), "timed_out": a.get("timedOut")})
                elif at in ("queued_command",):
                    prompts.append((ts(r["timestamp"]), str(a.get("prompt"))[:5000], False))
                elif at in ("hook_additional_context", "instructions", "prompt_snapshot", "mcp_instructions_delta", "deferred_tools_record"):
                    prompts.append((ts(r["timestamp"]), json.dumps(a)[:400000] if at != "deferred_tools_record" else "", True))
    # ---- turns
    turns = []
    seen = {}  # token -> (turn index, source)
    for (tt, txt, meta) in prompts:
        if tt <= (msgs[order[0]]["first"] if order else 1e18):
            for tk in specific_tokens(txt):
                seen.setdefault(tk, (-1, "prompt"))
    # later prompts (resume messages) are added at the turn that follows them
    pend = sorted(prompts)
    pi = 0
    loaded = {}          # deferred tool name -> turn index at which a ToolSearch loaded it (query select: list, or a name in its result)
    prev_sets = []       # word sets of the previous turn's calls, for the refinement test
    DEFERRED = lambda n: n.startswith("mcp__") or n in ("SendMessage", "WebFetch", "WebSearch", "Monitor")
    prev_end = None      # last result ts of the previous turn (None when it had no call)
    prev_msg_last = None
    for k, mid in enumerate(order):
        m = msgs[mid]
        ref = reqs.get(m["ref"])
        R = ref["ts"] if ref else None
        E = m["last"]
        calls = m["calls"]
        rs = [results.get(c["id"]) for c in calls]
        rts = [x["ts"] for x in rs if x]
        P = max(rts) if rts else None
        u = m["usage"]
        cc = u.get("cache_creation") or {}
        cw1, cw5 = int(cc.get("ephemeral_1h_input_tokens") or 0), int(cc.get("ephemeral_5m_input_tokens") or 0)
        cw5 += max(0, int(u.get("cache_creation_input_tokens") or 0) - cw1 - cw5)
        cr = int(u.get("cache_read_input_tokens") or 0)
        inp = int(u.get("input_tokens") or 0)
        out = int(u.get("output_tokens") or 0)
        usd = L.message_usd(m["model"], u) or 0.0
        # prompts arriving before this turn's start (resume messages, notifications)
        start = R if R is not None else m["first"]
        newp = []
        while pi < len(pend) and pend[pi][0] <= start:
            newp.append(pend[pi]); pi += 1
        # token bookkeeping for dependency tests, before this turn adds its own
        tcalls = []
        for c, r_ in zip(calls, rs):
            tk = specific_tokens(call_text(c["name"], c["input"]))
            dep_idx = [seen[x][0] for x in tk if x in seen and seen[x][1] == "res"]
            unk = [x for x in tk if x not in seen]
            if DEFERRED(c["name"]) and c["name"] in loaded:
                dep_idx.append(loaded[c["name"]])      # the call needs the schema a ToolSearch returned
            words = set(w for w in re.split(r"\s+", call_text(c["name"], c["input"])) if len(w) >= 3)
            jac = max([len(words & q) / max(1, len(words | q)) for q in prev_sets] or [0.0])
            tcalls.append({"name": c["name"], "cls": classify(c["name"], c["input"]), "ntok": len(tk), "dep_idx": dep_idx, "n_unseen": len(unk),
                           "jac": round(jac, 2), "nseg": nseg(c["input"].get("command", "")) if c["name"] == "Bash" else 0,
                           "errh": re.sub(r"[A-Za-z0-9_-]{32,}", "<id>", r_["text"][:70].replace("\n", " ")) if (r_ and r_["err"]) else "", "path": (c["input"].get("file_path") or c["input"].get("path") or "") if c["name"] != "Bash" else "",
                           "cmd0": (c["input"].get("command", "").strip().split() or [""])[0][:20] if c["name"] == "Bash" else "",
                           "lat": (r_["ts"] - c["ts"]) if r_ else None, "chars": r_["chars"] if r_ else 0, "err": r_["err"] if r_ else None,
                           "pd": r_["pd"] if r_ else None, "cls_ctx": r_["cls"] if r_ else None,
                           "head": " ".join(str(c["input"].get(k)) for k in ("file_path", "path", "pattern", "query") if c["input"].get(k))[:90] if c["name"] != "Bash" else ""})
        wait = None
        if k > 0:
            if prev_end is None:
                wait = (R if R is not None else m["first"]) - prev_msg_last   # resume after a turn with no tool call
        gap_prev = None if (k == 0 or prev_end is None or R is None) else R - prev_end
        turns.append({"k": k, "mid": mid[-8:], "R": R, "E": E, "first": m["first"], "model_s": (E - R) if R is not None else None,
                      "ttfb_s": (m["first"] - R) if R is not None else None,
                      "tool_s": (P - E) if (P is not None and calls) else None, "gap_prev_s": gap_prev,
                      "pre_s": (E - prev_end) if (prev_end is not None) else None,
                      "wait_s": wait, "ncalls": len(calls), "calls": tcalls, "out": out, "cr": cr, "cw5": cw5, "cw1": cw1, "inp": inp,
                      "usd": usd, "model": m["model"], "think_ms": m["think_ms"], "stop": m["stop"], "text_chars": m["text_chars"],
                      "new_prompt": bool(newp and k > 0), "missing_results": sum(1 for x in rs if not x)})
        # add tokens: this turn's assistant output (calls and text), then results; prompts that arrived
        for (tt, txt, meta) in newp:
            for tk in specific_tokens(txt):
                seen.setdefault(tk, (k, "prompt"))
        for c in calls:
            for tk in specific_tokens(call_text(c["name"], c["input"])):
                seen.setdefault(tk, (k, "asst"))
        for tx in m.get("texts", []):
            for tk in specific_tokens(tx):
                seen.setdefault(tk, (k, "asst"))
        for r_ in rs:
            if r_:
                for tk in specific_tokens(r_["text"][:100000]):
                    seen.setdefault(tk, (k, "res"))
        for c, r_ in zip(calls, rs):
            if c["name"] == "ToolSearch":
                q = str(c["input"].get("query") or "")
                names = re.findall(r"mcp__[A-Za-z0-9_\-]+|SendMessage|WebFetch|WebSearch|Monitor", q) + (re.findall(r"mcp__[A-Za-z0-9_\-]+", r_["text"]) if r_ else [])
                for nm_ in names:
                    loaded.setdefault(nm_, k)
        prev_sets = [set(w for w in re.split(r"\s+", call_text(c["name"], c["input"])) if len(w) >= 3) for c in calls]
        prev_end = P if calls else None
        prev_msg_last = E
    meta = {}
    try:
        meta = json.load(open(path[:-6] + ".meta.json"))
    except Exception:
        pass
    n_reqs_noasst = sum(1 for rid in reqs if rid not in {m["ref"] for m in msgs.values()})
    out = {"label": label, "agent": agent, "name": meta.get("name") or agent, "type": meta.get("agentType"), "file_mb": os.path.getsize(path) / 1e6,
           "turns": turns, "hooks": hooks, "n_requests_no_assistant": n_reqs_noasst, "reqsrc": sorted({v["src"] for v in reqs.values() if v["src"]}),
           "parse_s": time.time() - t0, "has_req_ts": bool(reqs)}
    return out


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    jobs = []
    for spec in sys.argv[2:]:
        label, main_path = spec.split("=", 1)
        jobs.append((label, main_path, "PI"))
        for f in sorted(glob.glob(main_path[:-6] + "/subagents/agent-*.jsonl")):
            jobs.append((label, f, os.path.basename(f)[6:-6]))
    jobs.sort(key=lambda j: -os.path.getsize(j[1]))
    t0 = time.time()
    with Pool(min(10, len(jobs))) as p:
        res = p.map(parse_one, jobs, chunksize=1)
    wall = time.time() - t0
    cpu = sum(r["parse_s"] for r in res)
    for r in res:
        with open(os.path.join(outdir, "%s_%s.json" % (r["label"], r["agent"])), "w") as fh:
            json.dump(r, fh)
    print("parsed %d transcripts, %.1f MB, wall %.1f s, sum of per-file parse time %.1f s (speed-up %.1fx)" % (len(res), sum(r["file_mb"] for r in res), wall, cpu, cpu / wall))


if __name__ == "__main__":
    main()
