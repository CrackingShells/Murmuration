#!/bin/bash
R=/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-8-928ebd/__instrumenta__/w08f_run.py
S=/private/tmp/murmuration-w08/explorer-w08-f
for rep in 1 2 3; do
  for a in default low medium high max; do
    python3 -I $R $S T-$a-$rep --agent w08f:th-$a --prompt "$(cat $S/prompt_think.txt)" &
  done
  wait
done
