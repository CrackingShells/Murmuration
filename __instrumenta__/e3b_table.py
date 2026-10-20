# merges the measured E3b runs (e3_measure.py output for the 429-script lab and for the first 336-script set) with my coding of reuse, evaluates E3b's decision rule, and writes the derived table; input: the run root, output folder; output: e3b_runs_table.tsv/.json and the rule evaluation on stdout
"""usage: python3 -I e3b_table.py RUNROOT OUTDIR

Reads RUNROOT/e3b_measure.json (arm P and Q, 429 scripts, the runs the rule uses) and RUNROOT/e3b_v0_measure.json (first set, 336 scripts, where
`ls -1` was 2.45 times one colgrep result, below the pre-registered 3: reported, not used by the rule), plus RUNROOT/e3b_search_probe.json.
CODING is my reading of each run (new files read against the near-fit script): t1 runs ran the fit script as is (some also wrote a cross-check
script of another algorithm, which is not a duplicate); t2 runs wrote new code after reading the first lines of a Collatz neighbour
(`collatz_trajectory_print.py` or `collatz_*.py`), none opened the near fit `collatz_longest_stopping_time.py` and none adapted it.
Stdlib only.
"""
import json
import os
import statistics as st
import sys

root, out = sys.argv[1:3]
rows = []
for name, setname in (("e3b_measure", "429 scripts (rule)"), ("e3b_v0_measure", "336 scripts (precondition not met)")):
    for r in json.load(open(os.path.join(root, name + ".json"))):
        task = r["task"]
        rows.append({"set": setname, "id": r["id"], "arm": "P" if r["id"][0] == "p" else "Q", "task": task, "kind": "fit" if task == "t1" else "near fit",
                     "s1_search_before_script": r["searched_before_script"], "s2_reuse": "reuse_as_is" if task == "t1" else "new_after_seeing_header",
                     "s3_search_call_result_chars": r["search_result_chars"], "s4_total_cost_usd": round(r["total_cost_usd"], 4),
                     "s5_methods": "+".join(r["s5_methods"]), "colgrep_calls": sum(k.startswith("colgrep") for k in r["search_kinds"]),
                     "s6_overwritten_unrelated": len(r["s6_overwritten_unrelated"]), "new_files": len(r["new_files"]), "tool_errors": "+".join(r["tool_errors"])})
json.dump(rows, open(os.path.join(out, "e3b_runs_table.json"), "w"), indent=1)
with open(os.path.join(out, "e3b_runs_table.tsv"), "w") as fh:
    fh.write("\t".join(rows[0]) + "\n")
    for r in rows:
        fh.write("\t".join(str(v) for v in r.values()) + "\n")
probe = json.load(open(os.path.join(root, "e3b_search_probe.json"))) if os.path.exists(os.path.join(root, "e3b_search_probe.json")) else {}
for setname in ("429 scripts (rule)", "336 scripts (precondition not met)"):
    print("==", setname)
    for arm in "PQ":
        s = [r for r in rows if r["set"] == setname and r["arm"] == arm]
        print(arm, "n", len(s), "s1", sum(r["s1_search_before_script"] for r in s), "strict reuse", sum(r["s2_reuse"] == "reuse_as_is" for r in s),
              "colgrep runs", sum(r["colgrep_calls"] > 0 for r in s), "overwrites", sum(r["s6_overwritten_unrelated"] for r in s),
              "median s3", st.median(r["s3_search_call_result_chars"] for r in s), "cost", round(sum(r["s4_total_cost_usd"] for r in s), 3))
print(probe)
