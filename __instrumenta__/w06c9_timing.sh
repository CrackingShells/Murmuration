# w06-c9: times every hook registration of plugin variants on recorded payloads and two real worker transcripts (a thin driver of hook_cost_time.py and hook_cost_summary.py); inputs: env TAG (output name), VARIANTS ("--variant name=dir ..."), N (pairs per cell, default 8), ONLY (optional "--only substring"); output: $S/exp/timing_$TAG.jsonl and the summary table on stdout
S=/private/tmp/murmuration-w06/author-w06-6
SHORT=$HOME/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/subagents/agent-a3ca5291991a08315.jsonl
LONG=$HOME/.claude/projects/-private-tmp-reproducer-w03-1-s2-runs-r1-lab/e08e7434-4338-497d-b7c1-339f5856ef4e/subagents/agent-a50b3982ac2a64503.jsonl
python3 -I __instrumenta__/hook_cost_time.py $VARIANTS --payloads __reports__/reflective_run/w04/author-w04-4/derived/recorded_payloads_rec1.jsonl --transcripts short=$SHORT,long=$LONG --reports-src $S/reports_src --fx $S/fx_$TAG --n ${N:-8} --spawn posix --paired --stdin sock --no-floors $ONLY --out $S/exp/timing_$TAG.jsonl
python3 -I __instrumenta__/hook_cost_summary.py $S/exp/timing_$TAG.jsonl
