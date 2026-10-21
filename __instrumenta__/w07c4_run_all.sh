#!/bin/sh
# Runs protocol P4's checks o1-o4 (A = scripts/lab_status.py at 1c23e5c, B = the one in this checkout) from a lab root and an output folder to the text files o1_frozen.out, cases.out, o2.out, o3_cli.out, micro.txt, o4_seed*.txt and selftest.out in it.
# usage: w07c4_run_all.sh LAB_ROOT OUT_DIR [quick]     full: 3 batches of 30 pairs, 200 micro calls; quick: 1 batch of 6 pairs, 20 micro calls (same code, about 1-2 minutes)
# Needs git, python3 (3.12), an APFS volume (cp -c). Reads ~/.claude/projects (clones, never writes it); the clone and scratch repositories go under a folder made by mktemp in /private/tmp, which is deleted at the end.
set -eu
ROOT=$1; OUT=$2; MODE=${3:-full}
HERE=$(cd "$(dirname "$0")/.." && pwd)
B=$HERE/scripts/lab_status.py
mkdir -p "$OUT"; S=$(mktemp -d /private/tmp/w07c4-XXXXXX)   # outside any repository: git would otherwise find an enclosing one
git -C "$HERE" show 1c23e5c:scripts/lab_status.py > "$S/lab_status_A.py"
A=$S/lab_status_A.py
I=$HERE/__instrumenta__
uptime > "$OUT/load_at_start.txt"
python3 -I "$B" --selftest > "$OUT/selftest.out" 2>&1 || true
python3 -I "$I/w07c4_frozen_diff.py" "$A" "$B" "$ROOT" "$S" --clone > "$OUT/o1_frozen.out" 2>&1 || true
python3 -I "$I/w07c4_worktree_cases.py" "$A" "$B" "$S/cases" > "$OUT/cases.out" 2>&1 || true
python3 -I "$I/w07c4_o2_synthetic.py" "$A" "$B" "$S/o2" > "$OUT/o2.out" 2>&1 || true
python3 -I "$I/w07c4_o3_cli.py" "$A" "$B" "$S/cases" > "$OUT/o3_cli.out" 2>&1 || true
if [ "$MODE" = quick ]; then PAIRS=6; SEEDS="1"; N=20; else PAIRS=30; SEEDS="1 2 3"; N=200; fi
python3 -I "$I/w07c4_micro.py" "$A" "$B" "$ROOT" $N > "$OUT/micro.txt" 2>&1 || true
for sd in $SEEDS; do
  python3 -I "$I/w07c4_o4_pairs.py" "$A" "$B" "$ROOT" "$OUT/o4_seed$sd.jsonl" --pairs $PAIRS --seed $sd > "$OUT/o4_seed$sd.txt" 2>&1 || true
done
rm -rf "$S"
