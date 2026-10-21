"""Serial hook seconds per wave: wave 4's start counts per registration and thread type (hook_count_invocations.py JSON) times the median wall per start of the old and the new plugin (hook_cost_time.py rows), to a table on stdout.

usage: w05c4_m2_sum.py TIMING.jsonl COUNTS.json [--bootstrap N] [--sizes SHORT_BYTES,LONG_BYTES]
TIMING.jsonl: rows of `hook_cost_time.py --variant old=... --variant new=...` (case, variant, script, wall_ms). COUNTS.json: the output of hook_count_invocations.py for the wave's main session (`starts.main`, `starts.workers`, per registration `Event|matcher|script`).
A worker's transcript size sets the price of its starts: both bounds are given (the 0.31 MB `short` and the 5.56 MB `long` transcript of the timing run). A registration the new plugin does not have (PostToolBatch) costs it zero. Sum = serial seconds; the starts overlap in the platform, so it is a sum and not a wall time.
--sizes: the byte sizes of the two timing transcripts (default 310000,5560000); a third price, `interp`, interpolates a worker start between the two by half of that worker's final transcript size (COUNTS.json `workers[].bytes`; a transcript grows during its run), weighted by the worker's tool calls.
--bootstrap N: 95% interval of the new/old ratio of the sums, resampling the timing rows of each cell N times (default 2000).
"""
import collections, json, random, statistics as st, sys
argv = sys.argv[1:]
n_boot = int(argv[argv.index("--bootstrap") + 1]) if "--bootstrap" in argv else 2000
rows = [json.loads(l) for l in open(argv[0])]; full = json.load(open(argv[1])); counts = full["starts"]
SB, LB = (float(x) for x in (argv[argv.index("--sizes") + 1] if "--sizes" in argv else "310000,5560000").split(","))
ws = [w for w in full["workers"] if w.get("bytes") is not None and w["tool_calls"]]
F = sum(w["tool_calls"] * min(1.0, max(0.0, (w["bytes"] / 2 - SB) / (LB - SB))) for w in ws) / sum(w["tool_calls"] for w in ws)
cells = collections.defaultdict(list)
for r in rows:
    cells[(r["case"], r["script"], r["variant"])].append(r["wall_ms"])
# registration -> (thread class, case template, script); {k} = short or long
MAP = {
 ("main", "PostToolUse||budget.py"): ("post_tool_use:main", "budget"), ("main", "PostToolBatch||budget.py"): ("post_tool_batch:main", "budget"),
 ("main", "PreToolUse|Agent|Task|budget.py"): ("pre_tool_use:dispatch", "budget"),
 ("workers", "PostToolUse||budget.py"): ("post_tool_use:worker-{k}", "budget"), ("workers", "PostToolBatch||budget.py"): ("post_tool_batch:worker-{k}", "budget"),
 ("workers", "PostToolUse|SubagentHandback|handback.py"): ("post_tool_use:handback", "handback"), ("workers", "PreToolUse|SubagentHandback|handback.py"): ("pre_tool_use:handback-explorer-no-report", "handback"),
 ("workers", "SubagentStart||budget.py"): ("subagent_start:worker", "budget"), ("workers", "SubagentStop||budget.py"): ("subagent_stop:worker-{k}", "budget"),
 ("workers", "SubagentStop||handback.py"): ("subagent_stop:worker-{k}", "handback"),
}
def med(case, script, variant, rnd=None):
    if "{k}" in case or "worker-interp" in case:
        a, b = med(case.replace("worker-interp", "worker-short"), script, variant, rnd), med(case.replace("worker-interp", "worker-long"), script, variant, rnd)
        return None if a is None or b is None else a + F * (b - a)
    v = cells.get((case, script, variant))
    if not v:
        return 0.0 if variant == "new" and case.startswith("post_tool_batch") else None
    if rnd:
        v = rnd.choices(v, k=len(v))
    return st.median(v)
def total(k, variant, rnd=None):
    s = 0.0
    for cls in ("main", "workers"):
        for reg, n in counts[cls].items():
            if (cls, reg) not in MAP or not n:
                continue
            case, script = MAP[(cls, reg)]
            m = med(case.format(k=k), script, variant, rnd)
            if m is None:
                continue
            s += n * m
    return s / 1000
print("| thread / registration | starts in wave 4 | old ms | new ms (short / long transcript) |\n|:--|--:|--:|--:|")
for cls in ("main", "workers"):
    for reg, n in counts[cls].items():
        if (cls, reg) not in MAP or not n:
            continue
        case, script = MAP[(cls, reg)]
        o = [med(case.format(k=k), script, "old") for k in ("short", "long")]
        w = [med(case.format(k=k), script, "new") for k in ("short", "long")]
        f = lambda x: "-" if x is None else "%.1f" % x
        print("| %s %s | %d | %s / %s | %s / %s |" % (cls, reg, n, f(o[0]), f(o[1]), f(w[0]), f(w[1])))
rnd = random.Random(20261021)
print("\ninterpolation weight F (0 = short transcript price, 1 = long) = %.3f over %d workers" % (F, len(ws)))
for k in ("short", "interp", "long"):
    o, w = total(k, "old"), total(k, "new")
    boots = sorted(total(k, "new", rnd) / total(k, "old", rnd) for _ in range(n_boot))
    print("\ntranscript price = %s: old %.1f s, new %.1f s serial per wave; new/old %.3f (95%% bootstrap %.3f to %.3f); down %.1f%%" % (k, o, w, w / o, boots[int(.025 * n_boot)], boots[int(.975 * n_boot)], 100 * (1 - w / o)))
