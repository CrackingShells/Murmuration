#!/bin/sh
# Lists and runs the capped cells of wave-4 E1/E2 (the first 18 non-pilot runs, `--cap 1.5`): E1/E2 arms A, B, C at 90 files and exploratory XA, XB, XC at 150 files with the `list` brief; same driver as budget_arms_run_all.sh.
# usage: budget_arms_run_capped.sh <scratch dir> <commit>. NOT run as a script (the cells were started by hand with these exact arguments; cell names as in derived/results_all_runs.tsv). About USD 6.2, 10 minutes.
set -e
S="$1"; C="$2"; H="$(cd "$(dirname "$0")/.." && pwd)"; I="$H/__instrumenta__"
mkdir -p "$S/logs"; (cd "$H" && sh "$I/budget_arms_export.sh" "$S" "$C" >/dev/null)
for k in 1 2 3; do
  python3 "$I/headless_explorer_cell.py" "$S" e1-a$k "$S/plugin_A" --seed $((20261020+k)) --files 90 --cap 1.5 &
  python3 "$I/headless_explorer_cell.py" "$S" e1-b$k "$S/plugin_B" --seed $((20261020+k)) --files 90 --cap 1.5 &
  python3 "$I/headless_explorer_cell.py" "$S" e2-c$k "$S/plugin_C" --seed $((20261020+k)) --files 90 --cap 1.5 &
done; wait
for k in 1 2 3; do for arm in A B C; do l=$(echo $arm | tr A-Z a-z)
  python3 "$I/headless_explorer_cell.py" "$S" x-$l$k "$S/plugin_$arm" --seed $((20261030+k)) --files 150 --brief list --cap 1.5 &
done; done; wait
