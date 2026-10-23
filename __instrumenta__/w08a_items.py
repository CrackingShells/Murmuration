# Extracts, per worker transcript (subagents/agent-*.jsonl of the given sessions), the sequence of requests with usage and the items that entered the context between requests (tool results, hook-injected text, messages), each classified by source class and subclass, with characters; inputs: LABEL=MAIN_JSONL pairs (workers read from <MAIN minus .jsonl>/subagents); output: one JSON per worker in OUTDIR (no transcript text, only class keys, path kinds and character counts). Usage: w08a_items.py OUTDIR LABEL=MAIN_JSONL [...]
import json, sys, os, glob, re, shlex
from multiprocessing import Pool

SKIP = ('{"type": "api-request-blob"', '{"type": "api-request-shape"', '{"type": "api-request"')
LAB_MARK = re.compile(r"(__statera__|__design__|__pondus__|__reports__|__scrupuli__|__instrumenta__|__roadmap__|scripts|skills|agents|hooks|templates|commands|references)/(.*)$")
SRC_EXT = (".py", ".sh", ".js", ".ts", ".rs", ".json", ".jsonl", ".toml", ".yaml", ".yml", ".css", ".html", ".svelte", ".ipynb", ".wl", ".m")
DOC_EXT = (".md", ".txt", ".rst")
DATA_EXT = (".tsv", ".csv", ".log", ".out", ".output")


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


def path_kind(p):
    """(class, kind) of a file path: lab document by kind, source code, scratch data, other document."""
    if not p:
        return ("other", "no path")
    base = os.path.basename(p)
    m = LAB_MARK.search(p)
    d, rest = (m.group(1), m.group(2)) if m else ("", "")
    if d == "__statera__":
        if re.match(r"wave-\d+\.md$", rest): return ("doc", "wave note")
        if rest == "synthesis.md": return ("doc", "synthesis")
        if rest == "user_words.md": return ("doc", "user_words")
        if rest.startswith("harness"): return ("doc", "harness log")
        return ("doc", "statera other")
    if d == "__design__": return ("doc", "framing") if rest == "framing.md" else ("doc", "design other")
    if d == "__pondus__": return ("doc", "claim file")
    if d == "__reports__":
        if base.endswith(DOC_EXT): return ("doc", "report")
        return ("doc", "report data (tsv/json/py)")
    if d == "__scrupuli__": return ("doc", "puzzle file")
    if d == "__roadmap__": return ("doc", "roadmap")
    if d in ("skills", "agents", "templates", "commands", "references") or base in ("AGENTS.md", "CLAUDE.md"):
        if base.endswith(DOC_EXT): return ("doc", "brief protocol (skills/agents/templates)")
        return ("src", "plugin source")
    if d in ("scripts", "hooks", "__instrumenta__"): return ("src", "source: " + d)
    if base.endswith(SRC_EXT): return ("src", "source code (other)")
    if base.endswith(DOC_EXT): return ("doc", "other document")
    if base.endswith(DATA_EXT) or p.startswith("/private/tmp") or "/tmp/" in p: return ("other", "scratch/data file")
    return ("other", "file (other)")


PATHTOK = re.compile(r"[\w$\{\}./~@%+=-]*[\w}]\.(?:md|txt|py|sh|js|json|jsonl|tsv|csv|log|toml|yaml|yml|rs|ipynb)\b|[\w$\{\}./~-]*(?:__statera__|__design__|__pondus__|__reports__|__scrupuli__|__instrumenta__)/[\w$\{\}./*~-]+")


def seg_words(seg):
    try:
        w = shlex.split(seg, posix=True)
    except ValueError:
        w = seg.split()
    while w and re.match(r"^[A-Za-z_]+=\S*$", w[0]):
        w = w[1:]
    return w


def classify_bash(cmd):
    """(class, kind) for a Bash command. Priority: lab script run > document/source read > git > search > other."""
    c = cmd or ""
    # drop heredoc bodies for segment analysis
    c0 = re.sub(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\b", " ", c, flags=re.S)
    segs = [s for s in re.split(r"&&|\|\||;|\||\n", c0) if s.strip()]
    runs, reads, gits, searches, others = [], [], [], [], []
    for s in segs:
        w = seg_words(s)
        if not w:
            continue
        w0 = os.path.basename(w[0])
        if w0 in ("cd", "echo", "true", "export", "set", "S=", "for", "do", "done", "if", "then", "fi", "printf", "test", "[", "wait", "sleep", "timeout") and not (w0 == "timeout"):
            continue
        if w0 == "timeout" and len(w) > 2:
            w = w[2:]; w0 = os.path.basename(w[0])
        if w0 in ("python3", "python", "uv", "bash", "sh", "node", "zsh") or w[0].startswith("./") or re.match(r".*\.(py|sh)$", w[0]):
            args = [x for x in w[1:] if not x.startswith("-")]
            if w0 == "uv" and args[:1] == ["run"]:
                args = args[1:]
                args = [x for x in args if x not in ("python", "python3")]
            tgt = w[0] if (w[0].startswith("./") or w[0].endswith((".py", ".sh"))) else (args[0] if args else "")
            if "<<" in s and not tgt:
                runs.append(("script", "inline python/heredoc"))
            elif "-c" in w[1:3] and w0 in ("python3", "python"):
                runs.append(("script", "inline python -c"))
            elif tgt in ("-", ""):
                runs.append(("script", "inline python/heredoc"))
            else:
                b = os.path.basename(tgt)
                if "__instrumenta__/" in tgt: runs.append(("script", "__instrumenta__/" + b))
                elif "scripts/" in tgt: runs.append(("script", "scripts/" + b))
                elif b.endswith((".py", ".sh")): runs.append(("script", "own scratch script"))
                else: runs.append(("other", "bash/python other"))
            continue
        if w0 in ("cat", "sed", "head", "tail", "nl", "less", "bat", "awk", "wc", "xxd", "od", "cut", "column", "jq", "diff", "sort", "uniq", "tr"):
            paths = [t for t in PATHTOK.findall(s)] or [x for x in w[1:] if "/" in x and not x.startswith("-")]
            if paths:
                cl, kd = path_kind(paths[0])
                reads.append((cl, kd, w0))
            else:
                others.append(("other", "shell " + w0))
            continue
        if w0 == "git":
            gits.append(("git", "git"))
            continue
        if w0 in ("grep", "rg", "find", "colgrep", "ag", "fd"):
            searches.append(("search", w0 + " (shell)"))
            continue
        others.append(("other", "shell " + w0))
    if runs:
        return runs[0]
    if reads:
        cl, kd, w0 = reads[0]
        return ("bashdoc" if cl == "doc" else ("bashsrc" if cl == "src" else "bashother"), kd + " via " + w0)
    if gits: return gits[0]
    if searches: return searches[0]
    return others[0] if others else ("other", "shell (other)")


def classify_call(name, inp):
    if name == "Read":
        cl, kd = path_kind(inp.get("file_path", ""))
        part = " (section)" if (inp.get("offset") or inp.get("limit")) else ""
        return ({"doc": "readdoc", "src": "readsrc"}.get(cl, "readother"), kd + part)
    if name == "Bash":
        return classify_bash(inp.get("command", ""))
    if name in ("Grep", "Glob"):
        return ("search", name + " tool")
    if name.startswith("mcp__"):
        if "colgrep" in name:
            return ("search", "colgrep " + name.split("__")[-1])
        return ("web", name.split("__")[1] + ":" + name.split("__")[-1])
    if name in ("WebFetch", "WebSearch"):
        return ("web", name)
    if name == "ToolSearch":
        return ("other", "ToolSearch (schemas)")
    return ("other", name)


def parse_one(args):
    label, path, agent = args
    msgs, order = {}, []
    events = []  # ("msg", mid) | ("res", id, chars) | ("att", cls, kind, chars) | ("prompt", chars, kind)
    results = {}
    first_user = True
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(SKIP):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            t = r.get("type")
            if t == "assistant" and isinstance(r.get("message"), dict):
                m = r["message"]
                if m.get("model") == "<synthetic>":
                    continue
                mid = m.get("id")
                e = msgs.get(mid)
                if e is None:
                    e = msgs[mid] = {"usage": {}, "model": m.get("model"), "calls": [], "ts": r.get("timestamp"), "sig": 0, "text": 0}
                    order.append(mid)
                    events.append(("msg", mid))
                u = m.get("usage") or {}
                for f in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
                    e["usage"][f] = max(int(e["usage"].get(f) or 0), int(u.get(f) or 0))
                if isinstance(u.get("cache_creation"), dict):
                    e["usage"]["cache_creation"] = u["cache_creation"]
                if u.get("speed") == "fast":
                    e["usage"]["speed"] = "fast"
                for b in m.get("content") or []:
                    if b.get("type") == "thinking":
                        e["sig"] += len(b.get("signature") or "") + len(b.get("thinking") or "")
                    elif b.get("type") == "text":
                        e["text"] += len(b.get("text") or "")
                    if b.get("type") == "tool_use" and b["id"] not in {c["id"] for c in e["calls"]}:
                        e["calls"].append({"id": b["id"], "name": b["name"], "input": b.get("input") or {}})
            elif t == "user":
                c = (r.get("message") or {}).get("content")
                got = False
                if isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "tool_result":
                            got = True
                            txt = text_of(b.get("content"))
                            events.append(("res", b["tool_use_id"], len(txt), bool(b.get("is_error"))))
                if not got:
                    txt = text_of(c)
                    events.append(("prompt", len(txt), "brief (first prompt)" if first_user else "message / resume prompt"))
                first_user = False
            elif t == "attachment":
                a = r.get("attachment") or {}
                at = a.get("type")
                if at == "hook_additional_context":
                    n = len("\n".join(a.get("content") or []) if isinstance(a.get("content"), list) else str(a.get("content") or ""))
                    nm = a.get("hookName") or ""
                    events.append(("att", "hook", "hook additionalContext: " + re.sub(r":.*", "", nm) , n))
                elif at == "total_tokens_reminder":
                    events.append(("att", "hook", "total_tokens reminder", len(a.get("text") or "")))
                elif at == "queued_command":
                    events.append(("att", "msg", "queued command / task notice", len(str(a.get("prompt") or ""))))
                elif at in ("hook_success", "hook_cancelled", "prompt_snapshot", "deferred_tools_record", "credential_org", "remote_session_change", "auto_mode"):
                    pass
                else:
                    events.append(("att", "harness", at, len(json.dumps(a))))
    # build turns: turn k = request k; items entering before request k (k>=1) are listed in turn k's "in"
    turns = []
    cur_in = []
    pending_calls = {}
    for ev in events:
        if ev[0] == "msg":
            m = msgs[ev[1]]
            u = m["usage"]
            cc = u.get("cache_creation") or {}
            cw1, cw5 = int(cc.get("ephemeral_1h_input_tokens") or 0), int(cc.get("ephemeral_5m_input_tokens") or 0)
            cw5 += max(0, int(u.get("cache_creation_input_tokens") or 0) - cw1 - cw5)
            turns.append({"mid": ev[1][-8:], "model": m["model"], "ts": m["ts"], "inp": int(u["input_tokens"]), "out": int(u["output_tokens"]), "cr": int(u["cache_read_input_tokens"]), "cw1": cw1, "cw5": cw5,
                          "fast": u.get("speed") == "fast", "in": cur_in, "ncalls": len(m["calls"]),
                          "call_chars": sum(len(json.dumps(c["input"])) for c in m["calls"]), "sig_chars": m["sig"], "text_chars": m["text"]})
            cur_in = []
            for c in m["calls"]:
                pending_calls[c["id"]] = (c["name"], c["input"], len(turns) - 1)
        elif ev[0] == "res":
            nm, inp, k = pending_calls.get(ev[1], ("?", {}, -1))
            cl, kd = classify_call(nm, inp)
            ref = ""
            if nm == "Read":
                ref = os.path.basename(inp.get("file_path", ""))
                m_ = LAB_MARK.search(inp.get("file_path", ""))
                ref = (m_.group(1) + "/" + m_.group(2)) if m_ else inp.get("file_path", "").split("/")[-1]
            elif nm == "Bash":
                cmd = inp.get("command", "")
                if cl == "script":
                    ref = kd
                else:
                    pts = PATHTOK.findall(cmd)
                    if pts:
                        m_ = LAB_MARK.search(pts[0]); ref = (m_.group(1) + "/" + m_.group(2)) if m_ else pts[0].split("/")[-1]
                ref = ref[:100]
            turns_ref = k
            # offset/limit used on Read
            cur_in.append({"cls": cl, "kind": kd, "ref": ref, "tool": nm, "chars": ev[2], "err": ev[3], "call_turn": k})
        elif ev[0] == "att":
            cur_in.append({"cls": ev[1], "kind": ev[2], "ref": "", "tool": "attachment", "chars": ev[3], "call_turn": -1})
        elif ev[0] == "prompt":
            cur_in.append({"cls": "msg" if ev[2].startswith("message") else "brief", "kind": ev[2], "ref": "", "tool": "prompt", "chars": ev[1], "call_turn": -1})
    # leading items before first request (brief, SubagentStart hook) belong to the base interval
    first_items = []
    # turns[0]["in"] was filled before the first msg event
    meta = {}
    try:
        meta = json.load(open(path[:-6] + ".meta.json"))
    except Exception:
        pass
    name = meta.get("name") or ""
    return {"label": label, "agent": agent, "name": name, "type": meta.get("agentType"), "turns": turns, "trailing": cur_in}


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    jobs = []
    for spec in sys.argv[2:]:
        label, main_path = spec.split("=", 1)
        for f in sorted(glob.glob(main_path[:-6] + "/subagents/agent-*.jsonl")):
            jobs.append((label, f, os.path.basename(f)[6:-6]))
    jobs.sort(key=lambda j: -os.path.getsize(j[1]))
    with Pool(min(10, len(jobs))) as p:
        res = p.map(parse_one, jobs, chunksize=1)
    for r in res:
        with open(os.path.join(outdir, "%s_%s.json" % (r["label"], r["agent"])), "w") as fh:
            json.dump(r, fh)
    print("parsed %d worker transcripts, %d requests, %d items" % (len(res), sum(len(r["turns"]) for r in res), sum(len(t["in"]) for r in res for t in r["turns"])))


if __name__ == "__main__":
    main()
