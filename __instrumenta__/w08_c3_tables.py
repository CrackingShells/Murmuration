# Aggregates the per-run tsv of w08_c3_score.py (one row per run) into the arm table of the w08-c3 report on stdout (markdown): items correct, summary content, re-reads, compaction numbers, spend, per model and arm.
"""usage: w08_c3_tables.py RUNS_SCORED.tsv"""
import csv, statistics, sys
rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
f = lambda x: float(x) if x not in ("-", "") else None
print("| model | arm | runs | Q1 strict | Q1 lenient | Q2 | Q3 | Q4 | Q5 | re-read calls (mean) | re-read tokens (per run) | summary holds sentence / names / next / labels / q5 | compaction request USD | context before -> after | next request writes | total USD at Opus list (mean) | context at the end (mean) |")
print("|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|:--|:--|--:|:--|--:|--:|--:|")
for model in ("opus", "haiku"):
    for arm in ("C", "B0", "B1", "H"):
        rs = [r for r in rows if r["model"] == model and r["arm"] == arm]
        if not rs: continue
        s = lambda k: "%d/%d" % (sum(int(r[k]) for r in rs if r[k] != "-"), len(rs))
        rr = "; ".join(str(r["reread_tok"]) for r in rs)
        sm = "; ".join("%s/%s/%s/%s/%s" % tuple(r[k] for k in ("s_sentence", "s_names", "s_next", "s_labels", "s_q5")) for r in rs) if arm != "C" else "-"
        cu = [f(r["comp_usd"]) for r in rs if f(r["pre"])]
        pre = [f(r["pre"]) for r in rs if f(r["pre"])]; post = [f(r["post"]) for r in rs if f(r["post"])]; nw = [f(r["next_write"]) for r in rs if f(r["next_write"])]
        print("| %s | %s | %d | %s | %s | %s | %s | %s | %s | %.1f | %s | %s | %s | %s | %s | %.2f | %d |" % (
            model, arm, len(rs), s("q1"), s("q1_lenient"), s("q2"), s("q3"), s("q4"), s("q5"), statistics.mean(float(r["reread_calls"]) for r in rs), rr, sm,
            "%.3f" % statistics.mean(cu) if cu else "-", "%d -> %d" % (statistics.mean(pre), statistics.mean(post)) if pre else "-", "%d" % statistics.mean(nw) if nw else "-",
            statistics.mean(float(r["total_usd_opus55"]) for r in rs), statistics.mean(float(r["ctx_last"]) for r in rs)))
