#!/bin/zsh
# usage: raw.sh <cell> '<json cfg>'
S=/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/explorer-w02-a
export HOOK_RAW="$2"
python3 -I $S/bin/run.py $1 --hook-mode raw --perm auto --cap none \
 --prompt "Call the Agent tool exactly once with subagent_type 'worker', in the foreground, with this prompt: 'Run these four Bash commands one per turn: echo one; then ls /nonexistent_dir; then echo three; then echo four. After that hand back a report that lists, verbatim, any message you received that is not from the user and not a tool output, and says where it appeared, and say how many Bash commands you ran.' Then say DONE." \
 --agent-prompt "You are a worker. Do the task you are given." > $S/runs/$1.out 2>&1
