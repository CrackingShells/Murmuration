# Attributes the USD of a PI main-thread transcript (.jsonl) to what put each token in its context: reads one transcript, writes <out>/<label>_requests.tsv (one row per request: spend split read / fresh write / rewrite / output, gap before it) and <out>/<label>_items.tsv (one row per context item: source category, tokens, USD carried), no transcript text.
# usage: python3 -I w08d_pi_context.py <outdir> <label>=<transcript.jsonl> [...]
# Model (ESTIMATE): context of request k = input + cache_read + cache_write tokens; tokens [0, cache_read) are read, the rest written/input. Items sit in chronological order; item tokens = chars x r (r fitted per session, least squares through the origin on the step growth), a step's residual is its own item, scaled down if items overshoot.
import json, sys, os, re, datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L

SKIP = ('{"type": "api-request-blob"', '{"type": "api-request-shape"', '{"type":"api-request-blob"', '{"type":"api-request-shape"')


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


def scrub(s, n=70):
    s = re.sub(r"[A-Za-z0-9_\-+/=]{32,}", "<id>", (s or "").replace("\n", " "))
    return s[:n]


def cat_read(path):
    p = path or ""
    ext = os.path.splitext(p)[1].lower()
    if "/__statera__/" in p or p.startswith("__statera__"):
        sub = "statera (notes, synthesis)"
    elif "/__reports__/" in p or "__reports__" in p:
        sub = "reports"
    elif "/__pondus__/" in p or "__pondus__" in p:
        sub = "pondus (claims)"
    elif "/__scrupuli__/" in p or "__scrupuli__" in p:
        sub = "scrupuli (puzzles)"
    elif "/__design__/" in p or "__design__" in p:
        sub = "design (framing)"
    elif "/skills/" in p or "SKILL" in p or "/references/" in p or "/templates/" in p:
        sub = "skill/reference"
    elif ext in (".md", ".txt", ".rst"):
        sub = "other doc"
    elif ext in (".py", ".sh", ".json", ".jsonl", ".toml", ".tsv", ".csv", ".yaml", ".yml"):
        sub = "code/data"
    else:
        sub = "other"
    return "Read: " + sub


def cat_bash(cmd):
    c = (cmd or "").strip()
    c1 = re.sub(r"^(cd\s+\S+\s*&&\s*)+", "", c)
    if "lab_status" in c1:
        return "Bash: lab_status.py"
    w = re.split(r"\s+", c1.split("|")[0].strip())
    w0 = w[0] if w else ""
    if w0 == "git" or re.search(r"(^|&&|;)\s*git\s", c1):
        return "Bash: git" + (" (write)" if re.search(r"git\s+(add|commit|merge|push|worktree|checkout|branch\s+-)", c1) else "")
    if w0 in ("cat", "sed", "head", "tail", "nl", "awk", "less") :
        return "Bash: file view (cat/sed/head/tail)"
    if w0 in ("grep", "rg", "ls", "find", "wc", "tree", "jq", "stat", "file") or "grep" in c1.split("|")[0]:
        return "Bash: grep/ls/find/jq"
    if w0 in ("python3", "python", "uv", "node"):
        return "Bash: python/script"
    if w0 == "gh":
        return "Bash: gh"
    if w0 in ("mkdir", "cp", "mv", "rm", "touch", "chmod", "cat>") or re.match(r"cat\s*>", c1) or "<<" in c1:
        return "Bash: write/heredoc/fs"
    return "Bash: other"


def cat_result(name, inp):
    if name == "Read":
        return cat_read(inp.get("file_path", ""))
    if name == "Bash":
        return cat_bash(inp.get("command", ""))
    if name in ("Write", "Edit", "NotebookEdit"):
        return "Write/Edit echo"
    if name in ("Agent", "Task", "SendMessage", "TaskOutput", "TaskStop"):
        return "Agent/SendMessage tool result"
    if name == "ToolSearch":
        return "ToolSearch schemas"
    if name in ("Glob", "Grep") or (name or "").startswith("mcp__plugin_colgrep"):
        return "search (Glob/Grep/colgrep)"
    if (name or "").startswith("mcp__"):
        return "other MCP tool result"
    if name in ("WebFetch", "WebSearch"):
        return "web"
    if name in ("Monitor", "TaskCreate", "TaskUpdate"):
        return "Monitor/Task result"
    return "other tool result: %s" % name


def parse(path):
    msgs, order = {}, []
    reqts = {}
    events = []          # ("A", mid) | ("I", item dict) in file order
    toolinfo = {}        # tool_use id -> (name, input)
    cur = None
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
                reqts[r["id"]] = ts(r["timestamp"])
            elif t == "assistant" and isinstance(r.get("message"), dict):
                m = r["message"]
                if m.get("model") == "<synthetic>":
                    continue
                mid = m.get("id")
                tt = ts(r["timestamp"])
                e = msgs.get(mid)
                if e is None:
                    e = msgs[mid] = {"ref": r.get("requestRef"), "first": tt, "last": tt, "usage": {}, "model": m.get("model"),
                                     "text": 0, "think": 0, "write": 0, "dispatch": 0, "calls": 0, "blocks": []}
                    order.append(mid)
                    events.append(("A", mid))
                e["last"] = max(e["last"], tt)
                L.merge_usage(e["usage"], m.get("usage") or {})
                for b in m.get("content") or []:
                    bt = b.get("type")
                    if bt == "text":
                        e["text"] += len(b.get("text") or "")
                    elif bt == "thinking":
                        e["think"] += len(b.get("thinking") or "")
                    elif bt == "tool_use":
                        inp = b.get("input") or {}
                        n = len(json.dumps(inp)) + len(b.get("name", ""))
                        toolinfo[b["id"]] = (b["name"], inp)
                        e["calls"] += 1
                        e.setdefault("tn", []).append(b["name"])
                        if b["name"] in ("Write", "Edit", "NotebookEdit"):
                            e["write"] += n
                        elif b["name"] in ("Agent", "Task", "SendMessage"):
                            e["dispatch"] += n
                        else:
                            e["text"] += n   # other tool calls: counted with own visible output, split later
                            e.setdefault("callchars", 0)
                            e["callchars"] += n
            elif t == "user":
                m = r.get("message") or {}
                c = m.get("content")
                tt = ts(r["timestamp"])
                origin = r.get("origin") or {}
                kind = origin.get("kind") if isinstance(origin, dict) else None
                if isinstance(c, str):
                    events.append(("I", classify_text(c, kind, r.get("isMeta"), tt)))
                elif isinstance(c, list):
                    for b in c:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "tool_result":
                            txt = text_of(b.get("content"))
                            nm, inp = toolinfo.get(b.get("tool_use_id"), ("?", {}))
                            lab = (inp.get("file_path") or inp.get("path") or "") if nm != "Bash" else scrub(inp.get("command", ""), 80)
                            if nm in ("Bash", "Agent", "SendMessage") or nm.startswith("mcp__"):
                                lab = ""   # no command or brief text in the derived tables: only file paths are kept
                            events.append(("I", {"cat": cat_result(nm, inp), "tool": nm, "label": scrub(lab, 90), "chars": len(txt), "ts": tt,
                                                 "err": bool(b.get("is_error"))}))
                        elif b.get("type") == "text":
                            events.append(("I", classify_text(b.get("text", ""), kind, r.get("isMeta"), tt)))
            elif t == "attachment":
                a = r.get("attachment") or {}
                at = a.get("type")
                tt = ts(r["timestamp"])
                if at == "queued_command":
                    p = a.get("prompt")
                    p = p if isinstance(p, str) else json.dumps(p)
                    events.append(("I", {"cat": "task notification (worker done)" if "<task-notification" in p else "queued prompt", "tool": "queued", "label": at, "chars": len(p), "ts": tt, "uuid": a.get("source_uuid")}))
                elif at in ("total_tokens_reminder", "silent_turn_reminder"):
                    events.append(("I", {"cat": "injected: " + at, "tool": "attachment", "label": at, "chars": len(a.get("text", "")), "ts": tt}))
                elif at in ("skill_listing", "instructions", "hook_additional_context", "hook_success", "deferred_tools_delta", "mcp_instructions_delta",
                            "agent_listing_delta", "environment", "session_context", "edited_text_file", "model", "date", "skill_mention", "auto_mode", "command_permissions", "remote_session_change"):
                    body = a.get("content") if at in ("skill_listing", "hook_additional_context") else a
                    n = len(body) if isinstance(body, str) else len(json.dumps(body))
                    if at == "skill_listing":
                        n = len(a.get("content") or "")
                    if at == "hook_success":
                        n = len(a.get("content") or "") + len(a.get("stdout") or "")
                    events.append(("I", {"cat": "injected: " + at, "tool": "attachment", "label": at, "chars": n, "ts": tt}))
    return msgs, order, reqts, events


def classify_text(s, kind, meta, tt):
    n = len(s)
    if "<task-notification" in s[:200]:
        return {"cat": "task notification (worker done)", "tool": "user", "label": "task-notification", "chars": n, "ts": tt}
    if kind == "peer" or s.startswith("Another Claude session sent a message"):
        return {"cat": "worker hand-back / message (peer)", "tool": "user", "label": "peer", "chars": n, "ts": tt}
    if s.lstrip().startswith("<system-reminder>") and ("finished a turn" in s[:600] or "started your proposal" in s[:600] or "as session local_" in s[:600]):
        return {"cat": "child-session note (system reminder: a session the PI started finished a turn)", "tool": "user", "label": "child-session", "chars": n, "ts": tt}
    if s.lstrip().startswith("<system-reminder>"):
        return {"cat": "injected: system reminder (user turn)", "tool": "user", "label": "system-reminder", "chars": n, "ts": tt}
    if meta and ("Base directory for this skill" in s[:200]):
        return {"cat": "injected: skill text (invoked skill)", "tool": "user", "label": "skill", "chars": n, "ts": tt}
    if meta:
        return {"cat": "injected: other meta text", "tool": "user", "label": "meta", "chars": n, "ts": tt}
    if "[Request interrupted" in s[:40]:
        return {"cat": "user message", "tool": "user", "label": "interrupt", "chars": n, "ts": tt}
    return {"cat": "user message", "tool": "user", "label": "human", "chars": n, "ts": tt}


def analyse(label, path, outdir):
    msgs, order, reqts, events = parse(path)
    K = len(order)
    # requests
    R = []
    for k, mid in enumerate(order):
        m = msgs[mid]
        u = m["usage"]
        cc = u.get("cache_creation") or {}
        cw1, cw5 = int(cc.get("ephemeral_1h_input_tokens") or 0), int(cc.get("ephemeral_5m_input_tokens") or 0)
        cw5 += max(0, int(u.get("cache_creation_input_tokens") or 0) - cw1 - cw5)
        cr = int(u.get("cache_read_input_tokens") or 0)
        inp = int(u.get("input_tokens") or 0)
        out = int(u.get("output_tokens") or 0)
        start = reqts.get(m["ref"], m["first"])
        R.append({"k": k, "model": m["model"], "cr": cr, "cw1": cw1, "cw5": cw5, "inp": inp, "out": out, "ctx": cr + cw1 + cw5 + inp,
                  "start": start, "end": m["last"], "p": L.PRICES.get(re.sub(r"-\d{8}$", "", m["model"] or ""))})
    # steps: items before request 0 -> base; after request k-1 and before k -> step k
    steps = [[] for _ in range(K + 1)]
    ai = -1
    seen_uuid = set()
    for kind, x in events:
        if kind == "A":
            ai += 1
            continue
        # an item after assistant ai (0-based) enters the step before request ai+1; before any assistant: step 0
        steps[ai + 1].append(x)
    # own assistant content as items placed at the front of the step that follows it
    items = []   # chronological list with 'step' = request index at which it first is in context
    for k in range(K):
        pass
    fit_pairs = []
    stepitems = {}
    for k in range(K + 1):
        its = []
        if k >= 1:
            m = msgs[order[k - 1]]
            callc = m.get("callchars", 0)
            vis_text = m["text"] - callc
            if vis_text > 0:
                its.append({"cat": "own output: text", "tool": "assistant", "label": "text", "chars": vis_text})
            if callc > 0:
                its.append({"cat": "own output: tool calls (Bash/Read/...)", "tool": "assistant", "label": "tool_use", "chars": callc})
            if m["write"] > 0:
                its.append({"cat": "own output: Write/Edit content", "tool": "assistant", "label": "write/edit input", "chars": m["write"]})
            if m["dispatch"] > 0:
                its.append({"cat": "own output: dispatch briefs/messages (Agent/SendMessage)", "tool": "assistant", "label": "agent/send input", "chars": m["dispatch"]})
            if m["think"] > 0:
                its.append({"cat": "own output: thinking (recorded)", "tool": "assistant", "label": "thinking", "chars": m["think"]})
        its += steps[k]
        stepitems[k] = its
    # fit r on steps >= 1 (growth)
    sw = sd = sww = 0.0
    prev = None
    deltas = {}
    for k in range(K):
        d = R[k]["ctx"] - (R[k - 1]["ctx"] if k else 0)
        deltas[k] = d
    for k in range(1, K):
        w = sum(i["chars"] for i in stepitems[k])
        d = deltas[k]
        if d > 0 and w > 0 and d < 0.5 * R[k - 1]["ctx"] + 200000:
            sd += d * w
            sww += w * w
    r = sd / sww if sww else 0.4
    # step k items enter before request k (k>=1); step K (after last assistant) never reaches a request
    # base: step 0 items + remainder of ctx_0
    allitems = []
    resets = []
    base_chars = sum(i["chars"] for i in stepitems[0])
    for k in range(K):
        its = stepitems[k]
        d = deltas[k]
        if k >= 1 and d < -0.2 * R[k - 1]["ctx"]:
            resets.append(k)
        if k == 0:
            est = sum(i["chars"] for i in its) * r
            for i in its:
                i["tokens"] = i["chars"] * r
            rem = d - est
            its = its + [{"cat": "system prompt + tool defs + CLAUDE.md (not in transcript)", "tool": "prefix", "label": "residual of request 0", "chars": 0, "tokens": max(rem, 0)}]
            if rem < 0:
                f = d / est if est else 1
                for i in its:
                    i["tokens"] *= f
        else:
            d_eff = max(d, 0)
            est = sum(i["chars"] for i in its) * r
            for i in its:
                i["tokens"] = i["chars"] * r
            if est > d_eff:
                f = d_eff / est if est else 0
                for i in its:
                    i["tokens"] *= f
                rem = 0
            else:
                rem = d_eff - est
            if rem > 0:
                its = its + [{"cat": "unattributed step residual (thinking, framing, reminders)", "tool": "residual", "label": "residual", "chars": 0, "tokens": rem}]
            if k in resets:
                its = its + [{"cat": "COMPACTION: context after reset", "tool": "reset", "label": "reset", "chars": 0, "tokens": R[k]["ctx"] - sum(i["tokens"] for i in its)}]
        for i in its:
            i["step"] = k
            i["ts"] = i.get("ts") or R[k]["start"]
            i["usd_read"] = i["usd_write_fresh"] = i["usd_rewrite"] = 0.0
            i["n_reads"] = 0
        allitems += its
    # positions (chronological = list order); on a reset the earlier items are dropped from context: mark
    live_from = 0
    pos = []
    cum = 0.0
    for i in allitems:
        pos.append(cum)
        cum += i["tokens"]
    # per request cost loop
    reqrows = []
    # index of items by entry step
    first_idx_of_step = {}
    for idx, i in enumerate(allitems):
        first_idx_of_step.setdefault(i["step"], idx)
    for k in range(K):
        q = R[k]
        p = q["p"]
        if p is None:
            continue
        ib = first_idx_of_step.get(k, len(allitems))
        # items in context at request k: all items with step <= k (after last reset <= k)
        lastreset = max([x for x in resets if x <= k], default=0)
        lo = first_idx_of_step.get(lastreset, 0) if lastreset else 0
        hi = len([i for i in allitems if i["step"] <= k]) if False else None
        # find hi quickly
        hi = ib
        while hi < len(allitems) and allitems[hi]["step"] == k:
            hi += 1
        # dropped-item offset: positions measured from pos[lo]
        off = pos[lo] if lo < len(pos) else 0
        wr = (q["cw5"] * p[3] + q["cw1"] * p[4] + q["inp"] * p[0]) / max(1, q["cw5"] + q["cw1"] + q["inp"])   # blended price of non-read tokens
        crp = p[2]
        prev_ctx = R[k - 1]["ctx"] if (k and k not in resets) else 0
        rewrite_tok = 0.0
        fresh_tok = 0.0
        read_tok = 0.0
        for idx in range(lo, hi):
            i = allitems[idx]
            a = pos[idx] - off
            b = a + i["tokens"]
            rd = max(0.0, min(b, q["cr"]) - a)
            nr = i["tokens"] - rd
            # of the non-read part, tokens at positions < prev_ctx are rewrites
            rw = max(0.0, min(b, prev_ctx) - max(a, q["cr"]))
            fr = nr - rw
            i["usd_read"] += rd * crp / 1e6
            i["usd_rewrite"] += rw * wr / 1e6
            i["usd_write_fresh"] += fr * wr / 1e6
            if rd > 0:
                i["n_reads"] += 1
            rewrite_tok += rw; fresh_tok += fr; read_tok += rd
        # request-level
        usd_out = q["out"] * p[1] / 1e6
        gap = None
        reqrows.append({"k": k, "start": q["start"], "end": q["end"], "model": q["model"], "ctx": q["ctx"], "cr": q["cr"], "cw5": q["cw5"], "cw1": q["cw1"], "inp": q["inp"], "out": q["out"],
                        "usd_read": q["cr"] * crp / 1e6, "usd_cw5": q["cw5"] * p[3] / 1e6, "usd_cw1": q["cw1"] * p[4] / 1e6, "usd_inp": q["inp"] * p[0] / 1e6, "usd_out": usd_out,
                        "rewrite_tok": rewrite_tok, "rewrite_usd": rewrite_tok * wr / 1e6, "rewrite_premium_usd": rewrite_tok * (wr - crp) / 1e6,
                        "reset": int(k in resets), "tools": ",".join(sorted(set(msgs[order[k]].get("tn", [])))) + "|" + str(sum(1 for x in msgs[order[k]].get("tn", []) if x in ("Agent", "Task"))) + "|" + str(sum(1 for x in msgs[order[k]].get("tn", []) if x == "SendMessage"))})
    # gaps and what ended them
    for k, row in enumerate(reqrows):
        if k == 0:
            row["gap_s"] = ""; row["gap_cause"] = ""
            continue
        g = row["start"] - reqrows[k - 1]["end"]
        row["gap_s"] = round(g, 1)
        its = [i for i in stepitems[k] if i.get("tool") != "assistant"]
        causes = [i["cat"] for i in its]
        c = "tool result"
        if any(x.startswith("user message") for x in causes):
            c = "user message"
        elif any(x.startswith("worker hand-back") for x in causes) or any(x.startswith("task notification") for x in causes):
            c = "worker message/notification"
        elif any(x.startswith("child-session") for x in causes):
            c = "child-session note (reminder)"
        elif any(x.startswith("injected: system reminder") for x in causes):
            c = "system reminder only (linked sessions / other)"
        row["gap_cause"] = c
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "%s_requests.tsv" % label), "w") as fh:
        cols = ["k", "start", "end", "model", "ctx", "cr", "cw5", "cw1", "inp", "out", "usd_read", "usd_cw5", "usd_cw1", "usd_inp", "usd_out", "rewrite_tok", "rewrite_usd", "rewrite_premium_usd", "reset", "gap_s", "gap_cause", "tools"]
        fh.write("\t".join(cols) + "\n")
        for row in reqrows:
            fh.write("\t".join(str(round(row[c], 6)) if isinstance(row[c], float) else str(row[c]) for c in cols) + "\n")
    with open(os.path.join(outdir, "%s_items.tsv" % label), "w") as fh:
        cols = ["step", "cat", "tool", "label", "chars", "tokens", "n_reads", "usd_write_fresh", "usd_read", "usd_rewrite"]
        fh.write("\t".join(cols) + "\n")
        for i in allitems:
            fh.write("\t".join(str(round(i[c], 6)) if isinstance(i[c], float) else str(i[c]).replace("\t", " ") for c in cols) + "\n")
    tot = sum(x["usd_read"] + x["usd_cw5"] + x["usd_cw1"] + x["usd_inp"] + x["usd_out"] for x in reqrows)
    items_usd = sum(i["usd_read"] + i["usd_write_fresh"] + i["usd_rewrite"] for i in allitems)
    req_noout = sum(x["usd_read"] + x["usd_cw5"] + x["usd_cw1"] + x["usd_inp"] for x in reqrows)
    print("%s: %d requests, %d items, r=%.3f tokens/char, total USD %.2f (requests, from usage), items sum %.2f vs request non-output %.2f, resets %s" % (label, K, len(allitems), r, tot, items_usd, req_noout, resets))
    return reqrows


def main():
    outdir = sys.argv[1]
    for spec in sys.argv[2:]:
        label, path = spec.split("=", 1)
        analyse(label, path, outdir)


if __name__ == "__main__":
    main()
