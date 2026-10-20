#!/bin/sh
# Runs wave-4 E1/E2 end to end (export of three arms from a commit, headless cells, analysis, summary) into <scratch>, from the commit named in argv[2]; `quick` runs arms A and C once at 20 files.
# usage: budget_arms_run_all.sh <scratch dir outside the repo> <commit> [quick]     Output: <scratch>/derived/{results_all_runs.tsv,cost_per_run.tsv,summary_by_arm.tsv}. Needs claude 2.1.302 on PATH, git, python3.
# Full: the uncapped E1/E2 set (A, B, C x 3, seeds 20261021-23, N = 90, USD 0.30) and the uncapped exploratory X (A, C x 2, N = 150, brief `list`): 13 cells in parallel, about 10 minutes, USD about 4.7. The capped sets of the report (--cap 1.5) are the same call with --cap.
set -e
S="$1"; C="$2"; Q="$3"; H="$(cd "$(dirname "$0")/.." && pwd)"; I="$H/__instrumenta__"
mkdir -p "$S/logs"; (cd "$H" && sh "$I/budget_arms_export.sh" "$S" "$C" >/dev/null)
run() { python3 "$I/headless_explorer_cell.py" "$S" "$@" > "$S/logs/$1.out" 2> "$S/logs/$1.err"; }
CELLS=""
if [ "$Q" = quick ]; then
  run q-a1 "$S/plugin_A" --seed 20261021 --files 20 & run q-c1 "$S/plugin_C" --seed 20261021 --files 20 & wait
  CELLS="q-a1:A q-c1:C"
else
  for k in 1 2 3; do for arm in A B C; do l=$(echo $arm | tr A-Z a-z); run u-$l$k "$S/plugin_$arm" --seed $((20261020+k)) --files 90 & CELLS="$CELLS u-$l$k:$arm"; done; done
  for k in 1 2; do for arm in A C; do l=$(echo $arm | tr A-Z a-z); run ux-$l$k "$S/plugin_$arm" --seed $((20261030+k)) --files 150 --brief list & CELLS="$CELLS ux-$l$k:X$arm"; done; done
  wait
fi
python3 -I "$I/budget_arms_analyze.py" "$S" "$S/plugin_A/scripts" "$S/derived" $CELLS > /dev/null
mv "$S"/derived/table_*.tsv "$S/derived/results_all_runs.tsv"
python3 - "$S" <<'PY'
import glob, json, os, sys
S = sys.argv[1]; rows = ["cell\tset\tarm\tname\ttotal_cost_usd"]; tot = 0
for f in sorted(glob.glob(os.path.join(S, "runs", "*", "meta.json"))):
    m = json.load(open(f)); tot += m["usd"]; rows.append("\t".join(map(str, [m["cell"], "run", "", m["name"], round(m["usd"], 4)])))
rows.append("TOTAL\t\t\t\t%.4f" % tot); open(os.path.join(S, "derived", "cost_per_run.tsv"), "w").write("\n".join(rows) + "\n")
PY
python3 -I "$I/budget_arms_summary.py" "$S/derived" 2>&1 | tail -4
