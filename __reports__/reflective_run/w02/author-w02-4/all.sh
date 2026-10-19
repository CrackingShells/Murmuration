#!/bin/bash
# all.sh: every run behind the numbers in the claim: 6 lean explorer runs (a-f), 3 control runs, 2 old-plugin runs,
# 4 smoke starts, then the measurement. About USD 1.4 in total, 10 minutes. Sonnet explorers, haiku main session.
# usage: SCRATCH=<folder outside the worktree> all.sh
set -e
D=$(cd "$(dirname "$0")" && pwd); bash "$D/setup.sh"; cd "$SCRATCH"
(./run.sh new a </dev/null & ./run.sh new b </dev/null & ./run.sh new c </dev/null & ./run.sh ctl a </dev/null & ./run.sh ctl b </dev/null & wait)
(BRIEF=brief_d.txt ./run.sh new d </dev/null & BRIEF=brief_d.txt ./run.sh ctl d </dev/null & BRIEF=brief_e.txt ./run.sh new e </dev/null & BRIEF=brief_e.txt ./run.sh new f </dev/null & wait)
(./run.sh old a </dev/null & ./run.sh old b </dev/null & wait)
(for a in author reproducer proof-adversary; do ./run_other.sh new $a & done; ./run_other.sh ctl author & wait)
python3 measure.py new_a new_b new_c new_d new_e new_f ctl_a ctl_b ctl_d old_a old_b > result.jsonl
python3 smoke.py > smoke.txt
python3 -c "
import glob, json
print('USD total', round(sum(json.load(open(f))['total_cost_usd'] for f in glob.glob('e_*.json')), 3))"
