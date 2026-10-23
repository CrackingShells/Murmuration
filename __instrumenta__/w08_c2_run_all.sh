#!/bin/bash
# Reproduces w08-c2 (protocol P2): the past hand-back tables and counterfactual, the selftest and offline cases of the length check, and the live headless cells with their tables.
# usage: w08_c2_run_all.sh full|quick OUT S REPO REV_ON REV_OFF     (OUT: a folder for the tables, S: a scratch folder for the live runs, REPO: the checkout holding REV_ON and REV_OFF)
#   full : 12 live cells (haiku parent and worker, about 2.5 min each, 4 at a time, USD 0.2 in all at list price) + all tables: about 12 min
#   quick: the past tables, selftest, offline cases, and 2 live cells (e_on_auto, e_short_auto): about 4 min, USD 0.03
# Needs the PI and worker transcripts of waves 1-8 under ~/.claude/projects (read only) and explorer-w08-d's tsv files in __reports__/wave-08/explorer-w08-d/.
set -e
MODE=$1; OUT=$2; S=$3; REPO=$4; ON=$5; OFF=$6
HERE=$(cd "$(dirname "$0")/.." && pwd); I=$HERE/__instrumenta__; D=$HERE/__reports__/wave-08/explorer-w08-d
P=$HOME/.claude/projects
f() { python3 -I -c "import glob,sys;print(glob.glob('$P/'+sys.argv[1])[0])" "$1"; }
mkdir -p "$OUT" "$S"
S1=$(f '*system-optimization-8cff9e/ab96c5ed*.jsonl'); S2=$(f '*wave-4-3417be/c533f1c6*.jsonl'); S3=$(f '*lab-system-optimization-1aa673/6b0e1f2a*.jsonl')
S4=$(f '*blissful-villani-34edd8/74fa512e*.jsonl'); S5=$(f '*xenodochial-franklin-bc67fb/f023f552*.jsonl'); S6=$(f '*wave-8-928ebd/ad75be4f*.jsonl')
python3 -I $I/w08_c2_handbacks.py $OUT/handbacks.tsv s1_w1-3=$S1 s2_w4=$S2 s3_w5=$S3 s4_w6=$S4 s5_w7=$S5 s6_w8=$S6
python3 -I $I/w08_c2_pi_side.py $OUT s1_w1-3=$S1=$D/s1_w1-3_items.tsv=$D/s1_w1-3_requests.tsv s2_w4=$S2=$D/s2_w4_items.tsv=$D/s2_w4_requests.tsv s3_w5=$S3=$D/s3_w5_items.tsv=$D/s3_w5_requests.tsv \
  s4_w6=$S4=$D/s4_w6_items.tsv=$D/s4_w6_requests.tsv s5_w7=$S5=$D/s5_w7_items.tsv=$D/s5_w7_requests.tsv s6_w8=$S6=$D/s6_w8_items.tsv=$D/s6_w8_requests.tsv
python3 -I $I/w08_c2_sections.py $HERE $OUT
for s in 600 1200 2000; do for v in "" low; do python3 -I $I/w08_c2_counterfactual.py $OUT $s $v > /dev/null; done; done
python3 -I $I/w08_c2_counterfactual.py $OUT 1200 full > /dev/null
python3 $REPO/scripts/handback.py --selftest
python3 -I $I/w08_c2_live.py exports $S $REPO $ON $OFF
python3 -I $I/w08_c2_offline.py $S/exp_on $OUT
if [ "$MODE" = quick ]; then CELLS="e_on_auto e_short_auto"; else CELLS="e_on_auto e_off_auto e_short_auto e_repeat_auto a_on_auto a_off_auto a_nopath_auto e_on_default e_on_auto_r2 e_on_auto_r3 a_on_auto_r2 a_on_auto_r3"; fi
n=0
for c in $CELLS; do python3 -I $I/w08_c2_live.py cell $S $c > $S/$c.job.log 2>&1 & n=$((n+1)); if [ $((n % 4)) = 0 ]; then wait; fi; done; wait
python3 -I $I/w08_c2_live_table.py $S $OUT
