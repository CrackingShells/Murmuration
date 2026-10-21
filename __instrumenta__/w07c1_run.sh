#!/bin/bash
# Builds the A and B exports of w07-c1 from git (agent files set to haiku) and runs the registered cells with w07c1_cell.py into <scratch>/runs, then tabulates them; inputs: mode (full|quick), scratch dir, lab worktree (default: this repo); output: <scratch>/runs/*/summary.json and a table on stdout.
# full = the 20 sessions of the claim (A p2 x3, B p2 x3, B p4 x2, B p5 x2, then v1: p2 x3, p4 x2, p5 x2, A p2 extra, A p5d); quick = A p2 and B p2 (2 sessions, about USD 0.02, 1 to 2 minutes). Sessions of a group run concurrently; one concurrent session once failed with "Not logged in" and had to be rerun alone.
set -u
MODE=${1:-quick}; S=${2:-/private/tmp/murmuration-w07/author-w07-1}; R=${3:-$(git rev-parse --show-toplevel)}
HERE=$R/__instrumenta__; A=7c6f4b6; B0=62dc6a4; B1=e5f4724
mk() { rm -rf $S/export_$1; mkdir -p $S/export_$1; git -C $R archive $2 | tar -x -C $S/export_$1; for f in $S/export_$1/agents/*.md; do sed -i.bak -E 's/^model: .*/model: haiku/' $f; rm -f $f.bak; done; }
mk A $A; mk B $B0
run() { python3 $HERE/w07c1_cell.py $S "$@" > $S/$1.out 2>&1; }
if [ "$MODE" = quick ]; then
  run A1 $S/export_A p2 & run B1 $S/export_B p2 & wait
else
  mk B1v $B1
  run A1 $S/export_A p2 & run B1 $S/export_B p2 & wait
  run A2 $S/export_A p2 & run B2 $S/export_B p2 & run A3 $S/export_A p2 & run B3 $S/export_B p2 & \
  run B_p4s $S/export_B p4s & run B_p4l $S/export_B p4l --nolab & run B_p5d $S/export_B p5d & run B_p5w $S/export_B p5w & wait
  run V1_1 $S/export_B1v p2 & run V1_2 $S/export_B1v p2 & run V1_3 $S/export_B1v p2 & run A4 $S/export_A p2 & wait
  run V1_p4s $S/export_B1v p4s & run V1_p4l $S/export_B1v p4l --nolab & run V1_p5d $S/export_B1v p5d & run V1_p5w $S/export_B1v p5w & wait
  run A_p5d $S/export_A p5d
fi
python3 -I $HERE/w07c1_table.py $S 2>&1
