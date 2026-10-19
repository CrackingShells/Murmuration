"""Own derivation: Write tool calls in subagent transcripts and whether the tool_result was the platform's refusal."""
import json, glob, os, re, sys
R = re.compile(r"^(REPORT|SUMMARY|FINDINGS|ANALYSIS).*\.md$", re.I)
sub = sys.argv[1]
rows = []
for f in sorted(glob.glob(sub + "/agent-*.jsonl")):
    meta = json.load(open(f[:-6] + ".meta.json")); calls = {}
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        c = (d.get("message") or {}).get("content")
        if not isinstance(c, list): continue
        for b in c:
            if b.get("type") == "tool_use" and b.get("name") == "Write": calls[b["id"]] = os.path.basename(b["input"].get("file_path", ""))
            if b.get("type") == "tool_result" and b.get("tool_use_id") in calls:
                t = b.get("content"); t = json.dumps(t) if not isinstance(t, str) else t
                refused = "Subagents should return findings" in t
                rows.append((meta.get("name"), calls[b["tool_use_id"]], refused, bool(R.match(calls[b["tool_use_id"]])), bool(b.get("is_error"))))
n = len(rows)
print("writes", n, "refused", sum(r[2] for r in rows), "regex-match", sum(r[3] for r in rows), "mismatch", [r for r in rows if r[2] != r[3]])
for r in rows:
    if r[2] or r[3]: print(r)
other_errors = [r for r in rows if r[4] and not r[2]]
print("other is_error writes", other_errors)
