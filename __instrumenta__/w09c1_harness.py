"""Re-derives M5 (budget hook, workers over budget) and M7 (name binding before/after w08-c12) of explorer-w09-f's findings per unique worker (agent_id), not per record, from the sibling worktrees' `__statera__/harness.jsonl` and the `.meta.json` names under ~/.claude/projects (read only); output: markdown on stdout."""
import json, glob, os, datetime, collections, statistics as st
root = os.path.expanduser("~/.claude/projects"); lab = os.path.abspath(os.path.dirname(__file__) + "/../..")
MERGE = datetime.datetime.fromisoformat("2026-10-24T03:18:27+09:00")  # 3d5147a, w08-c12
FREEZE = datetime.datetime.fromisoformat("2026-10-25T00:00:00+00:00")  # records after this are the live wave-9 run, left out
meta = {}
for m in glob.glob(root + "/*/*/subagents/agent-*.meta.json"):
    try: meta[os.path.basename(m)[6:-10]] = json.load(open(m)).get("name") or ""
    except Exception: pass
def T(s): return datetime.datetime.fromisoformat(s)
R = []
for f in sorted(glob.glob(lab + "/*/__statera__/harness.jsonl")):
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("t") and T(r["t"]) < FREEZE: r["lab"] = f.split("/")[-3]; R.append(r)
# ---- M5
by = collections.defaultdict(list)
for r in R: by[(r["lab"], r.get("agent_id"))].append(r)
ends = [r for r in R if r["event"] == "end"]
print("## M5 (per record vs per worker; records before 2026-10-25T00:00Z)")
print("records: start %d, end %d, raise %d, note %d; unique workers with a start %d, with an end %d, starts with no end %d" % (sum(r["event"]=="start" for r in R), len(ends), sum(r["event"]=="raise" for r in R), sum(r["event"]=="note" for r in R), sum(1 for k, v in by.items() if any(x["event"]=="start" for x in v)), sum(1 for k, v in by.items() if any(x["event"]=="end" for x in v)), sum(1 for k, v in by.items() if any(x["event"]=="start" for x in v) and not any(x["event"]=="end" for x in v))))
fr = [r["frac"] for r in ends]
print("end records: n %d, median frac %.2f, max %.2f, over 1.0: %d, with stops>0: %d" % (len(fr), st.median(fr), max(fr), sum(x > 1 for x in fr), sum(1 for r in ends if r.get("stops"))))
fin = {}
for k, v in by.items():
    e = [x for x in v if x["event"] == "end"]
    if e: fin[k] = (max(e, key=lambda x: x["t"]), [x for x in v if x["event"] == "raise"], [x for x in v if x["event"] == "start"])
ff = [v[0]["frac"] for v in fin.values()]
print("per worker (last end record): n %d, median frac %.2f, max %.2f, over 1.0 B_at_end: %d, share of workers with at least one raise: %d of %d" % (len(ff), st.median(ff), max(ff), sum(x > 1 for x in ff), sum(1 for v in fin.values() if v[1]), len(fin)))
rr = []
for k, (e, rs, ss) in fin.items():
    if rs:
        B0 = min(x["B_before"] for x in rs)
        rr.append((k[0][:12], e["name"], e["used"], B0, e["used"] / B0, len(rs)))
print("workers with a raise: n %d; spend at last end / budget before their first raise: median %.2f, max %.2f; over 1.0 of the pre-raise budget: %d" % (len(rr), st.median(x[4] for x in rr), max(x[4] for x in rr), sum(x[4] > 1 for x in rr)))
for x in sorted(rr, key=lambda x: -x[4])[:6]: print("   ", x)
tf = [v[0]["t_frac"] for v in fin.values() if v[0].get("t_frac") is not None]
print("time: per worker median t_frac %.2f, over 1.0 T_at_end: %d of %d" % (st.median(tf), sum(x > 1 for x in tf), len(tf)))
# ---- M7
print("\n## M7 (per dispatch: the first, non-resumed start of each agent_id; merge 3d5147a = 2026-10-24T03:18:27+09:00)")
disp = []
for k, v in by.items():
    s = sorted([x for x in v if x["event"] == "start" and not x.get("resumed")], key=lambda x: x["t"])
    if s: disp.append(s[0])
byt = collections.defaultdict(list)
for d in disp: byt[(d["lab"], d["type"])].append(d)
for d in disp:
    d["batch"] = any(o is not d and abs((T(o["t"]) - T(d["t"])).total_seconds()) <= 5 for o in byt[(d["lab"], d["type"])])
    d["real"] = meta.get(d["agent_id"]); d["after"] = T(d["t"]) >= MERGE
print("| side | dispatches | with meta name | in a same-type batch (starts within 5 s) | wrong name | wrong name, in a batch | name_unconfirmed |"); print("|:--|--:|--:|--:|--:|--:|--:|")
for side in (False, True):
    D = [d for d in disp if d["after"] == side]; W = [d for d in D if d["real"]]
    bad = [d for d in W if d["name"] != d["real"] and not d.get("name_unconfirmed")]
    print("| %s | %d | %d | %d | %d | %d | %d |" % ("after" if side else "before", len(D), len(W), sum(d["batch"] for d in W), len(bad), sum(d["batch"] for d in bad), sum(bool(d.get("name_unconfirmed")) for d in D)))
allst = [x for x in R if x["event"] == "start" and meta.get(x["agent_id"])]
print("\nstart records (the explorer's unit, resumes included): %d with a meta name, %d wrong name, of which resume starts %d" % (len(allst), sum(1 for x in allst if x["name"] != meta[x["agent_id"]] and not x.get("name_unconfirmed")), sum(1 for x in allst if x["name"] != meta[x["agent_id"]] and not x.get("name_unconfirmed") and x.get("resumed"))))
print("wrong-name dispatches by source:", dict(collections.Counter(d.get("source") for d in disp if d["real"] and d["name"] != d["real"] and not d.get("name_unconfirmed"))))
print("after-merge batches (size, names):")
for d in sorted([d for d in disp if d["after"] and d["batch"]], key=lambda d: d["t"]): print("   ", d["t"][:19], d["lab"][:14], d["type"][12:], d["name"], "meta:", d["real"], "unconf" if d.get("name_unconfirmed") else "")
# ---- live wave-9 starts (after the freeze; the file grows, these lines are not part of the frozen figures)
print("\nlive wave-9 start records (not frozen; as of the run):")
for f in sorted(glob.glob(lab + "/*/__statera__/harness.jsonl")):
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("event") in ("start", "named") and r.get("t") and T(r["t"]) >= FREEZE:
            print("   ", r["t"][:19], r["event"], r.get("name"), "meta:", meta.get(r["agent_id"]), "B=%s" % r.get("B"), "unconfirmed %s" % r.get("name_unconfirmed") if r.get("name_unconfirmed") else "", r.get("candidates", ""))
