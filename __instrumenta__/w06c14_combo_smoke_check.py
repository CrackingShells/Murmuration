# w06-c14 smoke: checks (a) to (d) of one run of w06c14_combo_smoke_run.py; input: run name; output: a table on stdout (tool calls, guard starts, denials, harness.jsonl events, hook error records in stream, debug log and the session transcripts under ~/.claude/projects); no account identifiers are printed
import collections, glob, json, os, re, sys

B = "/private/tmp/murmuration-w06/reproducer-w06-8"
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
            print("hook_response not success:", m["hook_name"], m.get("outcome"), m.get("exit_code"), (m.get("stderr") or "")[:100])
print("== tool calls (tool, parent=subagent?, result head)")
for u, n, i, p in uses:
    d = i.get("command") or i.get("file_path") or json.dumps(i)
    print("  %-16s %-5s %-60r -> %s" % (n, "sub" if p else "main", d[:60], res.get(u, "")[:90].replace("\n", " ")))
print("== Bash tool calls:", sum(1 for u in uses if u[1] == "Bash"))
print("== hook starts by name:", {k[1]: v for k, v in hs.items() if k[0] == "hook_started"})
g = [json.loads(x) for x in open(R + "/guard.log")] if os.path.exists(R + "/guard.log") else []
print("== guard.log lines:", len(g), "decisions:", dict(collections.Counter((x["decision"], x["group"]) for x in g)))
dbg = open(R + "/dbg.log", errors="replace").read()
print("== debug log: guard finishes (status 0 / other):",
      len(re.findall(r"permission_guard.py.*finished with status 0", dbg)), len(re.findall(r"permission_guard.py.*finished with status [1-9]", dbg)), "; error words:",
      {w: len(re.findall(w, dbg)) for w in ("hook_non_blocking_error", "hook_cancelled", "non-blocking", "hook error", "timed out")})
H = R + "/lab/__statera__/harness.jsonl"
if os.path.exists(H):
    ev = [json.loads(x) for x in open(H)]
    print("== harness.jsonl events:", [(e["event"], e.get("name"), e.get("frac"), e.get("mode")) for e in ev])
print("== hand-back files:", sorted(os.listdir(R + "/lab/__statera__/handbacks")) if os.path.isdir(R + "/lab/__statera__/handbacks") else None)
tr = 0; bad = collections.Counter()
for f in glob.glob(os.path.expanduser("~/.claude/projects/*/%s*" % sid)) + glob.glob(os.path.expanduser("~/.claude/projects/*/%s/**/*.jsonl" % sid), recursive=True):
    fs = [f] if os.path.isfile(f) else glob.glob(f + "/**/*.jsonl", recursive=True)
    for ff in fs:
        tr += 1
        for l in open(ff, errors="replace"):
            for w in ("hook_non_blocking_error", "hook_cancelled", "hook_blocking_error"):
                if w in l:
                    bad[(os.path.basename(ff)[:12], w)] += 1
print("== transcript files:", tr, "hook error records:", dict(bad))
print("== stub.log lines:", len(open(B + "/stub.log").read().splitlines()))
