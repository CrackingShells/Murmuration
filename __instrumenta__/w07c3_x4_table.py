# w07-c3: x4 table: per pair and arm, the median platform-recorded duration (debug file `Hooks: <Event[:tool]> [<command>] (plugin murmuration@inline) finished with status N (X ms)`) of the guard's PreToolUse hook and of the budget PostToolUse hook, A minus B per pair, the sign count and the per-event table of every other murmuration hook; inputs: RUNS_DIR PAIRS_LOG SCENARIO N; output: markdown on stdout
"""usage: w07c3_x4_table.py RUNS_DIR PAIRS_LOG SCENARIO N     (runs RUNS_DIR/<scenario>_<i>_A and _B for i = 1..N; load averages from PAIRS_LOG lines `pair i load_start x load_end y`)
Hook kinds: guard = event PreToolUse with `permission_guard` in the command; budget-post = event PostToolUse with `run_hook.py budget` (all agents, main thread and workers pooled: the debug file does not name the agent;
the worker-only column uses the lab's harness.jsonl `start`/`end` windows as in w06c9_measure.py). Reported: per pair medians (ms), A minus B, B lower in how many pairs, median saving, min, max, quartiles; pooled medians over all starts."""
import datetime, json, re, statistics as st, sys

RUNS, PLOG, SC, N = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
LINE = re.compile(r"^(\S+) \[DEBUG\] Hooks: (\w+)(?::(\S+))? \[(.*)\] \(plugin murmuration@inline\) finished with status (\d+) \((\d+)ms\)")
epoch = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
med = lambda v: st.median(v) if v else float("nan")


def kinds(d):
    wins = {}
    try:
        for l in open(d + "/lab/__statera__/harness.jsonl"):
            r = json.loads(l)
            if r.get("event") in ("start", "end") and r.get("agent_id"):
                wins.setdefault(r["agent_id"], {})[r["event"]] = epoch(r["t"])
    except FileNotFoundError:
        pass
    wins = [(w["start"], w.get("end", 1e18)) for w in wins.values() if "start" in w]
    out = {}
    for l in open(d + "/dbg.log", errors="replace"):
        m = LINE.match(l)
        if not m:
            continue
        ts, event, tool, cmd, status, ms = m.groups()
        t = epoch(ts)
        worker = tool != "Agent" and any(a <= t <= b + 0.5 for a, b in wins)
        if "permission_guard" in cmd:
            k = "guard PreToolUse"
        elif "user_words" in cmd:
            k = "user_words UserPromptSubmit"
        elif re.search(r"run_hook\.py\"? budget", cmd):
            k = "budget %s%s" % (event, ":Agent" if tool == "Agent" else "")
        elif re.search(r"run_hook\.py\"? handback", cmd):
            k = "handback %s" % event
        else:
            continue
        out.setdefault(k, []).append(int(ms))
        if k == "budget PostToolUse" and worker:
            out.setdefault("budget PostToolUse (worker)", []).append(int(ms))
    return out


loads = {}
for l in open(PLOG):
    m = re.match(r"pair (\d+) load_start ([\d.]+) load_end ([\d.]+)", l)
    if m and not l.startswith("pair 90"):
        loads[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
data = {i: {arm: kinds("%s/%s_%d_%s" % (RUNS, SC, i, arm)) for arm in "AB"} for i in range(1, N + 1)}
allk = sorted({k for i in data for arm in "AB" for k in data[i][arm]})
for key in ("guard PreToolUse", "budget PostToolUse", "budget PostToolUse (worker)"):
    print("### %s: per-pair medians of the platform-recorded duration, ms\n" % key)
    print("| pair | load avg start / end | A n | A median | B n | B median | A minus B | B lower |\n|--:|:--|--:|--:|--:|--:|--:|:--|")
    diffs = []
    for i in range(1, N + 1):
        a, b = data[i]["A"].get(key, []), data[i]["B"].get(key, [])
        d = med(a) - med(b); diffs.append(d)
        print("| %d | %.2f / %.2f | %d | %.1f | %d | %.1f | %.1f | %s |" % (i, *loads.get(i, (float("nan"),) * 2), len(a), med(a), len(b), med(b), d, "yes" if d > 0 else "NO"))
    q = st.quantiles(diffs, n=4) if len(diffs) > 1 else [float("nan")] * 3
    print("\nB lower in %d of %d pairs; median saving %.1f ms; min %.1f, max %.1f, quartiles %.1f / %.1f; pooled over all starts: A %.1f ms (n = %d), B %.1f ms (n = %d)\n" % (
        sum(d > 0 for d in diffs), len(diffs), med(diffs), min(diffs), max(diffs), q[0], q[2],
        med([x for i in data for x in data[i]["A"].get(key, [])]), sum(len(data[i]["A"].get(key, [])) for i in data),
        med([x for i in data for x in data[i]["B"].get(key, [])]), sum(len(data[i]["B"].get(key, [])) for i in data)))
print("### every murmuration hook kind: pooled median ms over all pairs, and the number of pairs in which B's per-pair median is lower\n")
print("| hook kind | A pooled median (n) | B pooled median (n) | pairs with both arms | B lower in |\n|:--|:--|:--|--:|--:|")
for k in allk:
    pa = [x for i in data for x in data[i]["A"].get(k, [])]; pb = [x for i in data for x in data[i]["B"].get(k, [])]
    both = [i for i in data if data[i]["A"].get(k) and data[i]["B"].get(k)]
    lower = sum(med(data[i]["B"][k]) < med(data[i]["A"][k]) for i in both)
    print("| %s | %.1f (%d) | %.1f (%d) | %d | %d |" % (k, med(pa), len(pa), med(pb), len(pb), len(both), lower))
print("\n### sum of the platform-recorded durations of every murmuration hook start in a session, ms (hooks run concurrently with siblings, so this is hook-time, not wall time)\n")
print("| pair | A starts, sum ms | B starts, sum ms | A minus B |\n|--:|--:|--:|--:|")
tot = []
for i in range(1, N + 1):
    sa = sum(sum(v) for k, v in data[i]["A"].items() if "(worker)" not in k); sb = sum(sum(v) for k, v in data[i]["B"].items() if "(worker)" not in k)
    na = sum(len(v) for k, v in data[i]["A"].items() if "(worker)" not in k); nb = sum(len(v) for k, v in data[i]["B"].items() if "(worker)" not in k)
    tot.append(sa - sb); print("| %d | %d (%d starts) | %d (%d starts) | %d |" % (i, sa, na, sb, nb, sa - sb))
print("\nmedian per-session difference %.0f ms; min %d, max %d" % (med(tot), min(tot), max(tot)))
