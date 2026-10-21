# w06-c9 hardening: reruns the command-mode check (main against the build) on one transcript N times, to tell a clock effect from a logic difference; inputs: env OLD, NEW, OUT (scratch, new), RES (folder), AGENT (transcript id, default a14002b966174526e), N (default 3); output: $RES/h_cmd_rerun_<i>.txt and the last line of each
mkdir -p $RES $OUT
python3 -I __instrumenta__/w06c9_list197.py > $OUT/list197.txt
TR=$(grep "agent-${AGENT:-a14002b966174526e}.jsonl" $OUT/list197.txt)
for i in $(seq 1 ${N:-3}); do
  python3 -I __instrumenta__/w06c9_verify_commands.py --old $OLD --new $NEW --work $OUT/rerun_$i --jobs 1 $TR > $RES/h_cmd_rerun_$i.txt 2>&1 &
done
wait
for i in $(seq 1 ${N:-3}); do echo "rerun $i: $(tail -1 $RES/h_cmd_rerun_$i.txt | cut -c1-700)"; done
