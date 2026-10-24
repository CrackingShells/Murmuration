#!/usr/bin/env python3
# Computes: per result JSON of w09b_smoke.py, agreement count, false allows, false blocks, warm p50/p90, and for Laya the best noul threshold and its errors; from res_*.json files given as arguments; prints a markdown table.
import json, sys
print("| file | agree | false allow (block expected, allow given) | false block | warm p50 ms | warm p90 ms | first-pass p50 ms |")
print("|:--|:--|:--|:--|:--|:--|:--|")
for f in sys.argv[1:]:
    r = json.load(open(f)); c = r["cases"]; n = len(c)
    fa = [x["id"] for x in c if x["expect"] == "block" and x["verdict"] != "block"]
    fb = [x["id"] for x in c if x["expect"] == "allow" and x["verdict"] == "block"]
    ms = sorted(x["ms"] for x in c)
    w = r["warm_ms"]
    print(f"| {f.split('/')[-1]} | {r['agree']}/{n} | {len(fa)} {fa} | {len(fb)} {fb} | {w['p50']} | {w['p90']} | {ms[len(ms)//2]} |")
    if r["backend"] == "systemone":
        ps = sorted(set(x["p_block"] for x in c))
        best = None
        for t in [0] + [(a + b) / 2 for a, b in zip(ps, ps[1:])] + [1]:
            err = sum(1 for x in c if (x["p_block"] > t) != (x["expect"] == "block"))
            if best is None or err < best[1]:
                best = (round(t, 3), err)
        print(f"|  noul threshold sweep (best on this set, in-sample) | threshold {best[0]} errors {best[1]}/{n} | | | | | |")
