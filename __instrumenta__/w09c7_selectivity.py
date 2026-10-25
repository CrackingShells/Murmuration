# w09-c7: prints, for each short-criterion judge of explorer-w09-c, the share of auto mode's refusals it blocks and the share of auto mode's natural (non-arena) classifier-allows it blocks, with n and Clopper-Pearson intervals on the raw counts, plus the character length of each judge's criterion wording; from the private cases.jsonl and the committed result rows. Usage: python3 -I w09c7_selectivity.py CASES_JSONL RESULTS_DIR
import sys, json, os
from math import comb
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w09c_judge as J
cases = {}
for l in open(sys.argv[1]):
    c = json.loads(l); cases[c["cid"]] = c
def cp(k, n, a=.05):
    cdf = lambda x, p: sum(comb(n, i) * p**i * (1-p)**(n-i) for i in range(x+1))
    lo = 0.0; hi = 1.0
    if k > 0:
        l, h = 0.0, 1.0
        for _ in range(60):
            m = (l+h)/2
            if 1 - cdf(k-1, m) > a/2: h = m
            else: l = m
        lo = (l+h)/2
    if k < n:
        l, h = 0.0, 1.0
        for _ in range(60):
            m = (l+h)/2
            if cdf(k, m) > a/2: l = m
            else: h = m
        hi = (l+h)/2
    return lo, hi
print("criterion wording lengths (characters): safeguard SHORT (system prompt, has an ALLOW clause) =", len(J.SHORT), "; Granite GRANITE_SHORT (criterion in Granite's template, no ALLOW clause) =", len(J.GRANITE_SHORT))
print("| judge | refusals blocked | 95% CP | natural allows blocked (raw) | 95% CP | arena allows blocked (raw) |")
print("|:--|--:|:--|--:|:--|--:|")
for name, f in (("granite-guardian-4.1-8b", "granite_short.jsonl"), ("gpt-oss-safeguard-20b", "safeguard_short.jsonl")):
    v = {r["cid"]: r["verdict"] == "block" for r in map(json.loads, open(os.path.join(sys.argv[2], f))) if "cid" in r}
    ref = [v[c] for c in v if cases[c]["group"] == "refusal"]
    nat = [v[c] for c in v if cases[c]["group"] == "allow" and cases[c]["source"] == "natural"]
    ar = [v[c] for c in v if cases[c]["group"] == "allow" and cases[c]["source"] == "arena"]
    a = cp(sum(ref), len(ref)); b = cp(sum(nat), len(nat))
    print(f"| {name} | {sum(ref)} of {len(ref)} = {100*sum(ref)/len(ref):.1f}% | {100*a[0]:.1f} to {100*a[1]:.1f}% | {sum(nat)} of {len(nat)} = {100*sum(nat)/len(nat):.1f}% | {100*b[0]:.1f} to {100*b[1]:.1f}% | {sum(ar)} of {len(ar)} |")
