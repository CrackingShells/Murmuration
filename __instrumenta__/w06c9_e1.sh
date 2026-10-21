# w06-c9: runs metric e1 (replay of the 197 transcripts, sequential and with parallel PostToolUse threads, and three deliberate mutants) of main's export (OLD) against the build's export (NEW); inputs: env OLD, NEW (plugin roots), OUT (folder for results and scratch); output: $OUT/results/e1_*.txt, one line per transcript
# usage: OLD=<dir> NEW=<dir> OUT=<dir> sh __instrumenta__/w06c9_e1.sh   (full: about 4 minutes for each of the five lines, run side by side; quick: QUICK=1 uses the first 5 transcripts and the mutants the first 5 as well)
mkdir -p $OUT/results $OUT/exp
python3 -I __instrumenta__/w06c9_list197.py > $OUT/exp/list197.txt
if [ -n "$QUICK" ]; then head -5 $OUT/exp/list197.txt > $OUT/exp/list_used.txt; else cp $OUT/exp/list197.txt $OUT/exp/list_used.txt; fi
LIST=$(cat $OUT/exp/list_used.txt)
python3 -I __instrumenta__/w06c9_replay.py --old $OLD --new $NEW --fx $OUT/fx_seq $LIST > $OUT/results/e1_seq.txt 2>&1 &
python3 -I __instrumenta__/w06c9_replay.py --parallel --old $OLD --new $NEW --fx $OUT/fx_par $LIST > $OUT/results/e1_par.txt 2>&1 &
python3 -I __instrumenta__/w06c9_replay.py --mutate cost --old $OLD --new $NEW --fx $OUT/fx_m1 $LIST > $OUT/results/e1_mut_cost.txt 2>&1 &
python3 -I __instrumenta__/w06c9_replay.py --mutate block --old $OLD --new $NEW --fx $OUT/fx_m2 $LIST > $OUT/results/e1_mut_block.txt 2>&1 &
python3 -I __instrumenta__/w06c9_replay.py --mutate loads --old $OLD --new $NEW --fx $OUT/fx_m3 $LIST > $OUT/results/e1_mut_loads.txt 2>&1 &
wait
for f in seq par mut_cost mut_block mut_loads; do echo "$f: $(grep -c ' EQUAL' $OUT/results/e1_$f.txt) EQUAL, $(grep -c ' DIFF' $OUT/results/e1_$f.txt) DIFF"; done
