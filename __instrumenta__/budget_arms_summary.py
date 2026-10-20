#!/usr/bin/env python3
"""Summarizes results_all_runs.tsv (from budget_arms_analyze.py) by run set and arm: runs with denies, report present, median fractions, overshoot, items, items per USD, stops short; writes summary_by_arm.tsv next to it.
usage: budget_arms_summary.py <derived dir>. Stdlib only."""
import csv, os, statistics as st, sys
D = sys.argv[1]
rows = list(csv.DictReader(open(os.path.join(D, "results_all_runs.tsv")), delimiter="\t"))
def setof(c):
    return "pilot" if c.startswith("pilot") else "E1E2-capped" if c[:3] in ("e1-", "e2-") else "E1E2-uncapped" if c.startswith("u-") else "X-capped" if c.startswith("x-") else "X-uncapped"
def num(r, k):
    try:
        return float(r[k])
    except ValueError:
        return None
cols = ["set", "arm", "n", "runs_with_deny", "report_present", "report_in_shape", "median_frac_first", "median_frac_final", "median_overshoot", "items_done", "items_correct", "median_items_per_usd", "stopped_short", "n4_budget_reason", "usd_sum", "platform_budget_attachments_max"]
out = ["\t".join(cols)]
for s in ("pilot", "E1E2-capped", "E1E2-uncapped", "X-capped", "X-uncapped"):
    for arm in sorted({r["arm"] for r in rows if setof(r["cell"]) == s}):
        rs = [r for r in rows if setof(r["cell"]) == s and r["arm"] == arm]
        med = lambda k: (lambda v: round(st.median(v), 3) if v else "NA")([num(r, k) for r in rs if num(r, k) is not None])
        cost = {l.split("\t")[0]: float(l.split("\t")[4]) for l in open(os.path.join(D, "cost_per_run.tsv")).read().splitlines()[1:-1]}
        out.append("\t".join(map(str, [s, arm, len(rs), sum(int(r["denies"]) > 0 for r in rs), sum(r["report_present"] == "True" for r in rs), sum(r["report_shape"] == "True" for r in rs),
                                       med("frac_first"), med("frac_final"), med("overshoot"), "/".join(r["items_done"] for r in rs), "/".join(r["items_correct"] for r in rs), med("items_per_usd"),
                                       sum(r["stopped_short"] == "True" for r in rs), sum(r["n4_budget_reason_for_stopping"] == "True" for r in rs), round(sum(cost[r["cell"]] for r in rs), 3),
                                       max(int(r["platform_budget_attachments"]) for r in rs)])))
open(os.path.join(D, "summary_by_arm.tsv"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
