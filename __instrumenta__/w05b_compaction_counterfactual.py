#!/usr/bin/env python3
# Estimates, from a <label>_requests.tsv written by w05b_pi_context_cost.py, how much cache-read cost a compaction at context size X tokens would have saved (compaction modelled as one read of the full context, SUMMARY_OUT output tokens, and a rewrite of AFTER tokens at the 1 h write price); prints savings as a share of the session's list-price total, for several X. Usage: w05b_compaction_counterfactual.py REQUESTS_TSV [AFTER=91500] [SUMMARY_OUT=15000]
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
AFTER = int(sys.argv[2]) if len(sys.argv) > 2 else 91500
SUMOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 15000
CR, CW, OUT, IN = 0.20, 8.0, 20.0, 4.0
ctx = [int(r["ctx"]) for r in rows]; cr = [int(r["cache_read"]) for r in rows]
total = sum(float(r["cost_usd_list"]) for r in rows)
print("requests %d, max ctx %d, mean ctx %d, list-price total (share base) %.2f" % (len(rows), max(ctx), sum(ctx) // len(ctx), total))
for X in (150000, 200000, 300000, 400000):
    R = 0; events = 0; saved = 0.0; cost_ev = 0.0
    for i in range(len(rows)):
        if i > 0 and ctx[i] < 0.6 * ctx[i - 1]:
            R = 0  # a real compaction or restart happened; the simulation starts over
        if ctx[i] - R > X and i > 0 and cr[i] > 0:
            # compact before this request: one read of the current simulated context, a summary, a rewrite of AFTER tokens
            cur = ctx[i] - R
            cost_ev += (cur * CR + SUMOUT * OUT + AFTER * CW) / 1e6
            R = ctx[i] - AFTER
            events += 1
        if cr[i] > 0:
            saved += min(R, cr[i]) * CR / 1e6
    print("X=%d: %d compactions; cache-read cost avoided %.1f%% of total; compaction cost %.1f%%; net %.1f%% of the session's list-price total" % (X, events, 100 * saved / total, 100 * cost_ev / total, 100 * (saved - cost_ev) / total))
