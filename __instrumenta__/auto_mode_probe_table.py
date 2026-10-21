"""Turns rows.jsonl files written by auto_mode_probe.py into markdown tables: permission decision ms per cell and per command (first call excluded), first-call run time and shell-snapshot outcome per cell, tokens and USD per cell.

usage: auto_mode_probe_table.py rows.jsonl [more rows.jsonl ...]   -> markdown on stdout
"""
import json, sys, statistics as st
rows = [json.loads(l) for f in sys.argv[1:] for l in open(f)]
calls = [r for r in rows if "perm_ms" in r]; runs = [r for r in rows if r.get("run") and "error" not in r]
cells = list(dict.fromkeys(r["cell"] for r in runs)); cmds = list(dict.fromkeys(r["cmd"] for r in calls if r["n_in_run"] > 0))
md = lambda xs: int(st.median(xs)) if xs else -1
print("### permission decision ms, median over reps (calls 2..n only; n = reps)\n")
print("| cell | all calls median | p90 | " + " | ".join(cmds) + " |\n|:--|--:|--:|" + "--:|" * len(cmds))
for c in cells:
    cc = [r for r in calls if r["cell"] == c and r["n_in_run"] > 1]; v = sorted(r["perm_ms"] for r in cc)
    print("| %s | %d | %d | " % (c, md(v), v[int(.9 * (len(v) - 1))] if v else -1) + " | ".join(str(md([r["perm_ms"] for r in cc if r["cmd"] == m])) for m in cmds) + " |")
print("\n### first Bash call, snapshot, tokens, USD per run\n")
print("| cell | runs | first call run s median | min | snapshot ok/runs | snapshot s median | cache_read median | cache_create median | output median | USD mean | api-turns median |\n|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for c in cells:
    rr = [r for r in runs if r["cell"] == c]; f = [r["run_ms"] / 1000 for r in calls if r["cell"] == c and r["n_in_run"] == 1 and r["run_ms"]]
    sn = [r["snapshot_s"] for r in rr if r.get("snapshot_s") is not None]
    print("| %s | %d | %.2f | %.2f | %d/%d | %.2f | %d | %d | %d | %.5f | %d |" % (c, len(rr), st.median(f), min(f), sum(1 for r in rr if r.get("snapshot_ok")), len(rr), st.median(sn) if sn else 0, st.median(r["cache_read"] for r in rr), st.median(r["cache_create"] for r in rr), st.median(r["output"] for r in rr), st.mean(r["cost"] for r in rr), st.median(r["turns"] for r in rr)))
