#!/bin/bash
H=/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-2
DES="/Users/hacker/Library/Application Support/Claude/claude-code/2.1.299/4fa9694b7975/claude.app/Contents/MacOS/claude"
AG='{"essayist": {"description": "reads note.txt, then writes about its topic", "prompt": "You are an essayist. Read note.txt with the Bash tool (cat note.txt). Think it through carefully first. Then write a clear, self-contained explanation of the topic of about 600 words, as your final answer, in prose.", "model": "haiku"}}'
P="Call the Agent tool exactly once with subagent_type 'essayist', in the foreground (run_in_background: false); wait for its result. When it has finished, reply with the single word DONE."
run() { # name bin mode
  d=$H/scratch/$1; mkdir -p $d; echo "Topic: why the number of subsets of an n-element set doubles each time n grows by one" > $d/note.txt
  ( cd $d && "$2" -p --model haiku --setting-sources project --agents "$AG" --output-format stream-json --verbose --permission-mode $3 --max-budget-usd 0.15 "$P" > stdout.jsonl 2> stderr.txt )
}
run ins-auto claude auto &
run ins-bypass claude bypassPermissions &
run des-auto "$DES" auto &
run des-bypass "$DES" bypassPermissions &
wait
