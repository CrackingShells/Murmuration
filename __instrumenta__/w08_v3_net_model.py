# Re-derives the compaction net (USD over the six PI sessions) from explorer-w08-d's per-request tables s1..s6 with my own loop: threshold T, summary output OUT, re-read R, floor S; prints net for the cells claimed in w08-c3. Inputs: requests dir; output: stdout.
import csv, glob, os, sys
D = sys.argv[1]
S6 = []
for f in sorted(glob.glob(os.path.join(D, "s?_*_requests.tsv"))):
    if os.path.basename(f).startswith("s4b"): continue
    S6.append([(int(r["ctx"]), int(r["cr"]), int(r["reset"])) for r in csv.DictReader(open(f), delimiter="\t")])
def net(T, OUT, R, S=91500, per_session=False):
    tot = []
    for rq in S6:
        drop = 0.0; sav = cost = 0.0; n = 0
        for k, (ctx, cr, reset) in enumerate(rq):
            if reset: drop = 0.0; continue
            prevc = rq[k-1][0] if k else 0
            miss = k > 0 and cr < 0.5 * prevc
            price = 8.0 if miss else 0.2                    # a request that missed the cache rewrites its dropped tokens at 1h price
            sav += drop * price / 1e6
            c = ctx - drop; prev = max(0.0, prevc - drop)
            if c > T:
                gap = max(0.0, c - prev)
                cost += (prev * price + (gap + 1800) * 4.0 + OUT * 20.0 + 41000 * 8.0 + R * 8.0) / 1e6
                drop += c - (S + R); n += 1
        tot.append((sav, cost, n))
    s = sum(t[0] for t in tot); c = sum(t[1] for t in tot); n = sum(t[2] for t in tot)
    return s, c, n
for T, OUT, R in [(250000, 3000, 2500), (250000, 3000, 10000), (250000, 3000, 20000), (250000, 3000, 45000), (250000, 6000, 45000), (250000, 3000, 0), (150000, 3000, 2500)]:
    s, c, n = net(T, OUT, R); print("T=%d OUT=%d R=%d  compactions=%d saved=%.2f cost=%.2f net=%.2f" % (T, OUT, R, n, s, c, s - c))
