# Re-derives the e3 sign counts and medians (Python minus Rust, wall and CPU, per payload and pooled) from the author's raw pair rows, and the e4 per-pair differences from the author's session rows, with its own code.
# inputs: e3*_budget|handback.jsonl and e4_rows.jsonl in the author's report folder; outputs: tables on stdout.
import json, statistics, sys, collections, os
d = sys.argv[1]
for f in ["e3_budget", "e3b_budget", "e3_handback", "e3b_handback"]:
    rows = [json.loads(l) for l in open(os.path.join(d, f + ".jsonl"))]
    g = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in rows:
        g[os.path.basename(r["payload"])][r["round"]][r["arm"]] = r
    tw = tc = tn = 0
    for p, rs in sorted(g.items()):
        dw = [(x["py"]["wall_ns"] - x["rs"]["wall_ns"]) / 1e6 for x in rs.values() if len(x) == 2]
        dc = [(x["py"]["user_us"] + x["py"]["sys_us"] - x["rs"]["user_us"] - x["rs"]["sys_us"]) / 1e3 for x in rs.values() if len(x) == 2]
        s = sorted(dw)
        print("%-12s %-14s n=%d wall med %.1f [p10 %.1f p90 %.1f] py>rs %d | cpu med %.1f py>rs %d" % (f, p, len(dw), statistics.median(dw), s[int(.1 * (len(s) - 1))], s[int(.9 * (len(s) - 1))], sum(v > 0 for v in dw), statistics.median(dc), sum(v > 0 for v in dc)))
        tw += sum(v > 0 for v in dw); tc += sum(v > 0 for v in dc); tn += len(dw)
    print("  pooled", f, tw, tc, "of", tn)
rows = [json.loads(l) for l in open(os.path.join(d, "e4_rows.jsonl"))]
by = collections.defaultdict(dict)
for r in rows:
    by[r["pair"]][r["arm"]] = r
for ev in ["PostToolUse:Bash", "PostToolBatch", "PreToolUse:Bash"]:
    diffs = []
    for p, x in sorted(by.items()):
        if "A" in x and "B" in x and not x["A"]["is_error"] and not x["B"]["is_error"] and x["A"]["ms"].get(ev) and x["B"]["ms"].get(ev):
            diffs.append(statistics.median(x["A"]["ms"][ev]) - statistics.median(x["B"]["ms"][ev]))
    print(ev, "pairs", len(diffs), "med A-B %.1f" % statistics.median(diffs), "min %.1f max %.1f" % (min(diffs), max(diffs)), "B lower in", sum(v > 0 for v in diffs))
