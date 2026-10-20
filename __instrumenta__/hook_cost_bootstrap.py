"""Bootstrap interval of the ratio median(new)/median(old) of hook wall and CPU time, per case, from a hook_cost_time.py results file.

Input: argv[1] = results.jsonl; optional argv[2] = number of resamples (default 5000). Seed 20261020. Output: a markdown table (case, script, ratio, 95% interval, for wall and CPU),
and one pooled row for the two registrations that run at every tool call on the long transcript (PostToolUse and PostToolBatch of the budget hook).
"""
import collections, json, random, statistics, sys

rows = [json.loads(l) for l in open(sys.argv[1])]
B = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
rnd = random.Random(20261020)
cell = collections.defaultdict(list)
for r in rows:
    cell[(r["case"], r["script"], r["variant"])].append(r)


def interval(old, new):
    base = statistics.median(new) / statistics.median(old)
    xs = sorted(statistics.median(rnd.choices(new, k=len(new))) / statistics.median(rnd.choices(old, k=len(old))) for _ in range(B))
    return base, xs[int(0.025 * B)], xs[int(0.975 * B)]


print("| case | script | wall ratio | wall 95% | cpu ratio | cpu 95% |")
print("|:--|:--|--:|:--|--:|:--|")
for (case, script, var) in sorted(cell):
    if var != "old":
        continue
    w = interval([r["wall_ms"] for r in cell[(case, script, "old")]], [r["wall_ms"] for r in cell[(case, script, "new")]])
    c = interval([r["cpu_ms"] for r in cell[(case, script, "old")]], [r["cpu_ms"] for r in cell[(case, script, "new")]])
    print("| %s | %s | %.2f | %.2f to %.2f | %.2f | %.2f to %.2f |" % (case, script, w[0], w[1], w[2], c[0], c[1], c[2]))
pool = ("post_tool_use:worker-long", "post_tool_batch:worker-long")
old = [r["wall_ms"] for k in pool for r in cell[(k, "budget", "old")]]
new = [r["wall_ms"] for k in pool for r in cell[(k, "budget", "new")]]
w = interval(old, new)
oc = [r["cpu_ms"] for k in pool for r in cell[(k, "budget", "old")]]
nc = [r["cpu_ms"] for k in pool for r in cell[(k, "budget", "new")]]
c = interval(oc, nc)
print("| pooled PostToolUse + PostToolBatch, long worker | budget | %.2f | %.2f to %.2f | %.2f | %.2f to %.2f |" % (w[0], w[1], w[2], c[0], c[1], c[2]))
