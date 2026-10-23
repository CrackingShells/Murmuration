#!/bin/bash
# Runs the w08-g batching-line arms interleaved (one warm-up, then 3 reps of base, lever1, lever2 in sequence): each run is a Haiku parent that calls the Agent tool on a Sonnet 5.5 test agent from S/plug; outputs S/runs/<label>.jsonl via w08f_run.py.
# usage: w08g_arms.sh S REPS [ARMS="base lever1 lever2"]
S=$1; REPS=${2:-3}; ARMS=${3:-"base lever1 lever2"}
R=/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-8-928ebd/__instrumenta__/w08f_run.py
run() { # label agent
  P="Make exactly one call of the Agent tool with subagent_type \`w08g:vf-$2\`, name \`verifier\`, and as its prompt exactly: Verify claim c1 in claim.md. Wait for it, then reply with its last two lines (recomputed_total_usd and verdict) verbatim and nothing else."
  python3 -I $R $S $1 --model haiku --task --src . --prompt "$P"
}
run W0-base base
for rep in $(seq 1 $REPS); do
  for a in $ARMS; do run V-$a-$rep $a; done
done
