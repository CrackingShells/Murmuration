#!/bin/sh
# Quick: the same code on a small subset, about 1 minute. Selftest, mutants, check.py --quick, combinatorics view.
set -e
D=$(cd "$(dirname "$0")" && pwd)
WT=$(cd "$D/../../../.." && pwd)
PY=$(command -v python3)
cd "$D"
"$PY" -I "$WT/scripts/lab_status.py" --selftest
"$PY" -I mutants.py
"$PY" -I check.py --quick
"$PY" -I "$WT/scripts/lab_status.py" --spend --project /Users/hacker/Documents/explore/combinatorics_on_binary | head -8
