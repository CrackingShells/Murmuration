"""Splits a session's wall time into tool time (tool_use record to its tool_result record) and the rest, per tool name and per thread class, from a main transcript and its subagents.

usage: tool_time_split.py MAIN.jsonl [--only SUBSTR_IN_META] ; prints JSON: per class (main/workers) span_s, tool_s, n_calls, per tool {n, sum_s, median_s, p90_s}.
Rules: a tool call's duration = timestamp of the user record holding its tool_result minus the timestamp of the assistant record holding its tool_use (parallel calls overlap, so the sum
can exceed the span; the `union_s` field merges overlaps). The hook time of PostToolUse is inside this duration when the platform runs it before returning the result [assumption: not verified].
"""
import json, sys, os, glob, collections, datetime as dt, statistics as st
def ts(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
def scan(path):
    uses, res, first, last = {}, {}, None, None
    for line in open(path, encoding="utf-8", errors="replace"):
        if '"tool_use"' not in line and '"tool_result"' not in line and '"timestamp"' not in line: continue
        try: r = json.loads(line)
        except ValueError: continue
        t = r.get("timestamp")
        if not t: continue
        t = ts(t); first = t if first is None else first; last = t
        m = r.get("message")
        if not isinstance(m, dict) or not isinstance(m.get("content"), list): continue
        for b in m["content"]:
            if not isinstance(b, dict): continue
            if b.get("type") == "tool_use" and r.get("type") == "assistant": uses.setdefault(b["id"], (t, b.get("name")))
            elif b.get("type") == "tool_result": res.setdefault(b.get("tool_use_id"), t)
    calls = [(uses[i][1], res[i] - uses[i][0], uses[i][0], res[i]) for i in uses if i in res]
    return calls, (first, last)
def union(iv):
    iv = sorted(iv); tot = 0; cur = None
    for a, b in iv:
        if cur is None: cur = [a, b]
        elif a <= cur[1]: cur[1] = max(cur[1], b)
        else: tot += cur[1] - cur[0]; cur = [a, b]
    return tot + (cur[1] - cur[0] if cur else 0)
main = sys.argv[1]; only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
paths = {"main": [main], "workers": []}
for f in sorted(glob.glob(main[:-6] + "/subagents/**/agent-*.jsonl", recursive=True)):
    if only:
        try: meta = open(f[:-6] + ".meta.json").read()
        except OSError: meta = ""
        if only not in meta: continue
    paths["workers"].append(f)
out = {}
for cls, fs in paths.items():
    span = tool = uni = 0.0; bytool = collections.defaultdict(list); n = 0
    for f in fs:
        calls, (a, b) = scan(f)
        if a is None: continue
        span += b - a; n += len(calls); uni += union([(c[2], c[3]) for c in calls])
        for name, d, _, _ in calls: bytool[name].append(d); tool += d
    out[cls] = {"files": len(fs), "span_s": round(span), "tool_union_s": round(uni), "tool_sum_s": round(tool), "n_calls": n,
                "tools": {k: {"n": len(v), "sum_s": round(sum(v)), "median_s": round(st.median(v), 2), "p90_s": round(sorted(v)[int(.9 * (len(v) - 1))], 1)}
                          for k, v in sorted(bytool.items(), key=lambda kv: -sum(kv[1]))[:12]}}
print(json.dumps(out, indent=1))
