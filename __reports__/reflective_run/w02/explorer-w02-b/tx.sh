#!/bin/bash
# usage: tx.sh <tag>  -> prints skill_listing attachments and usage per turn for the subagent of lab_<tag>
S=/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/explorer-w02-b
D=$(ls -d ~/.claude/projects/*explorer-w02-b-lab-$1)/$(jq -r .session_id $S/e_$1.json)/subagents
echo "== $1"
jq -r 'select(.type=="attachment")|.attachment.type' $D/agent-*.jsonl | sort | uniq -c | tr '\n' ';'; echo
python3 -I $S/sl4.py $D/agent-*.jsonl
jq -c 'select(.type=="assistant")|.message.usage|[.input_tokens,.cache_creation_input_tokens,.cache_read_input_tokens,.cache_creation]' $D/agent-*.jsonl | awk '!s[$0]++' | head -40
