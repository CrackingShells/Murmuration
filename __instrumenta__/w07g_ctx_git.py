# Splits the tool phase of single-call classifier-decided Bash turns in worker transcripts by what the record's serverClassifierContext.git_state holds (root set or null, status, error) and by trivial command; inputs: main transcript .jsonl paths (workers read from <path minus .jsonl>/subagents); output: markdown table on stdout (read only).
# usage: w07g_ctx_git.py MAIN.jsonl [MAIN.jsonl ...]
import json, sys, glob, re, statistics as st, datetime
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
TRIV = re.compile(r"^\s*(ls|cat|head|tail|wc|pwd|git (status|log|diff|show|rev-parse)|sed -n|echo|date|stat|file)\b[^|;&><`$]{0,160}$")
rows = []
for m in sys.argv[1:]:
    for f in glob.glob(m[:-6] + "/subagents/agent-*.jsonl"):
        calls, n_by_msg = {}, {}
        recs = [json.loads(l) for l in open(f) if '"api-request' not in l[:40]]
        for r in recs:
            if r.get("type") == "assistant":
                bl = [b for b in r["message"].get("content", []) if b.get("type") == "tool_use"]
                for b in bl:
                    calls[b["id"]] = (ts(r["timestamp"]), b["name"], b["input"].get("command", "") if b["name"] == "Bash" else "", len(bl))
        for r in recs:
            if r.get("type") == "user" and "serverClassifierContext" in r and isinstance(r.get("message", {}).get("content"), list):
                for b in r["message"]["content"]:
                    t = calls.get(b.get("tool_use_id"))
                    if b.get("type") == "tool_result" and t and t[1] == "Bash" and t[3] == 1:
                        g = r["serverClassifierContext"]["context"]["git_state"]
                        rows.append((ts(r["timestamp"]) - t[0], g.get("root") is not None, g.get("status") is not None, g.get("error"), bool(TRIV.match(t[2]))))
print("| subset | n | median s | p10 | p90 |\n|:--|--:|--:|--:|--:|")
def line(name, xs):
    xs = sorted(xs)
    if xs: print("| %s | %d | %.2f | %.2f | %.2f |" % (name, len(xs), st.median(xs), xs[int(.1 * (len(xs) - 1))], xs[int(.9 * (len(xs) - 1))]))
for tr in (True, False):
    for root in (True, False):
        line("trivial=%s git root set=%s" % (tr, root), [r[0] for r in rows if r[4] == tr and r[1] == root])
for err in sorted({str(r[3]) for r in rows}):
    line("trivial, git_state.error=%s" % err, [r[0] for r in rows if r[4] and str(r[3]) == err])
line("trivial, status present", [r[0] for r in rows if r[4] and r[2]])
