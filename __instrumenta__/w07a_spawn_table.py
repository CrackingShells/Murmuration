"""Summarises JSONL from w07a_spawn_bench (one row per spawn: case, round, wall_ns, user_us, sys_us, rc, load1) into a markdown table: per case n, median/p90/min wall ms, median CPU ms, median load1, plus per-round paired difference to a reference case (median and p10-p90 of case minus reference within the same round). Input: one or more JSONL paths, --ref CASE; output: markdown on stdout."""
import json, sys, statistics as st
args = sys.argv[1:]
ref = args[args.index("--ref") + 1] if "--ref" in args else None
files = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] != "--ref")]
rows = [json.loads(l) for f in files for l in open(f) if l.strip()]
rows = [r for r in rows if "wall_ns" in r]
def q(v, p):
    v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
cases = list(dict.fromkeys(r["case"] for r in rows))
by = {c: [r for r in rows if r["case"] == c] for c in cases}
byround = {}
for r in rows: byround.setdefault((r.get("file", 0), r["round"]), {}).setdefault(r["case"], r["wall_ns"] / 1e6)
print("| case | n | wall median ms | p90 | min | cpu median ms (u+s) | load1 median | paired diff vs %s: median [p10, p90] ms |" % ref)
print("|:--|--:|--:|--:|--:|--:|--:|:--|")
for c in cases:
    w = [r["wall_ns"] / 1e6 for r in by[c]]; cpu = [(r["user_us"] + r["sys_us"]) / 1e3 for r in by[c]]
    ld = st.median(r["load1"] for r in by[c])
    d = ""
    if ref and c != ref:
        dd = [rr[c] - rr[ref] for rr in byround.values() if c in rr and ref in rr]
        if dd: d = "%+.2f [%+.2f, %+.2f] (n=%d)" % (st.median(dd), q(dd, .1), q(dd, .9), len(dd))
    print("| %s | %d | %.2f | %.2f | %.2f | %.2f | %.1f | %s |" % (c, len(w), st.median(w), q(w, .9), min(w), st.median(cpu), ld, d))
