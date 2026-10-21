# w07-c3: downstream time per tool call: per pair and arm, the median time from the assistant record holding a Bash `echo` tool_use to the user record holding its tool_result (transcript timestamps; includes the guard's PreToolUse, the permission step, the command, the PostToolUse hooks); inputs: RUNS_DIR SCENARIO N; output: markdown on stdout
"""usage: w07c3_tool_gap.py RUNS_DIR SCENARIO N     Calls: Bash whose command starts with `echo ` (the scripted ones), in the main and the worker transcripts of runs RUNS_DIR/<scenario>_<i>_{A,B}.
A call with parallel siblings is included as it is. The figure is a lower bound of what a hook start saves in a call (the model's own time is outside the interval) and is noisy (the permission step is in it)."""
import datetime, glob, json, statistics as st, sys

RUNS, SC, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
ts = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000


def gaps(d):
    out = []
    for f in glob.glob(d + "/transcripts/*.jsonl"):
        use = {}
        for l in open(f):
            r = json.loads(l)
            t = r.get("timestamp")
            m = r.get("message")
            if not t or not isinstance(m, dict) or not isinstance(m.get("content"), list):
                continue
            for c in m["content"]:
                if c.get("type") == "tool_use" and c.get("name") == "Bash" and str(c["input"].get("command", "")).startswith("echo "):
                    use[c["id"]] = ts(t)
                elif c.get("type") == "tool_result" and c.get("tool_use_id") in use:
                    out.append(ts(t) - use.pop(c["tool_use_id"]))
    return out


print("| pair | A calls | A median ms | B calls | B median ms | A minus B |\n|--:|--:|--:|--:|--:|--:|")
diffs = []
for i in range(1, N + 1):
    a, b = gaps("%s/%s_%d_A" % (RUNS, SC, i)), gaps("%s/%s_%d_B" % (RUNS, SC, i))
    d = st.median(a) - st.median(b); diffs.append(d)
    print("| %d | %d | %.0f | %d | %.0f | %.0f |" % (i, len(a), st.median(a), len(b), st.median(b), d))
print("\nB lower in %d of %d pairs; median per-pair difference %.0f ms; min %.0f, max %.0f" % (sum(d > 0 for d in diffs), N, st.median(diffs), min(diffs), max(diffs)))
