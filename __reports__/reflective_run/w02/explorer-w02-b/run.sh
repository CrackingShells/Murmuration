#!/bin/bash
# usage: run.sh <tag> <agent> <ncalls> [extra claude args...]
S=/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/explorer-w02-b
tag=$1; ag=$2; n=$3; shift 3
mkdir -p $S/lab_$tag; cd $S/lab_$tag
claude -p --model haiku --plugin-dir $S/plug --output-format json --max-budget-usd 0.4 --permission-mode bypassPermissions "$@" "Use the Agent tool once with subagent_type 'w02b:$ag', name 'walker-$tag', description 'walk', prompt 'Your name is walker-$tag. Run $n Bash calls.' Then say the subagent's reply." > $S/e_$tag.json 2> $S/e_$tag.err
echo "$tag cost=$(jq .total_cost_usd $S/e_$tag.json) sid=$(jq -r .session_id $S/e_$tag.json)"
