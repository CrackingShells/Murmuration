# w09-i: from the private cases.jsonl and w09i / w09c result rows, prints where qwen3.6 (full rules) errs: misses by tool and by recorded refusal reason, natural-allow blocks by stratum flag (risky/plain) and by tool, and how many of the 67 refusals each judge allows (overlap, all-allow set). No case text. Usage: python3 -I w09i_slices.py CASES_JSONL QWEN_FULL_JSONL [OTHER_JSONL name ...]
import sys, json, collections
cases = {}
for l in open(sys.argv[1]):
    c = json.loads(l); cases[c["cid"]] = c
def load(f):
    return {r["cid"]: r["verdict"] == "block" for r in map(json.loads, open(f)) if "cid" in r}
Q = load(sys.argv[2])
ref = [c for c in Q if cases.get(c, {}).get("group") == "refusal"]
nat = [c for c in Q if cases.get(c, {}).get("group") == "allow" and cases[c]["source"] == "natural"]
print("qwen full, refusals missed by tool:")
t = collections.defaultdict(lambda: [0, 0])
for c in ref: t[cases[c]["tool"]][0] += 1; t[cases[c]["tool"]][1] += (not Q[c])
print({k: f"{v[1]} of {v[0]} missed" for k, v in t.items()})
print("by recorded refusal reason (the classifier's category label):")
t = collections.defaultdict(lambda: [0, 0])
for c in ref: t[cases[c].get("reason") or "?"][0] += 1; t[cases[c].get("reason") or "?"][1] += (not Q[c])
for k, v in sorted(t.items(), key=lambda kv: -kv[1][0]): print(f"  {k}: {v[1]} of {v[0]} missed")
print("era (recorded era vs before):")
for e in ("True", "False"):
    s = [c for c in ref if str(cases[c].get("era")) == e]; print(f"  era={e}: {sum(not Q[c] for c in s)} of {len(s)} missed")
print("natural allows blocked by risky flag (raw n, weighted share within flag):")
for fl in ("True", "False"):
    s = [c for c in nat if str(cases[c].get("risky")) == fl]
    w = sum(float(cases[c]["weight"]) for c in s)
    print(f"  risky={fl}: {sum(Q[c] for c in s)} of {len(s)}; weighted {100*sum(float(cases[c]['weight'])*Q[c] for c in s)/w:.1f}% (weight {w:.0f})")
print("natural allows blocked by tool (raw):")
t = collections.defaultdict(lambda: [0, 0])
for c in nat: t[cases[c]["tool"]][0] += 1; t[cases[c]["tool"]][1] += Q[c]
print({k: f"{v[1]} of {v[0]}" for k, v in t.items()})
args = sys.argv[3:]
print("overlap of misses on the 67 refusals (judge allows the refusal):")
miss = {"qwen36_full": {c for c in ref if not Q[c]}}
for i in range(0, len(args), 2):
    R = load(args[i]); miss[args[i+1]] = {c for c in ref if c in R and not R[c]}
    print(f"  {args[i+1]}: {len(miss[args[i+1]])} missed of {sum(c in R for c in ref)} scored")
print("  qwen36_full:", len(miss["qwen36_full"]))
allm = set.intersection(*miss.values()) if len(miss) > 1 else set()
print("refusals allowed by ALL listed judges:", len(allm), sorted(allm))
print("refusals allowed by qwen36_full and every other:", {k: len(miss["qwen36_full"] & v) for k, v in miss.items()})
