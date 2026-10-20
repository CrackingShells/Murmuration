# turns the measured E3c runs (e3_measure.py output) and my coding of each run's reuse into the derived table and evaluates E3c's rule; input: e3c_measure.json, output folder; output: e3c_runs_table.tsv/.json and the counts on stdout
"""usage: python3 -I e3c_table.py E3C_MEASURE_JSON OUTDIR

CODING (my reading of each run, new files diffed against the target): t1 runs opened and ran the target and used its output as is
(pt1r1 also wrote a cross-check of another algorithm); pt2r2 opened the near fit and wrote a new file that reuses its cache loop (adapted by
copy); pt2r1 and pt2r3 never opened the near fit and wrote new code after reading the head of other Collatz scripts.  Stdlib only.
"""
import json
import os
import statistics as st
import sys

CODING = {"pt1r1": "reuse_as_is", "pt1r2": "reuse_as_is", "pt1r3": "reuse_as_is", "pt2r1": "new_target_not_found", "pt2r2": "adapted_by_copy", "pt2r3": "new_target_not_found"}
rows = []
for r in json.load(open(sys.argv[1])):
    rows.append({"id": r["id"], "task": r["task"], "kind": "fit" if r["task"] == "t1" else "near fit", "s1_search_before_script": r["searched_before_script"],
                 "s2_reuse": CODING[r["id"]], "s3_search_call_result_chars": r["search_result_chars"], "s4_total_cost_usd": round(r["total_cost_usd"], 4),
                 "s5_methods": "+".join(r["s5_methods"]), "colgrep_calls": sum(k.startswith("colgrep") for k in r["search_kinds"]),
                 "s6_overwritten_unrelated": len(r["s6_overwritten_unrelated"]), "s7_target_found": r["s7_target_found"], "s7_how": "+".join(r["s7_how"])})
json.dump(rows, open(os.path.join(sys.argv[2], "e3c_runs_table.json"), "w"), indent=1)
with open(os.path.join(sys.argv[2], "e3c_runs_table.tsv"), "w") as fh:
    fh.write("\t".join(rows[0]) + "\n")
    for r in rows:
        fh.write("\t".join(str(v) for v in r.values()) + "\n")
print("n", len(rows), "s1", sum(r["s1_search_before_script"] for r in rows), "s7", sum(r["s7_target_found"] for r in rows),
      "by task", {t: sum(r["s7_target_found"] for r in rows if r["task"] == t) for t in ("t1", "t2")}, "colgrep runs", sum(r["colgrep_calls"] > 0 for r in rows),
      "overwrites", sum(r["s6_overwritten_unrelated"] for r in rows), "median s3", st.median(r["s3_search_call_result_chars"] for r in rows),
      "cost", round(sum(r["s4_total_cost_usd"] for r in rows), 3))
