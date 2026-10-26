"""Summarises the `end` records of the sibling worktrees' `__statera__/harness.jsonl` (cost fraction of the budget, time fraction, notes k, blocks `stops`, per worker type); input: the harness files next to this lab; output: markdown on stdout."""
import json, glob, os, statistics as st, collections
lab = os.path.abspath(os.path.dirname(__file__) + "/../..")
E = []
for f in sorted(glob.glob(lab + "/*/__statera__/harness.jsonl")):
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("event") == "end": E.append(r)
print("| type | workers | median cost/B | share over 1.0 B | share over 1.5 B | max cost/B | workers with a block | median time/T | share over 1.0 T |"); print("|:--|--:|--:|--:|--:|--:|--:|--:|--:|")
g = collections.defaultdict(list)
for r in E: g[r["type"]].append(r)
for k, v in sorted(g.items()) + [("all", E)]:
    fr = [r["frac"] for r in v]; tf = [r["t_frac"] for r in v if r.get("t_frac") is not None]
    print("| %s | %d | %.2f | %.2f | %.2f | %.2f | %d | %.2f | %.2f |" % (k, len(v), st.median(fr), sum(x > 1 for x in fr) / len(fr), sum(x > 1.5 for x in fr) / len(fr), max(fr), sum(1 for r in v if r.get("stops")), st.median(tf), sum(x > 1 for x in tf) / len(tf)))
