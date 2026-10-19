#!/bin/bash
# prints the subagents dir for tag
S=/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/explorer-w02-b
t=${1//_/-}
echo $(ls -d ~/.claude/projects/*explorer-w02-b-lab-$t)/$(jq -r .session_id $S/e_$1.json)/subagents
