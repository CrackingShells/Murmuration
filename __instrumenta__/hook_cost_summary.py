"""Summarizes hook_cost_time.py results: per (case, script, variant) the n, median and p90 wall time, median CPU time, and the share of runs that exited 0 with equal output.

Input: one or more results.jsonl (argv[1:]); with `--ratio A B` (two variant names) a column with median(B)/median(A) is added. Output: a markdown table on stdout.
p90 is the 90th percentile by nearest rank (sorted values, index ceil(0.9 n) - 1).
"""
import collections, json, math, statistics, sys

argv = sys.argv[1:]
pair = None
if "--ratio" in argv:
    i = argv.index("--ratio")
    pair = argv[i + 1:i + 3]
    argv = argv[:i] + argv[i + 3:]
rows = [json.loads(l) for f in argv for l in open(f)]
cells = collections.defaultdict(list)
for r in rows:
    cells[(r["case"], r["script"], r["variant"])].append(r)


def p90(xs):
    xs = sorted(xs)
    return xs[math.ceil(0.9 * len(xs)) - 1]


stat = {}
for k, rs in sorted(cells.items()):
    w = [r["wall_ms"] for r in rs]
    stat[k] = (len(rs), statistics.median(w), p90(w), statistics.median(r["cpu_ms"] for r in rs), sum(r["rc"] == 0 for r in rs), sorted({r["out_len"] for r in rs}))
print("| case | script | variant | n | wall median ms | wall p90 ms | cpu median ms | rc=0 | stdout bytes |")
print("|:--|:--|:--|--:|--:|--:|--:|--:|:--|")
for (case, script, var), (n, med, p, cpu, ok, ol) in stat.items():
    print("| %s | %s | %s | %d | %.1f | %.1f | %.1f | %d | %s |" % (case, script, var, n, med, p, cpu, ok, ",".join(map(str, ol))))
if pair:
    print("\n| case | script | %s median ms | %s median ms | ratio (new/old) | %s cpu | %s cpu | cpu ratio |" % (pair[0], pair[1], pair[0], pair[1]))
    print("|:--|:--|--:|--:|--:|--:|--:|--:|")
    for (case, script, var) in sorted(stat):
        if var == pair[0] and (case, script, pair[1]) in stat:
            a, b = stat[(case, script, pair[0])], stat[(case, script, pair[1])]
            print("| %s | %s | %.1f | %.1f | %.2f | %.1f | %.1f | %.2f |" % (case, script, a[1], b[1], b[1] / a[1], a[3], b[3], b[3] / a[3]))
