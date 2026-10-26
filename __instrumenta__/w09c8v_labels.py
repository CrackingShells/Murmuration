# w09-c8 verifier: checks that the 67 refusal and 212 natural-allow cases of cases.jsonl carry auto mode's recorded decision (classifier_block / classifier_allow) in classified.jsonl, by tool-use id suffix, session and tool; prints counts only (no case text). Usage: python3 -I w09c8v_labels.py SET_DIR
import json, sys, collections, os
D = sys.argv[1]
cases = [json.loads(l) for l in open(os.path.join(D, "cases.jsonl"))]
want = {}
for c in cases:
    if c["group"] == "refusal" or (c["group"] == "allow" and c.get("source") == "natural"):
        want[c["cid"][2:]] = c
print("wanted", len(want), collections.Counter(c["group"] for c in want.values()))
found = {}
for l in open(os.path.join(D, "classified.jsonl")):
    # cheap prefilter: id suffix
    i = l[l.find('"id"') if '"id"' in l[:20] else 0:]
    j = json.loads(l)
    s = j["id"][-8:]
    if s in want:
        found.setdefault(s, []).append(j)
ct = collections.Counter(); bad = []
for s, c in want.items():
    js = found.get(s, [])
    if len(js) != 1: ct[("nmatch", len(js))] += 1; continue
    j = js[0]
    ct[(c["group"], j["decider"], j["tool"] == c["tool"], j["session"] == c["session"], str(j.get("auto")), str(j.get("mode")))] += 1
for k, v in sorted(ct.items(), key=str): print(k, v)
# era: refusals with the allow label existing (recorded_decision_era)
