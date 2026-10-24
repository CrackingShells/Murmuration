# w09-a: computes the ESTIMATE tables for agreement-interval sizes (Clopper-Pearson bounds on misses among n refusals, Wilson half-widths, n for a target half-width among allows with a design effect, days of traffic to collect refusals) from refusals.jsonl counts; prints markdown. Usage: python3 -I w09a_sample_size.py IN_DIR
import json, math, os, sys, collections
d = sys.argv[1]
ref = [json.loads(l) for l in open(os.path.join(d, "refusals.jsonl"))]
blk = [r for r in ref if r["label"] == "refuse"]
era = [r for r in blk if r["recorded_decision_era"]]
sess = len({r["session"] for r in blk})
def cdf(k, n, p):
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k + 1))
def cp_upper(k, n, a=0.05):  # one-sided (1-a) upper bound, exact
    if k >= n: return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if cdf(k, n, mid) > a: lo = mid
        else: hi = mid
    return hi
def cp_two(k, n):
    def lower(k, n):
        if k == 0: return 0.0
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if 1 - cdf(k - 1, n, mid) < 0.025: lo = mid
            else: hi = mid
        return lo
    return lower(k, n), cp_upper(k, n, 0.025)
def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h
print("refusals: %d (sessions %d); recorded-decision era (>= 2.1.293): %d" % (len(blk), sess, len(era)))
print("\n### A. false-allow side: local model allows what Anthropic refused (k misses of n refusals)\n")
print("| n refusals | k misses | point | exact 95% two-sided | Wilson 95% |")
print("|--:|--:|--:|:--|:--|")
for n in (len(era), len(blk)):
    for k in (0, 1, 3, 6, 10, 20):
        if k <= n:
            lo, hi = cp_two(k, n); wl, wh = wilson(k, n)
            print("| %d | %d | %.3f | %.3f-%.3f | %.3f-%.3f |" % (n, k, k / n, lo, hi, wl, wh))
print("\nrule of three, one-sided 95%%: k=0 of n=%d gives upper bound %.3f (exact %.3f)" % (len(blk), 3 / len(blk), cp_upper(0, len(blk))))
print("\n### B. refusals needed for a target half-width on the miss rate p (n = deff * z^2 p (1-p) / h^2, z = 1.96)\n")
print("| p | h = 0.10 | h = 0.05 | h = 0.025 |")
print("|--:|--:|--:|--:|")
for p in (0.05, 0.1, 0.2, 0.3):
    print("| %.2f | %s |" % (p, " | ".join("%d" % math.ceil(1.96**2 * p * (1 - p) / h**2) for h in (0.10, 0.05, 0.025))))
print("\n### C. allowed calls needed per estimate of the disagreement rate q among allows (local refuses what Anthropic allowed), n = deff * z^2 q (1-q) / h^2\n")
print("| q | h | deff 1 | deff 2 | deff 4 |")
print("|--:|--:|--:|--:|--:|")
for q, h in ((0.01, 0.005), (0.02, 0.01), (0.05, 0.02), (0.10, 0.03), (0.20, 0.05)):
    print("| %.2f | %.3f | %s |" % (q, h, " | ".join("%d" % math.ceil(f * 1.96**2 * q * (1 - q) / h**2) for f in (1, 2, 4))))
print("\n### D. what the skew means (population of recorded decisions)\n")
na, nb = 30511, len(era)
print("recorded era: %d classifier allows, %d classifier refusals: refusal share %.4f%%" % (na, nb, 100 * nb / (na + nb)))
print("accuracy of a model that allows everything: %.4f%%; its sensitivity: 0" % (100 * na / (na + nb)))
print("random allowed sample of n needed to see >= 1 more refusal-like item by chance at p=%.5f: n=%d (95%%)" % (nb / (na + nb), math.ceil(math.log(0.05) / math.log(1 - nb / (na + nb)))))
dates = sorted(r["ts"][:10] for r in era)
if dates:
    d0, d1 = dates[0], dates[-1]
    print("era refusals span %s to %s: %d refusals; observed rate about %.2f per day in this account" % (d0, d1, len(era), len(era) / max(1, (int(d1[8:]) - int(d0[8:]) + 1))))
