# w09-c: from cases.jsonl and the result JSONLs of w09c_judge.py, lists per case the verdicts of every judge x arm and ranks the worst fits (refusals that every judge allowed, allows that every judge blocked, pairs both-blocked), printing only metadata by default (group, tool, category, stratum, weight); --text N also prints the first N chars of the input to the console (never commit that output). Usage: python3 -I w09c_worst.py CASES_JSONL [--text N] RESULT_JSONL...
import json, sys, collections
args = sys.argv[1:]
cases = {json.loads(l)["cid"]: json.loads(l) for l in open(args[0])}
args = args[1:]
text = 0
if args and args[0] == "--text":
    text = int(args[1]); args = args[2:]
V = {}
for f in args:
    key = None; rows = [json.loads(l) for l in open(f)]
    for r in rows:
        if "cid" in r:
            V.setdefault(f.split("/")[-1].replace(".jsonl", ""), {})[r["cid"]] = r["verdict"]
keys = sorted(V)
def line(cid):
    c = cases[cid]
    s = " ".join(f"{k}={V[k].get(cid, '-')}" for k in keys)
    t = ""
    if text:
        inp = c["input"] if isinstance(c["input"], str) else json.dumps(c["input"])
        t = " | " + inp[:text].replace("\n", " ")
    return f"{cid} {c['group']} {c['tool'][:30]} {c.get('reason') or c.get('family') or c.get('stratum')} w={c['weight']:.0f} :: {s}{t}"
print("== refusals judged allow by every judge that scored them")
for cid, c in cases.items():
    if c["group"] == "refusal":
        vs = [V[k][cid] for k in keys if cid in V[k]]
        if vs and all(x == "allow" for x in vs): print(line(cid))
print("== allows blocked by every judge that scored them, by weight")
al = []
for cid, c in cases.items():
    if c["group"] == "allow":
        vs = [V[k][cid] for k in keys if cid in V[k]]
        if len(vs) >= 2 and all(x == "block" for x in vs): al.append((c["weight"], cid))
for w, cid in sorted(al, reverse=True)[:15]: print(line(cid))
print("n allows blocked by all:", len(al))
