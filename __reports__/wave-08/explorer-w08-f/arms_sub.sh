#!/bin/bash
R=/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-8-928ebd/__instrumenta__/w08f_run.py
S=/private/tmp/murmuration-w08/explorer-w08-f
for rep in 1 2 3; do
  for a in default low high max; do
    P="Make exactly one call of the Agent tool with subagent_type \`w08f:th-$a\`, name \`solver\`, and as its prompt exactly the text between the markers. Wait for it, then reply with its answer and nothing else.
<<<
$(cat $S/prompt_think.txt)
>>>"
    python3 -I $R $S S-$a-$rep --model haiku --prompt "$P" &
  done
  wait
done
