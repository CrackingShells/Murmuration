#!/bin/bash
# usage: run.sh <variant new|ctl> <name letter>   one explorer run in a fresh copy of the scratch lab
S=${SCRATCH:?set SCRATCH}
v=$1; n=$2; tag=${v}_$n
rm -rf $S/lab_$tag; cp -R $S/lab_base $S/lab_$tag; cd $S/lab_$tag
BF=${BRIEF:-brief.txt}; B=$(sed "s/NAME/$n/g" $S/$BF)
claude -p --model haiku --plugin-dir $S/plug_$v --output-format json --max-budget-usd 1.0 --permission-mode auto \
  "Use the Agent tool once with subagent_type 'w02c4:explorer', name 'explorer-w01-$n', description 'probe', and this exact prompt (between the markers).
<<<
$B
>>>
Then print the subagent's reply verbatim." > $S/e_$tag.json 2> $S/e_$tag.err
echo "$tag cost=$(jq .total_cost_usd $S/e_$tag.json) sid=$(jq -r .session_id $S/e_$tag.json) turns=$(jq .num_turns $S/e_$tag.json)"
