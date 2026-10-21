# w06-c9 hardening: command-mode check (w06c9_verify_commands.py) of main against the five `_json` masks A-E of one build, on four transcripts; inputs: env OLD (main export), MASKS (folder from w06c9_make_masks.py), OUT (scratch, new), RES (folder), TAG (output prefix); output: $RES/<TAG>_mask{A..E}.txt and the last line of each on stdout
mkdir -p $RES $OUT
python3 -I __instrumenta__/w06c9_list197.py > $OUT/list197.txt
TR4=$(for s in abe4e78584507379e a1f4458ce75dacdec a8427a2477a2a02c2 a8b904eac66ca2fe4; do grep "agent-$s.jsonl" $OUT/list197.txt; done)
for m in A B C D E; do
  python3 -I __instrumenta__/w06c9_verify_commands.py --old $OLD --new $MASKS/mask$m --work $OUT/cmd_$m --jobs 1 $TR4 > $RES/${TAG}_mask$m.txt 2>&1 &
done
wait
for m in A B C D E; do echo "$TAG mask$m: $(tail -1 $RES/${TAG}_mask$m.txt | cut -c1-200)"; done
