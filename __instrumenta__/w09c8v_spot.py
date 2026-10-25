# w09-c8 verifier: compares stored qwen36_full scores with the author's 45-case re-run (verdict equality, score difference sd/max), the paired AUC qwen full vs qwen short and gemma, and a Gaussian-noise TPR at 10% weighted FPR; no case text. Usage: python3 -I w09c8v_spot.py CASES_JSONL ROWS_DIR SPOT_JSONL
import json, sys, os, collections
import numpy as np
cases = {}
for l in open(sys.argv[1]):
    c = json.loads(l); cases[c["cid"]] = c
RD = sys.argv[2]
def rows(p):
    R = {}
    for l in open(p):
        r = json.loads(l)
        if "cid" in r: R[r["cid"]] = r
    return R
Q = rows(os.path.join(RD, "qwen36_full.jsonl")); S = rows(sys.argv[3])
ids = [c for c in S if c in Q]
d = np.array([S[c]["score"] - Q[c]["score"] for c in ids])
print("spot n", len(S), "matched", len(ids), "verdict equal", sum(S[c]["verdict"] == Q[c]["verdict"] for c in ids), "diff mean", d.mean().round(3), "sd", d.std(ddof=1).round(3), "max|d|", np.abs(d).max().round(2), "n>0.25", int((np.abs(d) > .25).sum()))
print("labels in spot", collections.Counter(cases[c]["label"] for c in ids), "by label sd", {l: np.std([S[c]["score"] - Q[c]["score"] for c in ids if cases[c]["label"] == l], ddof=1).round(3) for l in ("refuse", "allow")})
print("block-prob mass (pb+pa) of cases with |d|>0.5:", [round(S[c]["pb"] + S[c]["pa"], 3) for c in ids if abs(S[c]["score"] - Q[c]["score"]) > .5])
pos = [c for c, v in cases.items() if v["group"] == "refusal"]
neg = [c for c, v in cases.items() if v["group"] == "allow" and v["source"] == "natural"]
w = np.array([float(cases[c]["weight"]) for c in neg])
def auc(sp, sn, wn):
    M = (sp[:, None] > sn[None, :]) + 0.5 * (sp[:, None] == sn[None, :]); return float((M * wn[None, :]).sum() / (len(sp) * wn.sum()))
sess = sorted({cases[c]["session"] for c in pos + neg})
out = {}
for nm in ("qwen36_full", "qwen36_short", "gemma4_short", "gemma4_full", "granite_short_scored"):
    R = rows(os.path.join(RD, nm + ".jsonl")); f = lambda c: float("nan") if R[c]["score"] is None else float(R[c]["score"]); out[nm] = (np.array([f(c) for c in pos]), np.array([f(c) for c in neg]))
    print(nm, "AUC", round(auc(*out[nm], w), 3), "nonfinite", int(np.sum(~np.isfinite(np.concatenate(out[nm])))))
ip = collections.defaultdict(list); inn = collections.defaultdict(list)
for i, c in enumerate(pos): ip[cases[c]["session"]].append(i)
for i, c in enumerate(neg): inn[cases[c]["session"]].append(i)
rng = np.random.default_rng(4242)
for a, b in (("qwen36_full", "qwen36_short"), ("qwen36_full", "gemma4_short"), ("qwen36_full", "granite_short_scored")):
    ds = []
    for _ in range(2000):
        ch = rng.integers(0, len(sess), len(sess))
        P = [i for k in ch for i in ip.get(sess[k], [])]; N = [i for k in ch for i in inn.get(sess[k], [])]
        if P and N: ds.append(auc(out[a][0][P], out[a][1][N], w[N]) - auc(out[b][0][P], out[b][1][N], w[N]))
    print(a, "minus", b, round(auc(*out[a], w) - auc(*out[b], w), 3), np.round(np.percentile(ds, [2.5, 97.5]), 3), "share>0", np.mean(np.array(ds) > 0))
# noise TPR at in-sample 10% FPR, sd 0.284, and binomial CI for 31/67
qp, qn = out["qwen36_full"]; W = w.sum(); r = np.random.default_rng(5)
t = []
for _ in range(500):
    p = qp + r.normal(0, .284, len(qp)); n = qn + r.normal(0, .284, len(qn)); best = np.inf
    for th in np.unique(np.concatenate([p, n]))[::-1]:
        if w[n >= th].sum() / W <= .10: best = th
        else: break
    t.append((p >= best).mean())
print("noise TPR mean", np.mean(t).round(3), np.round(np.percentile(t, [2.5, 97.5]), 3))
from math import comb
def cp(k, n, a=.025):
    lo = 0; hi = 1
    f = lambda p, k: sum(comb(n, i) * p**i * (1-p)**(n-i) for i in range(k, n+1))
    a_, b_ = 0.0, k / n
    for _ in range(60):
        m = (a_ + b_) / 2
        if f(m, k) < a: a_ = m
        else: b_ = m
    lo = (a_ + b_) / 2
    a_, b_ = k / n, 1.0
    for _ in range(60):
        m = (a_ + b_) / 2
        if 1 - f(m, k + 1) > a: a_ = m  # P(X<=k) > a  -> increase p
        else: b_ = m
    return lo, (a_ + b_) / 2
print("CP 31/67", cp(31, 67), "45/67", cp(45, 67))
