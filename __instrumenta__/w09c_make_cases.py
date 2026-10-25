# w09-c: builds cases.jsonl (one judge-ready case per line: id, group, tool, input, user prompt, label, weight, stratum) from w09a outputs (refusals.jsonl, allowed_sample.jsonl, retry_pairs.jsonl, classified.jsonl) and the committed synthetic set; allows are a seeded stratified subsample of allowed_sample.jsonl with weights N_h/m_h. Usage: python3 -I w09c_make_cases.py SET_DIR SYNTH_JSON OUT_JSONL [N_ALLOW=400] [SEED=20261025]
import json, os, random, sys, collections
d, synth, out = sys.argv[1:4]
n_allow = int(sys.argv[4]) if len(sys.argv) > 4 else 400
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 20261025
rd = lambda f: [json.loads(l) for l in open(os.path.join(d, f))]
cases = []
def mk(cid, group, tool, inp, prompt, label, weight=1.0, **kw):
    c = dict(cid=cid, group=group, tool=tool, input=inp, prompt=(prompt or "")[:1500], label=label, weight=weight)
    c.update(kw)
    cases.append(c)
refs = [r for r in rd("refusals.jsonl") if r["label"] == "refuse"]
for r in refs:
    mk("R-" + r["id"][-8:], "refusal", r["tool"], r["input"], r.get("prompt_context"), "refuse", 1.0,
       era=bool(r.get("recorded_decision_era")), session=r["session"], month=r["month"], reason=r.get("classifier_reason"))
# pairs: refusal -> first next same-tool call with a recorded classifier allow
ids = set()
pairs = rd("retry_pairs.jsonl")
for p in pairs:
    for n in p["next_same_tool"]:
        if n["decider"] == "classifier_allow":
            ids.add(n["id"]); break
allowed_full = {}
with open(os.path.join(d, "classified.jsonl")) as f:
    for l in f:
        if '"classifier_allow"' not in l:
            continue
        j = json.loads(l)
        if j["id"] in ids:
            allowed_full[j["id"]] = j
npair = 0
for p in pairs:
    for n in p["next_same_tool"]:
        if n["decider"] == "classifier_allow":
            a = allowed_full[n["id"]]
            pid = "P%02d" % npair; npair += 1
            mk(pid + "-block", "pair_block", p["block"]["tool"], next(r["input"] for r in refs if r["id"] == p["block"]["id"]),
               next(r.get("prompt_context") for r in refs if r["id"] == p["block"]["id"]), "refuse", 1.0, pair=pid, ref_id="R-" + p["block"]["id"][-8:])
            mk(pid + "-allow", "pair_allow", a["tool"], a["input"], a.get("prompt_context"), "allow", 1.0, pair=pid)
            break
# synthetic
for s in json.load(open(synth))["cases"]:
    mk("S-" + s["id"], "synthetic", s["tool"], s["input"], s["user_task"], "refuse" if s["expected"] == "refuse" else "allow", 1.0,
       family=s["family"], pair=s.get("pair_id"))
# allows: stratified subsample of the stratified sample
al = rd("allowed_sample.jsonl")
by = collections.defaultdict(list)
for r in al:
    by[r["stratum"]].append(r)
rng = random.Random(seed)
tot = len(al)
frac = n_allow / tot
for st, rows in sorted(by.items()):
    m = min(len(rows), max(2, round(len(rows) * frac)))
    pick = rng.sample(rows, m)
    for r in pick:
        mk("A-" + r["id"][-8:], "allow", r["tool"], r["input"], r.get("prompt_context"), "allow", r["N_h"] / m,
           stratum=st, N_h=r["N_h"], m_h=m, session=r["session"], source=r["source"], risky=r["risky"])
with open(out, "w") as f:
    for c in cases:
        f.write(json.dumps(c) + "\n")
print(collections.Counter(c["group"] for c in cases), "sum weights allow", sum(c["weight"] for c in cases if c["group"] == "allow"))
