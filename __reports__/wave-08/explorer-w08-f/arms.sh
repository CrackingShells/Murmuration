#!/bin/bash
# runs the effort arms, 4 at a time (one per arm), three repeats, for task $1 (src dir) with label prefix $2
R=/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-8-928ebd/__instrumenta__/w08f_run.py
S=/private/tmp/murmuration-w08/explorer-w08-f
for rep in 1 2 3; do
  for a in default low medium high; do
    python3 -I $R $S $2-$a-$rep --agent w08f:vf-$a --task --src $1 &
  done
  wait
done
