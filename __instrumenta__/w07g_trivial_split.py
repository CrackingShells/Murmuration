# Splits the tool phase of single-call classifier-decided Bash turns of worker transcripts (result under 3000 chars) by command shape (bare read-only command, pipe/chain of read-only words, `cd dir &&` prefix, git, grep/sed/awk, other) to test what w07b's "trivial" 1.49 s contains; inputs: main transcript .jsonl paths (workers read from <path minus .jsonl>/subagents), read only; output: markdown table on stdout.
# usage: w07g_trivial_split.py LABEL=MAIN.jsonl [LABEL=MAIN.jsonl ...]
import json, sys, glob, re, statistics as st, datetime
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
BARE = {"ls", "cat", "head", "tail", "wc", "pwd", "echo", "date", "stat", "file", "test"}
RO = BARE | {"sed", "grep", "awk", "sort", "uniq", "cut", "tr", "nl", "jq", "basename", "dirname", "find", "tree", "du"}
def shape(cmd):
    c = cmd.strip()
    first = c.split()[0] if c.split() else ""
    if "python" in c or "uv run" in c or "cargo" in c or "sleep" in c or "claude" in c or "timeout" in c or "<<" in c:
        return "runs a program (python/uv/cargo/sleep/claude/heredoc)"
    if first == "cd":
        return "cd dir && ..."
    if first == "git":
        return "git ..."
    if first in BARE and not re.search(r"[|;&><`$(]", c):
        return "bare ls/cat/head/tail/wc/pwd/echo/date/stat/file/test"
    segs = [s.strip().split()[0] for s in re.split(r"\|\||&&|;|\|", c) if s.strip()]
    if all(s in RO for s in segs):
        return "pipe/chain of read-only words" if len(segs) > 1 else "single grep/sed/awk/find..."
    return "other"
rows = []
for a in sys.argv[1:]:
    lab, m = a.split("=")
    for f in glob.glob(m[:-6] + "/subagents/agent-*.jsonl"):
        calls = {}
        recs = [json.loads(l) for l in open(f) if '"api-request' not in l[:40]]
        for r in recs:
            if r.get("type") == "assistant":
                bl = [b for b in r["message"].get("content", []) if b.get("type") == "tool_use"]
                for b in bl:
                    calls[b["id"]] = (ts(r["timestamp"]), b["name"], b["input"].get("command", "") if b["name"] == "Bash" else "", len(bl))
        for r in recs:
            if r.get("type") == "user" and "serverClassifierContext" in r and isinstance(r.get("message", {}).get("content"), list):
                pd = r.get("permissionDecision") or {}
                for b in r["message"]["content"]:
                    t = calls.get(b.get("tool_use_id"))
                    if b.get("type") == "tool_result" and t and t[1] == "Bash" and t[3] == 1 and len(json.dumps(b.get("content"))) < 3000:
                        rows.append((lab, ts(r["timestamp"]) - t[0], shape(t[2]), pd.get("reasonType")))
print("| shape | n | median s | p10 | p90 |\n|:--|--:|--:|--:|--:|")
for s in sorted({r[2] for r in rows}):
    xs = sorted(r[1] for r in rows if r[2] == s)
    print("| %s | %d | %.2f | %.2f | %.2f |" % (s, len(xs), st.median(xs), xs[int(.1 * (len(xs) - 1))], xs[int(.9 * (len(xs) - 1))]))
xs = sorted(r[1] for r in rows)
print("| all | %d | %.2f | %.2f | %.2f |" % (len(xs), st.median(xs), xs[int(.1 * (len(xs) - 1))], xs[int(.9 * (len(xs) - 1))]))
print("\nby wave, bare commands only:")
for l in sorted({r[0] for r in rows}):
    xs = sorted(r[1] for r in rows if r[0] == l and r[2].startswith("bare"))
    if xs: print("- %s: n=%d median %.2f s p10 %.2f p90 %.2f" % (l, len(xs), st.median(xs), xs[int(.1 * (len(xs) - 1))], xs[int(.9 * (len(xs) - 1))]))
