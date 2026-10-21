#!/bin/sh
# Runs P6 end to end: exports A and B, runs c1 (A1 B1 A2 B2) serially and c2 (A3 B3, 7.5 minutes each) in parallel, then parses c1-c3 and prices; inputs: scratch folder S (empty or new), lab repo, commits A and B; outputs: S/runs, S/parsed.json, tables on stdout.
# usage: w07c7_full.sh S LAB COMMIT_A COMMIT_B [quick]   (quick: only A1 and B1, about 1 minute; full: 6 sessions, about 8 minutes wall; USD 0.05 in total)
S=$1; LAB=$2; CA=$3; CB=$4; I=$(dirname "$0"); mkdir -p "$S"
if [ "$5" = quick ]; then
  python3 -I $I/w07c7_run.py $S $LAB $CA $CB A1,B1
  python3 -I $I/w07c7_parse.py $S A1,B1; python3 -I $I/w07c7_prices.py $S $LAB A1,B1
else
  python3 -I $I/w07c7_run.py $S $LAB $CA $CB A3 > $S/A3.job.log 2>&1 &
  python3 -I $I/w07c7_run.py $S $LAB $CA $CB B3 > $S/B3.job.log 2>&1 &
  python3 -I $I/w07c7_run.py $S $LAB $CA $CB B1,A2,B2,A1
  wait
  python3 -I $I/w07c7_parse.py $S A1,B1,A2,B2,A3,B3; python3 -I $I/w07c7_prices.py $S $LAB A1,B1,A2,B2,A3,B3
fi
