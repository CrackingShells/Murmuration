"""Re-derives from the lab's six `__statera__/harness.jsonl` files (the live wave-9 file left out), per worker (agent_id) not per record: ends, last end's USD and time fraction of the budget in force, raises, fraction against the budget before the first raise, duplicate records; also per-dispatch name checks (start records: first non-resumed start per agent_id, batch within 5 s, name vs agent) to stdout; independent of w09f/w09c1 scripts."""
import json, glob, collections, statistics as st, os
root = "/Users/hacker/Documents/tmp/claude-worktrees/Murmuration"
recs = []
for f in sorted(glob.glob(root + "/*/__statera__/harness.jsonl")):
    if "wave-9" in f: continue
    for i, l in enumerate(open(f)):
        r = json.loads(l); r["_f"] = f.split("/")[-3]; r["_i"] = i; recs.append(r)
print("records", len(recs), collections.Counter(r["event"] for r in recs))
key = lambda r: json.dumps({k: v for k, v in r.items() if k not in ("_f", "_i")}, sort_keys=True)
c = collections.Counter(key(r) for r in recs); print("exact duplicate records:", sum(v - 1 for v in c.values()))
ends = collections.defaultdict(list); raises = collections.defaultdict(list)
for r in recs:
    if r["event"] == "end": ends[r["agent_id"]].append(r)
    if r["event"] == "raise": raises[r["agent_id"]].append(r)
print("end records", sum(len(v) for v in ends.values()), "workers with an end", len(ends))
last = {a: max(v, key=lambda r: r["t"]) for a, v in ends.items()}
fr = [r["used"] / r["B"] for r in last.values()]; tf = [r["t_frac"] for r in last.values()]
print("last end: USD frac median %.3f max %.3f over1 %d; blocks(stops>0) %d; time over1 %d" % (st.median(fr), max(fr), sum(x > 1 for x in fr), sum(1 for r in last.values() if r.get("stops")), sum(x > 1 for x in tf)))
# any end record of any resume above 1?
print("end records with used/B>1:", sum(1 for v in ends.values() for r in v if r["used"] / r["B"] > 1), " t_frac>1:", sum(1 for v in ends.values() for r in v if r["t_frac"] > 1))
rw = [a for a in ends if a in raises]; print("workers with end and raise", len(rw), "raise records", sum(len(raises[a]) for a in raises), "workers raised overall", len(raises), "of which no end:", len([a for a in raises if a not in ends]))
x = []
for a in rw:
    r0 = min(raises[a], key=lambda r: r["t"]); Bb = r0["B_before"]; e = last[a]
    x.append((e["used"] / Bb, e["name"]))
print("vs budget before first raise: over1", [(round(v, 2), n) for v, n in x if v > 1], "median %.2f" % st.median(v for v, n in x), "n", len(x))
