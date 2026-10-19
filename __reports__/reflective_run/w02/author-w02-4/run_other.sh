#!/bin/bash
# usage: run_other.sh <variant new|ctl> <agent>   smoke start of one non-explorer worker: loads, preload, first-turn context
S=${SCRATCH:?set SCRATCH}
v=$1; ag=$2; tag=${v}_$ag
rm -rf $S/lab_$tag; cp -R $S/lab_base $S/lab_$tag; cd $S/lab_$tag
claude -p --model haiku --plugin-dir $S/plug_$v --output-format json --max-budget-usd 0.5 --permission-mode auto \
  "Use the Agent tool once with subagent_type 'w02c4:$ag', description 'smoke', prompt 'Your name is $ag-w01-z. Do no work. Reply with one line: ok, then the exact names of the tools you can call directly.' Then print the subagent's reply verbatim." > $S/e_$tag.json 2> $S/e_$tag.err </dev/null
echo "$tag cost=$(jq .total_cost_usd $S/e_$tag.json)"
