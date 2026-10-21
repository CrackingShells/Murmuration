"""Buckets the duration of every Bash tool call of a session's workers (and main thread) and lists the slowest commands, from a main transcript and its subagents to a table on stdout.

usage: bash_time_buckets.py MAIN.jsonl [--top N]. Duration = tool_result timestamp minus the tool_use record's timestamp (see tool_time_split.py); buckets 0-0.5, 0.5-2, 2-10, 10-60, 60+ s with count and summed seconds; `top` prints the slowest calls with the first 100 characters of the command.
"""
import json, sys, glob, datetime as dt
def ts(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 8
main = sys.argv[1]
files = [("main", main)] + [("worker", f) for f in sorted(glob.glob(main[:-6] + "/subagents/**/agent-*.jsonl", recursive=True))]
calls = []
for cls, f in files:
    uses, res = {}, {}
    for line in open(f, encoding="utf-8", errors="replace"):
        if '"tool_use"' not in line and '"tool_result"' not in line: continue
        try: r = json.loads(line)
        except ValueError: continue
        t = r.get("timestamp"); m = r.get("message")
        if not t or not isinstance(m, dict) or not isinstance(m.get("content"), list): continue
        for b in m["content"]:
            if not isinstance(b, dict): continue
            if b.get("type") == "tool_use" and b.get("name") == "Bash" and r.get("type") == "assistant":
                uses.setdefault(b["id"], (ts(t), (b.get("input") or {}).get("command", "")))
            elif b.get("type") == "tool_result": res.setdefault(b.get("tool_use_id"), ts(t))
    calls += [(cls, res[i] - uses[i][0], uses[i][1]) for i in uses if i in res]
edges = [0, .5, 2, 10, 60, 1e9]
print("class  bucket_s        n   sum_s  share")
for cls in ("main", "worker"):
    cs = [c for c in calls if c[0] == cls]; tot = sum(c[1] for c in cs) or 1
    for a, b in zip(edges, edges[1:]):
        sel = [c for c in cs if a <= c[1] < b]
        print("%-6s %-10s %6d %7d  %4.0f%%" % (cls, "%g-%s" % (a, "inf" if b > 1e8 else "%g" % b), len(sel), sum(c[1] for c in sel), 100 * sum(c[1] for c in sel) / tot))
print("\nslowest:")
for cls, d, cmd in sorted(calls, key=lambda c: -c[1])[:top]: print("%7.0f s %-6s %s" % (d, cls, " ".join(cmd.split())[:100]))
print("\nfastest-bucket sample (0-0.5 s) vs 0.5-2 s commands:")
import random; random.seed(1)
for lo, hi in ((0, .5), (.5, 2)):
    s = [c for c in calls if lo <= c[1] < hi]; random.shuffle(s)
    for cls, d, cmd in s[:5]: print("%5.2f s  %s" % (d, " ".join(cmd.split())[:90]))
