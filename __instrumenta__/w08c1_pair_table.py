# Tables the paired start-time bench: reads the JSONL of w07c6_pair_bench (arm, payload, round, wall_ns, user_us, sys_us, rc, load1) and two arm names; writes a markdown table per payload name: medians, paired difference A-B (median, p10, p90) and the number of pairs in which A is slower, for wall and CPU.
# usage: python3 -I w08c1_pair_table.py BENCH.jsonl A B [--out FILE]
import json, sys, statistics as st

def q(xs, f):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(round(f * (len(xs) - 1)))))]

def table(path, a, b):
    rows = [json.loads(l) for l in open(path)]
    by = {}
    for r in rows:
        by.setdefault((r["payload"].split("/")[-1], r["round"]), {})[r["arm"]] = r
    names = sorted({k[0] for k in by})
    out = ["| payload | pairs | %s wall med | %s wall med | %s-%s wall med [p10, p90] | %s slower (wall) | %s-%s CPU med [p10, p90] | %s slower (CPU) | load1 med |" % (a, b, a, b, a, a, b, a),
           "|:--|--:|--:|--:|:--|--:|:--|--:|--:|"]
    for n in names + ["ALL"]:
        v = [x for (p, _), x in by.items() if (p == n or n == "ALL") and a in x and b in x and x[a]["rc"] == 0 and x[b]["rc"] == 0]
        if not v:
            continue
        w = [(x[a]["wall_ns"] - x[b]["wall_ns"]) / 1e6 for x in v]
        c = [(x[a]["user_us"] + x[a]["sys_us"] - x[b]["user_us"] - x[b]["sys_us"]) / 1e3 for x in v]
        out.append("| %s | %d | %.1f | %.1f | %.1f [%.1f, %.1f] | %d | %.1f [%.1f, %.1f] | %d | %.1f |" % (
            n, len(v), st.median(x[a]["wall_ns"] / 1e6 for x in v), st.median(x[b]["wall_ns"] / 1e6 for x in v), st.median(w), q(w, .1), q(w, .9),
            sum(d > 0 for d in w), st.median(c), q(c, .1), q(c, .9), sum(d > 0 for d in c), st.median(x[a]["load1"] for x in v)))
    return "\n".join(out)

if __name__ == "__main__":
    t = table(sys.argv[1], sys.argv[2], sys.argv[3])
    if "--out" in sys.argv:
        open(sys.argv[sys.argv.index("--out") + 1], "w").write(t + "\n")
    print(t)
