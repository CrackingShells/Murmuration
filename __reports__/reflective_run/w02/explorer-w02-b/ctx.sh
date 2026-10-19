#!/bin/bash
S=/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/explorer-w02-b
D=$($S/sd.sh $1)
echo -n "$1 first-turn ctx / listing attachments / preloaded-skill record / cost: "
jq -s '[.[]|select(.type=="assistant")]|.[0].message.usage|(.input_tokens+.cache_read_input_tokens+.cache_creation_input_tokens)' $D/agent-*.jsonl | tr '\n' ' '
echo -n "/ "; jq -c 'select(.type=="attachment" and .attachment.type=="skill_listing")|.attachment.content|length' $D/agent-*.jsonl | tr '\n' ' '
echo -n "/ "; jq -c 'select(.type=="user")|.message.content|tostring|select(contains("command-name>mini"))|1' $D/agent-*.jsonl | wc -l | tr -d ' \n'
echo " / $(jq .total_cost_usd $S/e_$1.json)"
