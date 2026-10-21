# merges the measured per-run records of E3 (three JSON files from e3_measure.py) with the hand coding of each run's reuse, and writes the derived table and the decision counts; input: the run root with main_measure.json, s_measure.json, x_measure.json and the runs' lab folders, plus the two scripts folders; output: runs_table.tsv, runs_table.json and a summary on stdout
"""usage: python3 -I e3_table.py RUNROOT SCRIPTS SCRIPTS_OPAQUE OUTDIR

CODING is my reading of each run's tool-call sequence (the sequences are in the JSON; raw runs stay outside git).  Categories of `s2`:
  reuse_as_is        an existing script was run and its output used, nothing new written for the task
  reuse_in_place     an existing script was edited in place and run
  extension_by_copy  a new file adapted from an existing script of the family: its code reuses the existing body (checked by reading the files), written after the body had been read
  new_after_seeing_header  a new file written after the first lines of the existing scripts were seen, with its own code (not an adaptation; corrected after reproducer-w04-4)
  new_no_search      a new script, written after the only search call failed (Glob is absent in the headless session); the existing script was never seen
  overwrite          a new script written under the name of an unrelated existing script (see S-w04-author-w04-3-5)
A cross-check script of another algorithm, written beside a reuse_as_is run, is noted in `note` and is not a duplicate.
Arms: M = author as the main agent (`--agent murmuration:author`; no SubagentStart note), S = the research PI dispatches the author (the worker is a subagent and gets the start note),
X = arm M with opaque file names u01..u46, C = arm M with the paragraph on `__instrumenta__/` deleted from agents/author.md (both exploratory, outside the pre-registered rule).
"""
import json
import os
import sys

CODING = {
    "t1r1": ("reuse_as_is", ""), "t1r2": ("reuse_as_is", "plus an independent suffix-automaton cross-check script"), "t1r3": ("reuse_as_is", ""),
    "t2r1": ("extension_by_copy", "read 20 lines of collatz_*.py; new file, similarity 0.42"), "t2r2": ("extension_by_copy", "read 30 lines; similarity 0.75"),
    "t2r3": ("new_after_seeing_header", "read 5 lines; wrote a plain no-cache loop, also a C version; not an adaptation (reproducer-w04-4 diffed it)"),
    "t3r1": ("extension_by_copy", "read the fit script; generic-alphabet copy, similarity 0.44"), "t3r2": ("extension_by_copy", "read the fit script; k-ary copy, similarity 0.44"),
    "t3r3": ("reuse_in_place", "patched the fit script to take the alphabet from argv; the file now differs from the start"),
    "st1r1": ("reuse_as_is", ""), "st1r2": ("reuse_as_is", ""), "st1r3": ("reuse_as_is", ""),
    "st2r1": ("new_no_search", "Glob absent, one failed call, no second search; the new script is a fresh cache-loop of the near fit's function"),
    "st2r2": ("new_after_seeing_header", "read 5 lines of two scripts; wrote a plain no-cache loop; not an adaptation"),
    "st2r3": ("new_after_seeing_header", "loaded colgrep find_files by ToolSearch, never called it; ls then head -5; plain no-cache loop (its header says so); not an adaptation"),
    "ct1r1": ("reuse_as_is", "no agent-file paragraph; listed the folder in the second call, ran the fit script, added a suffix-check script"),
    "ct1r2": ("reuse_as_is", "no paragraph; ls -R, ran the fit script; added a cross-check script in the claim folder"),
    "ct1r3": ("new_no_search", "no paragraph; never looked at the folder; wrote its own brute force (duplicate of the fit script) in exp/"),
    "ct2r1": ("new_no_search", "no paragraph; never looked at the folder; wrote collatz_peak.py and .c into __instrumenta__/"),
    "ct2r2": ("new_no_search", "no paragraph; its only `ls __instrumenta__` was in the same call as the write; script placed in __instrumenta__/w04-c9/"),
    "ct2r3": ("new_no_search", "no paragraph; never looked at the folder; script in w04-c9/ outside __instrumenta__/"),
    "xt1r1": ("reuse_as_is", "found u03 by head -1 of all files; plus a cross-check u47"), "xt1r2": ("reuse_as_is", "found u03 by head -1 of all files"),
    "xt1r3": ("reuse_as_is", "found u03 by head -1 of all files; plus a cross-check"),
    "xt2r1": ("new_after_seeing_header", "colgrep search (limit 5, paths __instrumenta__) listed u09 and u08 first; new u47 is a plain no-cache loop, not an adaptation"),
    "xt2r2": ("overwrite", "ls cut by `head -30`, saw u01..u26, wrote the new script as u27.py: overwrote jsonl_field_counter.py; had seen the first lines of u08 and u09"),
    "xt2r3": ("new_after_seeing_header", "head -n1 of all, grep collatz; new collatz_peak.py, plain loop; read only first lines"),
}


def main(root, scripts, opaque, out):
    rows = []
    for arm, name, sc in (("M", "main_measure", scripts), ("S", "s_measure", scripts), ("X", "x_measure", opaque), ("C", "c_measure", scripts)):
        for r in json.load(open(os.path.join(root, name + ".json"))):
            if r["pilot"]:
                continue
            rid = r["id"]
            est = ""
            h = os.path.join(root, "runs", rid, "lab", "__statera__", "harness.jsonl")
            if arm == "S" and os.path.exists(h):
                ends = [json.loads(l) for l in open(h) if '"event": "end"' in l]
                est = round(sum(e["used"] for e in ends), 4)
            cat, note = CODING[rid]
            rows.append({"id": rid, "arm": arm, "task": r["task"], "kind": {"t1": "fit", "t2": "near fit", "t3": "near fit (of the fit script)"}[r["task"]],
                         "s1_search_before_script": r["searched_before_script"], "s1_first_search": r["first_search_kind"] or "none (failed Glob)" if r["first_search_kind"] is None and r["tool_errors"] else r["first_search_kind"],
                         "colgrep_calls": sum(1 for k in r["search_kinds"] if k.startswith("colgrep")), "s2_reuse": cat,
                         "new_files": len(r["new_files"]), "modified_starting_files": len(r["modified"]),
                         "s3_search_call_result_chars": r["search_result_chars"], "s3_baseline_ls_plus_first_lines_chars": r["baseline_chars"],
                         "s4_total_cost_usd": round(r["total_cost_usd"], 4), "worker_usd_estimate_from_harness": est, "tool_calls": r["tool_calls"], "note": note})
    json.dump(rows, open(os.path.join(out, "runs_table.json"), "w"), indent=1)
    cols = list(rows[0])
    with open(os.path.join(out, "runs_table.tsv"), "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")
    print("rows", len(rows), "total_cost_usd (non-pilot)", round(sum(r["s4_total_cost_usd"] for r in rows), 4))
    for arms in (("M",), ("S",), ("M", "S"), ("X",), ("C",)):
        sel = [r for r in rows if r["arm"] in arms]
        n = len(sel)
        s1 = sum(r["s1_search_before_script"] for r in sel)
        cats = {}
        for r in sel:
            cats[r["s2_reuse"]] = cats.get(r["s2_reuse"], 0) + 1
        print("arms", "+".join(arms), "n", n, "s1", s1, "cats", cats, "colgrep calls", sum(r["colgrep_calls"] for r in sel),
              "cost", round(sum(r["s4_total_cost_usd"] for r in sel), 3))
        for kind in ("fit", "near fit"):
            k = [r for r in sel if r["kind"].startswith(kind)]
            c = {}
            for r in k:
                c[r["s2_reuse"]] = c.get(r["s2_reuse"], 0) + 1
            print("   ", kind, len(k), c)


if __name__ == "__main__":
    main(*sys.argv[1:5])
