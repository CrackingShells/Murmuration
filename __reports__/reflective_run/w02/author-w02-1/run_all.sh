#!/bin/sh
# Full: reproduces every number of claim w02-c1. About 30 s, no model calls, no network, no randomness (no seeds).
# Run from anywhere: sh __reports__/reflective_run/w02/author-w02-1/run_all.sh
set -e
D=$(cd "$(dirname "$0")" && pwd)
WT=$(cd "$D/../../../.." && pwd)
MAIN=/Users/hacker/Documents/src/CrackingShells/Murmuration
COMB=/Users/hacker/Documents/explore/combinatorics_on_binary
PY=$(command -v python3)
cd "$D"
"$PY" -I "$WT/scripts/lab_status.py" --selftest
"$PY" -I mutants.py > mutants.txt; cat mutants.txt
"$PY" -I check.py > check.txt; cat check.txt
t() { s=$(date +%s.%N 2>/dev/null || date +%s); "$@" > "$OUT" 2>&1; e=$(date +%s.%N 2>/dev/null || date +%s); echo "$e - $s" | bc 2>/dev/null || true; }
OUT=after_worktree.txt;       echo "worktree seconds:       $(t "$PY" -I "$WT/scripts/lab_status.py" --project "$WT")"
OUT=after_main.txt;           echo "main checkout seconds:  $(t "$PY" -I "$WT/scripts/lab_status.py" --project "$MAIN")"
OUT=after_combinatorics.txt;  echo "combinatorics seconds:  $(t "$PY" -I "$WT/scripts/lab_status.py" --spend --project "$COMB")"
# F3: without git on PATH the lab is its own folder only (no worktrees found)
OUT=after_main_nogit.txt;     echo "main checkout, no git:  $(t /usr/bin/env PATH=/nonexistent "$PY" -I "$WT/scripts/lab_status.py" --project "$MAIN")"
wc -l "$WT/scripts/lab_status.py" "$WT/skills/lab-status/SKILL.md" > lines_after.txt; cat lines_after.txt
