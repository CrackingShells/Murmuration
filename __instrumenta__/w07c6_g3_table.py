# Pairs the rows of w07c6_pair_bench by round and reports, for wall time and for CPU time (user+sys of the child), the paired difference A minus B (positive = B cheaper), how many pairs B wins, per-arm medians, spread and load; inputs: rows.jsonl [payload_sizes.tsv]; output: markdown on stdout.
# usage: python3 -I __instrumenta__/w07c6_g3_table.py rows.jsonl [payload_sizes.tsv]
import json, statistics as st, sys, os
rows = [json.loads(l) for l in open(sys.argv[1])]
bad = [r for r in rows if r["rc"] != 0]
by = {}
for r in rows:
    by.setdefault(r["round"], {})[r["arm"]] = r
pairs = [(v["A"], v["B"]) for k, v in sorted(by.items()) if "A" in v and "B" in v and v["A"]["rc"] == 0 and v["B"]["rc"] == 0]
sizes = {}
if len(sys.argv) > 2:
    for l in open(sys.argv[2]):
        i, n = l.split(); sizes[int(i)] = int(n)
def q(xs, p):
    xs = sorted(xs); k = (len(xs) - 1) * p; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)
def report(label, ps):
    out = ["| %s | pairs %d |" % (label, len(ps))]
    for name, fn in (("wall ms", lambda r: r["wall_ns"] / 1e6), ("CPU ms (user+sys)", lambda r: (r["user_us"] + r["sys_us"]) / 1e3)):
        a, b = [fn(x[0]) for x in ps], [fn(x[1]) for x in ps]
        d = [x - y for x, y in zip(a, b)]
        out.append("| %s | A median %.2f | B median %.2f | A-B median %.2f [p10 %.2f, p90 %.2f] | B cheaper in %d of %d |" % (name, st.median(a), st.median(b), st.median(d), q(d, .1), q(d, .9), sum(x > 0 for x in d), len(d)))
    return out
print("rows %d, non-zero exit codes %d (payloads that the guard denies still exit 0)" % (len(rows), len(bad)))
print("load1 median %.2f (p10 %.2f, p90 %.2f)" % (st.median(r["load1"] for r in rows), q([r["load1"] for r in rows], .1), q([r["load1"] for r in rows], .9)))
print("\n".join(report("all", pairs)))
if sizes:
    def sz(p): return sizes[int(os.path.basename(p["payload"])[1:-5])]
    srt = sorted(pairs, key=lambda x: sz(x[0]))
    t = len(srt) // 3
    for name, part in (("smallest third (<= %d B)" % sz(srt[t - 1][0]), srt[:t]), ("middle third", srt[t:2 * t]), ("largest third (>= %d B)" % sz(srt[2 * t][0]), srt[2 * t:])):
        print("\n".join(report(name, part)))
