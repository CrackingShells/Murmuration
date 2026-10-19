#!/bin/sh
# Claim w01-c3: the same code on a subset, about 5 s: the combinatorics case only (4 ended sessions, exact answers known).
cd "$(dirname "$0")" || exit 1
export PYTHONDONTWRITEBYTECODE=1
python3 -I compare.py --quick                      # v6 vs lab_spend on the combinatorics project -> compare_quick.csv/.txt
python3 -I validate.py --quick                     # 5 lab sessions + 2 combinatorics sessions against cost-state -> validate_cells_quick.csv
python3 -I lab_spend.py --root /Users/hacker/Documents/explore/combinatorics_on_binary | head -8
