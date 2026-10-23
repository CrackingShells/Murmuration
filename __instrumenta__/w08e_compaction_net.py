# Recomputes explorer-w08-d's compaction lever from its per-request tables (s*_requests.tsv) with the compaction request priced as measured in w08e headless runs (cached prefix read + uncached tail at input price + summary output + 41k post-compaction write), a re-read allowance R and a thrash check; prints markdown tables on stdout.
"""usage: w08e_compaction_net.py REQUESTS_DIR   (REQUESTS_DIR = __reports__/wave-08/explorer-w08-d, holds s1_w1-3_requests.tsv ... s6_w8_requests.tsv)
Prices per million tokens, Opus 5.5 list (scripts/lab_status.py): read 0.20, write 1 h 8, uncached input 4, output 20.
Model per compaction, before request k whose context c_k (minus what earlier compactions dropped) exceeds the threshold T:
  cost = prev x (0.20, or 8 when the baseline request k missed the cache) + (g + 1,800) x 4 + OUT x 20 + 41,000 x 8 + R x 8
  prev = context of request k-1 after drops; g = c_k - prev (tokens not yet cached); 1,800 = summariser prompt (measured: uncached input minus step growth, 1.8-1.9k);
  41,000 = post-compaction write (measured 40.2k in w08e headless, 41,043 at the lab's real compaction); OUT = summary output; R = tokens the PI re-reads afterwards (written once, then carried).
  the context after is S + R (S = 91,500, the lab's real post-compaction context); every later request carries `drop` fewer tokens: saving drop x 0.20 (x 8 where the baseline request missed).
  savings start at request k+1 (request k's own read saving, at most USD 0.2 per compaction, is not counted).
`legacy` reproduces explorer-w08-d (cost = c x 0.20 + 8,000 x 20 + 41,000 x 8, no R)."""
import csv, glob, os, sys

D = sys.argv[1]
RD, W1, INP, OUT_P = 0.20, 8.0, 4.0, 20.0
SESS = {}
for f in sorted(glob.glob(os.path.join(D, "s?_*_requests.tsv"))):
    lab = os.path.basename(f).split("_requests")[0]
    if lab.startswith("s4b"): continue
    SESS[lab] = [dict(k=int(r["k"]), ctx=int(r["ctx"]), cr=int(r["cr"]), reset=int(r["reset"]), gap=float(r["gap_s"] or 0)) for r in csv.DictReader(open(f), delimiter="\t")]
TOT = 144.47

def simulate(rq, T, mode, OUT=6000, R=0, S=91500):
    drop = sav = cost = 0.0; nc = 0; thrash = 0; steps = []
    for r in rq:
        k = r["k"]
        if r["reset"]: drop = 0.0; continue
        prev_base = rq[k - 1]["ctx"] if k else 0
        miss = k > 0 and r["cr"] < 0.5 * prev_base
        sav += drop * (W1 if miss else RD) / 1e6
        ctx = r["ctx"] - drop; prev = max(0.0, prev_base - drop)
        if ctx > T:
            g = max(0.0, ctx - prev)
            if mode == "legacy":
                C = (ctx * RD + 8000 * OUT_P + 41000 * W1) / 1e6; after = S
            else:
                C = (prev * (W1 if miss else RD) + (g + 1800) * INP + OUT * OUT_P + 41000 * W1 + R * W1) / 1e6; after = S + R
            if mode != "legacy" and after + 3 * 12000 > T: thrash += 1
            cost += C; drop += ctx - after; nc += 1
    return sav, cost, nc, thrash

def run(T, mode, **kw):
    out = {}
    for lab, rq in SESS.items(): out[lab] = simulate(rq, T, mode, **kw)
    return out
def fmt(o):
    s = sum(v[0] for v in o.values()); c = sum(v[1] for v in o.values()); n = sum(v[2] for v in o.values()); th = sum(v[3] for v in o.values())
    return s, c, n, th

print("## check: legacy model (explorer-w08-d), R = 0, S = 91,500\n\n| threshold | compactions | saved | compaction cost | net | share of USD %.2f |\n|--:|--:|--:|--:|--:|--:|" % TOT)
for T in (200000, 300000):
    s, c, n, th = fmt(run(T, "legacy"))
    print("| %dk | %d | %.2f | %.2f | %.2f | %.1f%% |" % (T // 1000, n, s, c, s - c, 100 * (s - c) / TOT))
print("\n## refined model: net USD over the six PI sessions (s1-s6), threshold T, summary output OUT, re-read R after each compaction\n")
print("| threshold T | OUT | R re-read | compactions | saved on later requests | cost of compactions | net | share | per-session net (s1/s2/s3/s4/s5/s6) | thrash-prone compactions |\n|--:|--:|--:|--:|--:|--:|--:|--:|:--|--:|")
for T in (150000, 250000, 400000):
    for OUT in (6000, 8000):
        for R in (0, 10000, 45000, 90000):
            o = run(T, "new", OUT=OUT, R=R); s, c, n, th = fmt(o)
            per = "/".join("%.1f" % (v[0] - v[1]) for v in o.values())
            print("| %dk | %d | %dk | %d | %.2f | %.2f | %.2f | %.1f%% | %s | %d |" % (T // 1000, OUT, R // 1000, n, s, c, s - c, 100 * (s - c) / TOT, per, th))
print("\n## one compaction's cost by context size (hit, OUT 6,000, g 10,000, R 0 / 45,000)\n\n| context before | read of prev | uncached tail | output | post write | R=0 total | R=45k total |\n|--:|--:|--:|--:|--:|--:|--:|")
for ctx in (150000, 250000, 400000, 967000):
    a = (ctx - 10000) * RD / 1e6; b = 11800 * INP / 1e6; o = 6000 * OUT_P / 1e6; w = 41000 * W1 / 1e6
    print("| %dk | %.3f | %.3f | %.3f | %.3f | %.3f | %.3f |" % (ctx // 1000, a, b, o, w, a + b + o + w, a + b + o + w + 45000 * W1 / 1e6))
print("\n## sessions: requests, max context, requests above each threshold\n\n| session | requests | max context | >150k | >250k | >400k |\n|:--|--:|--:|--:|--:|--:|")
for lab, rq in SESS.items():
    print("| %s | %d | %d | %d | %d | %d |" % (lab, len(rq), max(r["ctx"] for r in rq), *[sum(1 for r in rq if r["ctx"] > T) for T in (150000, 250000, 400000)]))

print("\n## break-even re-read R per compaction (net = 0, OUT 6,000) and the thrash limit R_max = T - 91,500 - 36,000 (above it the context refills to T within 3 turns, the platform's breaker stops it)\n\n| threshold T | R_max | net at R_max | break-even R (or `none below R_max`) |\n|--:|--:|--:|:--|")
for T in (150000, 250000, 400000):
    Rmax = max(0, T - 91500 - 36000)
    def net(R): s_, c_, n_, th_ = fmt(run(T, "new", OUT=6000, R=R)); return s_ - c_
    be = "none below R_max"
    lo, hi = 0, Rmax
    if net(hi) <= 0 < net(lo):
        for _ in range(30):
            mid = (lo + hi) / 2
            if net(mid) > 0: lo = mid
            else: hi = mid
        be = "%.0fk" % (lo / 1000)
    print("| %dk | %dk | %.2f | %s |" % (T // 1000, Rmax // 1000, net(Rmax), be))
