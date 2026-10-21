# w06-c9: derives metric e2 (platform-recorded hook time of budget.py / handback.py starts, worker against main thread) from the debug logs of paired headless runs of w06c9_run.py; inputs: pairs "main_run:new_run" (run names under /private/tmp/murmuration-w06/author-w06-6/runs); output: markdown tables on stdout
"""The platform's own figure is the `Hooks: <Event[:tool]> [<command>] ... finished with status N (X ms)` line of the debug file (a command hook that prints nothing leaves no transcript record, so no `durationMs` attachment).
A start belongs to budget.py or handback.py when its command names `budget` or `handback` (main: `.../scripts/budget.py`; lean: `.../run_hook.py budget`).
Worker or main thread: the debug file does not name the agent, so the lab's harness.jsonl decides: a start finished between a worker's `start` and `end` line (their `t`) is a worker's, except `PostToolUse:Agent` and `PreToolUse:Agent`, which only the main thread runs; everything else is the main thread's.
Reported per run: n and median ms of worker PostToolUse starts of budget.py, of main-thread PostToolUse starts, and the sums of all budget.py + handback.py starts (worker, main). Per pair: median(main arm) - median(new arm) for worker PostToolUse starts, and whether it is >= 25 ms.
"""
import datetime, json, re, statistics as st, sys

S = "/private/tmp/murmuration-w06/author-w06-6"
LINE = re.compile(r"^(\S+) \[DEBUG\] Hooks: (\w+)(?::(\S+))? \[(.*)\] \(plugin murmuration@inline\) finished with status \d+ \((\d+)ms\)")


def epoch(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def run(name):
    d = "%s/runs/%s" % (S, name)
    wins = {}
    for l in open(d + "/lab/__statera__/harness.jsonl"):
        r = json.loads(l)
        if r.get("event") in ("start", "end") and r.get("agent_id"):
            wins.setdefault(r["agent_id"], {})[r["event"]] = epoch(r["t"])
    wins = [(w["start"], w.get("end", 1e18)) for w in wins.values() if "start" in w]
    rows = []
    for l in open(d + "/dbg.log", errors="replace"):
        m = LINE.match(l)
        if not m:
            continue
        ts, event, tool, cmd, ms = m.groups()
        script = "budget" if "budget" in cmd else ("handback" if "handback" in cmd else None)
        if not script:
            continue
        t = epoch(ts)
        worker = tool != "Agent" and any(a <= t <= b + 0.5 for a, b in wins)
        rows.append(dict(event=event, tool=tool, script=script, ms=int(ms), worker=worker))
    return rows


def med(v):
    return st.median(v) if v else float("nan")


def summary(rows):
    pw = [r["ms"] for r in rows if r["script"] == "budget" and r["event"] == "PostToolUse" and r["worker"]]
    pm = [r["ms"] for r in rows if r["script"] == "budget" and r["event"] == "PostToolUse" and not r["worker"]]
    return dict(pw=pw, pm=pm, sum_w=sum(r["ms"] for r in rows if r["worker"]), sum_m=sum(r["ms"] for r in rows if not r["worker"]), n_all=len(rows))


print("| pair | arm | run | worker PostToolUse budget starts: n, median ms | main PostToolUse starts: n, median ms | budget+handback starts, sum ms: worker / main thread (n) |\n|:--|:--|:--|:--|:--|:--|")
diffs = []
for i, pair in enumerate(sys.argv[1:], 1):
    a, b = pair.split(":")
    sa, sb = summary(run(a)), summary(run(b))
    for arm, nm, s in (("main", a, sa), ("new", b, sb)):
        print("| %d | %s | %s | %d, %.0f | %d, %.0f | %d / %d (%d) |" % (i, arm, nm, len(s["pw"]), med(s["pw"]), len(s["pm"]), med(s["pm"]), s["sum_w"], s["sum_m"], s["n_all"]))
    diffs.append((i, med(sa["pw"]) - med(sb["pw"]), med(sa["pm"]) - med(sb["pm"]), sa["sum_w"] + sa["sum_m"], sb["sum_w"] + sb["sum_m"]))
print("\n| pair | worker PostToolUse median, main minus new (ms) | pass (>= 25) | main-thread PostToolUse median, main minus new (ms) | run sum main arm (ms) | run sum new arm (ms) |\n|:--|--:|:--|--:|--:|--:|")
for i, dw, dm, ta, tb in diffs:
    print("| %d | %.0f | %s | %.0f | %d | %d |" % (i, dw, "yes" if dw >= 25 else "NO", dm, ta, tb))
print("\nall pairs pass: %s; median of the differences: %.0f ms" % (all(d[1] >= 25 for d in diffs), med([d[1] for d in diffs])))
pooled = {"main": [], "new": [], "main_m": [], "new_m": []}
for pair in sys.argv[1:]:
    x, y = pair.split(":")
    sx, sy = summary(run(x)), summary(run(y))
    pooled["main"] += sx["pw"]; pooled["new"] += sy["pw"]; pooled["main_m"] += sx["pm"]; pooled["new_m"] += sy["pm"]
print("pooled over all pairs: worker PostToolUse starts main arm n=%d median %.0f ms, new arm n=%d median %.0f ms (difference %.0f ms); main-thread PostToolUse starts main arm n=%d median %.0f ms, new arm n=%d median %.0f ms (difference %.0f ms)" % (
    len(pooled["main"]), med(pooled["main"]), len(pooled["new"]), med(pooled["new"]), med(pooled["main"]) - med(pooled["new"]),
    len(pooled["main_m"]), med(pooled["main_m"]), len(pooled["new_m"]), med(pooled["new_m"]), med(pooled["main_m"]) - med(pooled["new_m"])))
