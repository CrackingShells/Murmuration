#!/bin/bash
# $1 = src dir (src|srcB), $2 = label prefix (VA|VB)
R=/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-8-928ebd/__instrumenta__/w08f_run.py
S=/private/tmp/murmuration-w08/explorer-w08-f
for rep in 1 2 3; do
  for a in default low medium high max; do
    P="Make exactly one call of the Agent tool with subagent_type \`w08f:vf-$a\`, name \`verifier\`, and as its prompt exactly: Verify claim c1 in claim.md. Wait for it, then reply with its last two lines (recomputed_total_usd and verdict) verbatim and nothing else."
    python3 -I $R $S $2-$a-$rep --model haiku --task --src $1 --prompt "$P" &
  done
  wait
done
