#!/bin/bash
# usage: ttl.sh <tag> : sums cache_creation 5m/1h for main and subagent transcripts of lab_<tag>
S=/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/explorer-w02-b
D=$($S/sd.sh $1)
M=$(dirname $D).jsonl
sum() { jq -s '[.[]|select(.type=="assistant")|.message|{id,u:.usage}]|unique_by(.id)|[.[].u.cache_creation|select(.!=null)]|{n:length,m5:(map(.ephemeral_5m_input_tokens)|add),h1:(map(.ephemeral_1h_input_tokens)|add)}' "$@" | tr -d '\n '; echo; }
echo -n "$1 main: "; sum $M
echo -n "$1 sub : "; sum $D/agent-*.jsonl
