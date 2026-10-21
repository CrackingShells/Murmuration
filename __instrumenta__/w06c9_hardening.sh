# w06-c9 hardening check: the six selftests, the e1 replay (sequential and parallel, mutants), the command-mode check of main against the build and against the five `_json` masks A-E, and the json fuzz with and without a mask; inputs: env OLD (main export), NEW (build export), MASKS (folder made by w06c9_make_masks.py from NEW), OUT (scratch, new), RES (folder for the outputs); output: $RES/h_*.txt and a summary on stdout
# usage: OLD=.. NEW=.. MASKS=.. OUT=.. RES=.. sh __instrumenta__/w06c9_hardening.sh   (about 6 minutes; the replay is the long part)
mkdir -p $RES $OUT
sh __instrumenta__/w06c9_selftests.sh $NEW > $RES/h_selftests.txt
python3 -I __instrumenta__/w06c9_list197.py > $OUT/list197.txt
SAMPLE="abe4e78584507379e a236ec9f6bcc0c19f a8427a2477a2a02c2 a1f4458ce75dacdec a8b904eac66ca2fe4 af9c9879f35b93623 a14002b966174526e a0f7fc4df62779853 aa1c72b39e7eedcd2 a507b6cb60663fb21"
TR10=$(for s in $SAMPLE; do grep "agent-$s.jsonl" $OUT/list197.txt; done)
TR4=$(for s in abe4e78584507379e a1f4458ce75dacdec a8427a2477a2a02c2 a8b904eac66ca2fe4; do grep "agent-$s.jsonl" $OUT/list197.txt; done)
OLD=$OLD NEW=$NEW OUT=$OUT/e1 QUICK= sh __instrumenta__/w06c9_e1.sh > $RES/h_e1_summary.txt 2>&1 &
python3 -I __instrumenta__/w06c9_verify_commands.py --old $OLD --new $NEW --work $OUT/cmd_ok --jobs 2 $TR10 > $RES/h_cmd_ok.txt 2>&1 &
for m in A B C D E; do
  python3 -I __instrumenta__/w06c9_verify_commands.py --old $OLD --new $MASKS/mask$m --work $OUT/cmd_$m --jobs 1 $TR4 > $RES/h_cmd_mask$m.txt 2>&1 &
done
wait
cp $OUT/e1/results/e1_seq.txt $OUT/e1/results/e1_par.txt $OUT/e1/results/e1_mut_cost.txt $OUT/e1/results/e1_mut_block.txt $OUT/e1/results/e1_mut_loads.txt $RES/ 2>/dev/null
for m in "" A B C D E; do python3 -I __instrumenta__/w06c9_fuzz_json.py $NEW $m > $RES/h_fuzz_${m:-none}.txt 2>&1; done
python3 -I __instrumenta__/w06c9_lines.py $OLD $NEW > $RES/h_e4_lines.txt
cat $RES/h_selftests.txt $RES/h_e1_summary.txt
for f in $RES/h_cmd_ok.txt $RES/h_cmd_mask?.txt; do echo "$f: $(tail -1 $f)"; done
for f in $RES/h_fuzz_*.txt; do echo "$f: $(head -1 $f)"; done
tail -1 $RES/h_e4_lines.txt
