#!/bin/sh
# Claim w01-c3: every number. Read-only on ~/.claude/projects (a frozen copy is used for compare.py), writes only here.
# Cost: about 15 s, no model calls, no network. Needs python3 (standard library only), git. Seeds: none (no randomness).
cd "$(dirname "$0")" || exit 1
export PYTHONDONTWRITEBYTECODE=1
ROOT=$(git rev-parse --show-toplevel)
python3 -I validate.py        > validate.txt     # V1-V3: price table and dedup against cost-state, 50 cells -> validate_cells.csv
python3 -I crossref.py        > crossref.txt     # X1: token equality with cost-state and with explorer-w01-a
python3 -I compare.py         > compare.stdout   # C1-C3: v6 vs lab_spend on this run (worktree, main checkout) and combinatorics -> compare.csv, compare.txt
python3 -I falsify.py         > falsify.stdout   # F1-F4: the claim's false cases -> falsify.txt
python3 -I index_test.py      > index_test.stdout # I1-I3: the run-index alternative -> index_test.txt
python3 -I bench.py           > bench.stdout     # B1-B2: runtime and lines of code -> bench.txt
python3 -I lab_spend.py --root "$ROOT"                                               > human_worktree.txt
python3 -I lab_spend.py --root /Users/hacker/Documents/src/CrackingShells/Murmuration > human_main_checkout.txt
python3 -I lab_spend.py --root /Users/hacker/Documents/explore/combinatorics_on_binary > human_combinatorics.txt
echo done
