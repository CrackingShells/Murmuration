# w07 combined smoke: checks one run of w07smoke_run.py by record; input: run folder name under /private/tmp/murmuration-w07/reproducer-w07-7/runs/ and the session transcripts under ~/.claude/projects; output: a table on stdout (tool calls and results, hook outcomes in the stream, guard.log decisions, debug-log error words, harness.jsonl events, hand-back files, user_words.md entries, per-subagent start note / graded notes / cache write TTLs, hook error records in the transcripts); no account identifiers are printed
import collections, glob, json, os, re, sys

B = "/private/tmp/murmuration-w07/reproducer-w07-7"
name = sys.argv[1]
R = "%s/runs/%s" % (B, name)
uses, res, hs, sid = [], {}, collections.Counter(), None
for l in open(R + "/stream.jsonl"):
    try:
        m = json.loads(l)
    except ValueError:
        continue
    sid = sid or m.get("session_id")
    if m.get("type") == "assistant":
        for b in m["message"].get("content", []):
            if b.get("type") == "tool_use":
                uses.append((b["id"], b["name"], b["input"], m.get("parent_tool_use_id")))
    elif m.get("type") == "user" and isinstance(m["message"].get("content"), list):
        for b in m["message"]["content"]:
            if b.get("type") == "tool_result":
                t = b.get("content")
                res[b["tool_use_id"]] = t if isinstance(t, str) else " ".join(x.get("text", "") for x in t or [])
    elif m.get("type") == "system" and m.get("subtype") in ("hook_started", "hook_response"):
        hs[(m["subtype"], m["hook_name"])] += 1
        if m["subtype"] == "hook_response" and (m.get("outcome") != "success" or str(m.get("exit_code")) not in ("0", "None")):
            print("hook_response not success:", m["hook_name"], m.get("outcome"), m.get("exit_code"), (m.get("stderr") or "")[:160].replace("\n", " "))
print("== tool calls (tool, main/sub, command or path, result head)")
for u, n, i, p in uses:
    d = i.get("command") or i.get("file_path") or json.dumps(i)
    print("  %-16s %-5s %-70r -> %s" % (n, "sub" if p else "main", d[:70], res.get(u, "")[:130].replace("\n", " ")))
print("== hook starts by name:", {k[1]: v for k, v in hs.items() if k[0] == "hook_started"})
g = [json.loads(x) for x in open(R + "/guard.log")] if os.path.exists(R + "/guard.log") else []
print("== guard.log lines:", len(g), "decisions:", dict(collections.Counter((x["decision"], x["group"]) for x in g)))
for x in g:
    if x["decision"] != "allow":
        print("   non-allow:", {k: (str(v)[:100]) for k, v in x.items() if k != "t"})
dbg = open(R + "/dbg.log", errors="replace").read()
hook_lines = [x for x in dbg.splitlines() if re.search(r"hook", x, re.I) and "MCP server" not in x]
print("== debug log: error words (whole log):", {w: len(re.findall(w, dbg)) for w in ("hook_non_blocking_error", "hook_cancelled", "hook_blocking_error", "non-blocking", "hook error")})
print("== debug log: hook lines (not MCP-server lines):", len(hook_lines), "; of them matching error|fail|timed out|Traceback|exit code [1-9]|status [1-9]:")
for ln in [x for x in hook_lines if re.search(r"error|fail|timed out|Traceback|exit code [1-9]|status [1-9]", x, re.I) and "additionalContext" not in x][:8]:
    print("   ", ln[:240])
print("== debug log: lines '[ERROR]' not from MCP servers:", len([x for x in dbg.splitlines() if "[ERROR]" in x and "MCP server" not in x]))
for ln in [x for x in dbg.splitlines() if "[ERROR]" in x and "MCP server" not in x][:5]:
    print("   ", ln[:240])
H = R + "/lab/__statera__/harness.jsonl"
if os.path.exists(H):
    ev = [json.loads(x) for x in open(H)]
    print("== harness.jsonl events:", [(e["event"], e.get("name"), e.get("frac"), e.get("t_frac"), e.get("mode")) for e in ev])
hb = R + "/lab/__statera__/handbacks"
print("== hand-back files:", sorted(os.listdir(hb)) if os.path.isdir(hb) else None)
if os.path.isdir(hb):
    for f in sorted(os.listdir(hb)):
        t = open(os.path.join(hb, f)).read()
        print("   %s: %d bytes, header lines: %s" % (f, len(t), [x[:110] for x in t.splitlines() if x.startswith("## ") or "bytes=" in x][:3]))
uw = R + "/lab/__statera__/user_words.md"
if os.path.exists(uw):
    t = open(uw).read()
    heads = [x for x in t.splitlines() if x.startswith("## ")]
    print("== user_words.md: %d bytes, %d dated headings:" % (len(t), len(heads)), heads)
    print("   contains 'Smoke test of the lab':", t.count("Smoke test of the lab"), "; contains 'test of a security hook':", t.count("test of a security hook"), "; contains seed question:", t.count("What is 1+1"))
# transcripts
proj = os.path.expanduser("~/.claude/projects/-" + R.replace("/", "-").replace("_", "-").lstrip("-") + "-lab")
bad = collections.Counter()
for ff in glob.glob(proj + "/**/*.jsonl", recursive=True):
    for l in open(ff, errors="replace"):
        for w in ("hook_non_blocking_error", "hook_cancelled", "hook_blocking_error"):
            if w in l:
                bad[(os.path.basename(ff)[:14], w)] += 1
print("== transcript hook error records (main + subagents):", dict(bad) or "none", "; files:", len(glob.glob(proj + "/**/*.jsonl", recursive=True)))
print("== subagent transcripts:")
for f in sorted(glob.glob(proj + "/*/subagents/agent-*.jsonl")):
    meta = json.load(open(f.replace(".jsonl", ".meta.json")))
    start, notes, w5, w1, rd, reqs, seen = [], [], 0, 0, 0, 0, set()
    for l in open(f):
        m = json.loads(l)
        if m.get("type") == "assistant":
            if m["message"].get("id") in seen:
                continue   # one request is written once per content block, with the same usage
            seen.add(m["message"].get("id"))
            u = m["message"].get("usage", {}); cc = u.get("cache_creation") or {}
            w5 += cc.get("ephemeral_5m_input_tokens", 0); w1 += cc.get("ephemeral_1h_input_tokens", 0); rd += u.get("cache_read_input_tokens", 0); reqs += 1
        elif m.get("type") == "attachment":
            a = m["attachment"]
            if a.get("type") == "hook_additional_context":
                for c in a.get("content", []):
                    if c.startswith("Budget:"):
                        start.append(c[:110])
                    elif c.startswith("Spent"):
                        notes.append((a.get("hookEvent"), c[:110]))
    print("  %-22s name=%-16s start-note=%s graded-notes=%s" % (meta.get("agentType"), meta.get("name"), start, notes))
    print("  %-22s requests=%d: 5m-write=%d 1h-write=%d cache-read=%d tokens" % ("", reqs, w5, w1, rd))
stub = B + "/stub.log"
print("== stub.log lines (whole file):", len(open(stub).read().splitlines()) if os.path.exists(stub) else 0)
