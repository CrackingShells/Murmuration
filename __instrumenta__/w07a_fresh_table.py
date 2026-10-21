"""Summarises first-run versus warm spawns of freshly built binaries: reads w07a_spawn_bench JSONL (rows in file order, case names bK_rJ for the J-th consecutive spawn of binary K, ctl_after_bK for a control spawn) and prints, per run index J, the median and p90 wall ms over binaries, the share of binaries whose first run exceeded their own later-run median by more than 3 ms, and the control median; usage: w07a_fresh_table.py rows.jsonl R."""
import json, sys, statistics as st, re
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
byj, ctl = {}, []
per = {}
for r in rows:
    m = re.match(r"b(\d+)_r(\d+)$", r["case"])
    if m: byj.setdefault(int(m.group(2)), []).append(r["wall_ns"] / 1e6); per.setdefault(int(m.group(1)), {})[int(m.group(2))] = r["wall_ns"] / 1e6
    elif r["case"].startswith("ctl"): ctl.append(r["wall_ns"] / 1e6)
q = lambda v, p: sorted(v)[min(len(v) - 1, int(p * len(v)))]
print("| run index (0 = first exec of a new binary) | n binaries | median ms | p90 ms | max ms |\n|--:|--:|--:|--:|--:|")
for j in sorted(byj): print("| %d | %d | %.2f | %.2f | %.2f |" % (j, len(byj[j]), st.median(byj[j]), q(byj[j], .9), max(byj[j])))
print("| control (known binary) | %d | %.2f | %.2f | %.2f |" % (len(ctl), st.median(ctl), q(ctl, .9), max(ctl)))
d = [v[0] - st.median([x for k, x in v.items() if k > 0]) for v in per.values() if 0 in v and len(v) > 1]
print("\nfirst run minus median of the same binary's later runs, ms: median %.2f, p10 %.2f, p90 %.2f, n=%d; first slower by >3 ms in %d of %d" % (st.median(d), q(d, .1), q(d, .9), len(d), sum(x > 3 for x in d), len(d)))
