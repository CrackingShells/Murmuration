# w09-c8: compares a fresh llama-server re-run of qwen3.6 full rules on a case subset (w09i_judge.py rows) with explorer-w09-i's stored rows: verdict agreement and score difference per case; prints markdown, no case text. Usage: python3 -I w09c8_spotcheck.py STORED_ROWS FRESH_ROWS
import sys, json, math
def ld(p): return {r["cid"]: r for r in map(json.loads, open(p)) if "cid" in r}
A, B = ld(sys.argv[1]), ld(sys.argv[2])
ids = [c for c in B if c in A]
same = sum(A[c]["verdict"] == B[c]["verdict"] for c in ids)
d = [abs(float(A[c]["score"]) - float(B[c]["score"])) for c in ids]
grp = lambda g: [c for c in ids if A[c]["group"] == g]
print(f"cases {len(ids)} (refusals {len(grp('refusal'))}, allows {len(grp('allow'))}); verdicts equal {same} of {len(ids)}")
sd=[float(B[c]["score"])-float(A[c]["score"]) for c in ids]; import statistics as st; print(f"signed difference (fresh minus stored): mean {st.mean(sd):+.3f}, sd {st.pstdev(sd):.3f}")
d.sort(); print(f"abs score difference: median {d[len(d)//2]:.3f}, max {d[-1]:.3f}")
for c in ids:
    if A[c]["verdict"] != B[c]["verdict"]: print("verdict differs:", c, A[c]["verdict"], B[c]["verdict"], round(float(A[c]["score"]), 2), round(float(B[c]["score"]), 2))
big = [(round(abs(float(A[c]["score"]) - float(B[c]["score"])), 2), c) for c in ids if abs(float(A[c]["score"]) - float(B[c]["score"])) > 0.25]
print("score differences above 0.25:", big)
ms = sorted(B[c]["ms"] for c in ids if B[c]["ms"] > 0); print(f"fresh latency: first call {B[min(B, key=lambda c: B[c]['idx'])]['ms']/1000:.1f} s (cold cache), later median {ms[len(ms)//2]/1000:.2f} s, max {ms[-1]/1000:.2f} s")
