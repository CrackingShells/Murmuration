# w09c6 verifier: Granite-short blocked share of the allow cases by project group and by subagent flag, weighted by N_h/m_h over the cases in each cell (post-stratification within strata kept via the case weight); inputs cases.jsonl, allowed_sample.jsonl, granite_short.jsonl; prints a table. Usage: python3 -I w09c6v_cuts.py SET_DIR RESULTS_DIR
import json, sys, re, collections
D, R = sys.argv[1:3]
cases = {c["cid"]: c for c in map(json.loads, open(D + "/cases.jsonl")) if c["group"] == "allow"}
meta = {("A-" + json.loads(l)["id"][-8:]): json.loads(l) for l in open(D + "/allowed_sample.jsonl")}
g = {}
for l in open(R + "/granite_short.jsonl"):
    j = json.loads(l)
    if "cid" in j: g[j["cid"]] = j
def block(cid):
    m = re.findall(r"<score>\s*(.*?)\s*</score>", g[cid]["raw"], re.S)
    return m and m[0].strip().lower() == "yes"
cell = collections.defaultdict(lambda: [0, 0.0, 0.0])
for cid, c in cases.items():
    m = meta[cid]
    for key in (("source", m["source"]), ("pgroup", "lab" if m["project_group"] == "murmuration-lab" else ("arena" if m["source"] == "arena" else "other-natural")),
                ("sub", (m["source"], m["sub"])), ("risky", (m["source"], m["risky"])), ("tool", (m["source"], m["tool_family"]))):
        x = cell[key]; w = float(c["weight"]); x[0] += 1; x[1] += w; x[2] += w * bool(block(cid))
print("cell | n | population weight | weighted blocked share")
for k in sorted(cell, key=str):
    n, w, b = cell[k]; print(k, n, round(w), round(100 * b / w, 1))
