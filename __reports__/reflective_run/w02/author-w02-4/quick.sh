#!/bin/bash
# quick.sh: one lean explorer run, one control run (Skill tool back), one old-plugin run; about USD 0.35, 2 minutes.
# usage: SCRATCH=<folder outside the worktree> quick.sh
set -e
D=$(cd "$(dirname "$0")" && pwd); bash "$D/setup.sh"; cd "$SCRATCH"
(./run.sh new a </dev/null & ./run.sh ctl a </dev/null & ./run.sh old a </dev/null & wait)
python3 measure.py new_a ctl_a old_a > quick_result.jsonl
python3 -c "
import json
for l in open('quick_result.jsonl'):
    d = json.loads(l); print({k: d.get(k) for k in ['tag', 'cost_usd', 'report_at_convention_path', 'headings_in_order', 'first_turn_ctx_tokens', 'skill_listing_chars', 'research_loop_preloaded']})"
