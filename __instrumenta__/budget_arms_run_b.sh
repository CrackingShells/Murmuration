#!/bin/sh
# Runs wave-4 E1b (list brief, 150 files, arms A and B') and E2b (sums task, 70 files, arms N = A and C): 12 uncapped cells in parallel, then the analysis, into <scratch>/derived2; exports from the named commit.
# usage: budget_arms_run_b.sh <scratch dir outside the repo> <commit>. About 6 minutes (E2b-N cells ran after E2b-C in the report: same arguments), USD about 4.5. The cells were started by hand with these arguments; this file was not run as a script.
set -e
S="$1"; C="$2"; H="$(cd "$(dirname "$0")/.." && pwd)"; I="$H/__instrumenta__"
mkdir -p "$S/logs"; (cd "$H" && sh "$I/budget_arms_export.sh" "$S" "$C" >/dev/null)
CELLS=""
for k in 1 2 3; do
  python3 "$I/headless_explorer_cell.py" "$S" e1b-a$k "$S/plugin_A"  --seed $((20261040+k)) --files 150 --brief list & CELLS="$CELLS e1b-a$k:A"
  python3 "$I/headless_explorer_cell.py" "$S" e1b-b$k "$S/plugin_Bp" --seed $((20261040+k)) --files 150 --brief list & CELLS="$CELLS e1b-b$k:Bp"
  python3 "$I/headless_explorer_cell.py" "$S" e2b-a$k "$S/plugin_A"  --seed $((20261050+k)) --files 70 --task sums & CELLS="$CELLS e2b-a$k:N"
  python3 "$I/headless_explorer_cell.py" "$S" e2b-c$k "$S/plugin_C"  --seed $((20261050+k)) --files 70 --task sums & CELLS="$CELLS e2b-c$k:C"
done; wait
python3 -I "$I/budget_arms_analyze.py" "$S" "$S/plugin_A/scripts" "$S/derived2" $CELLS > /dev/null
