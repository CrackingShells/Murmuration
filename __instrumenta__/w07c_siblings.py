"""Tabulates sibling-hook behaviour from w07-c sib*/exec* run directories: per event and per tool call, how far apart the siblings' own start times are (hooks.log t0, taken inside the script), the platform's own duration per hook (debug log 'finished with status 0 (N ms)'), the span from the first sibling's start to the last sibling's end on the sleeper calls (sleep 0.5 s each: parallel ~0.5 s, serial ~N*0.5 s), and tool_use to tool_result time in the transcript; input: run directories; output: markdown table on stdout.
"""
import json, sys, os, re, statistics as st, collections
def med(x): return round(st.median(x), 1) if x else None
print("| run | N siblings | event | start spread (last-first t0) ms, median over calls | consecutive start gap ms, median | platform duration per hook ms, median / p90 | sleeper calls: first start to last end ms (sleep 500 each) | tool_use to tool_result ms, median |\n|:--|--:|:--|--:|--:|:--|--:|--:|")
for d in sys.argv[1:]:
    name = os.path.basename(d); n = int(re.sub(r"\D", "", name))
    log = [json.loads(l) for l in open(os.path.join(d, "hooks.log"))]
    g = collections.defaultdict(list)
    for r in log: g[(r["event"], r["tool_use_id"])].append(r)
    dur = collections.defaultdict(list)
    for l in open(os.path.join(d, "dbg.log")):
        m = re.search(r"Hooks: (PreToolUse|PostToolUse):Bash \[.*hook\.py.*?(sib\w*)?.*\] \(plugin w7c@inline\) finished with status 0 \((\d+)ms\)", l)
        if m: dur[m.group(1)].append(int(m.group(3)))
    # transcript: tool_use -> tool_result
    gap = []; tu = {}
    for l in open(os.path.join(d, "transcript.jsonl")):
        r = json.loads(l); ts = r.get("timestamp")
        if not ts or r.get("type") not in ("assistant", "user"): continue
        from datetime import datetime
        t = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1000
        m = r["message"]["content"]
        if isinstance(m, list):
            for c in m:
                if c.get("type") == "tool_use": tu[c["id"]] = t
                if c.get("type") == "tool_result" and c.get("tool_use_id") in tu: gap.append(t - tu[c["tool_use_id"]])
    for ev in ("PreToolUse", "PostToolUse"):
        calls = [v for (e, i), v in g.items() if e == ev and len(v) == n]
        spread = [(max(x["t0_ns"] for x in v) - min(x["t0_ns"] for x in v)) / 1e6 for v in calls]
        gaps = []
        for v in calls:
            t0s = sorted(x["t0_ns"] for x in v); gaps += [(b - a) / 1e6 for a, b in zip(t0s, t0s[1:])]
        sl = [(max(x["t1_ns"] for x in v) - min(x["t0_ns"] for x in v)) / 1e6 for v in calls if any(x["acted"] for x in v)] if ev == "PreToolUse" else []
        dd = sorted(dur[ev])
        print("| %s | %d | %s | %s | %s | %s / %s | %s | %s |" % (name, n, ev, med(spread), med(gaps), med(dd), dd[int(.9 * (len(dd) - 1))] if dd else None, med(sl) if sl else "n/a", med(gap)))
