#!/bin/bash
# setup.sh: build the three scratch plugins (new = this worktree, ctl = new + Skill tool back, old = git HEAD)
# and the scratch lab. With WITH_HOOKS=1 the worktree's hooks/ is copied into new and ctl too (default: no hooks). Needs SCRATCH (a folder OUTSIDE the worktree). The plugin is renamed w02c4 in the copies.
set -e
W=$(cd "$(dirname "$0")/../../../.." && pwd); A=$W/__reports__/reflective_run/w02/author-w02-4
: "${SCRATCH:?set SCRATCH to a folder outside the worktree}"
mkdir -p "$SCRATCH"; cd "$SCRATCH"
cp "$A"/brief*.txt "$A"/*.py "$A"/run*.sh .
for v in new ctl; do
  rm -rf "./plug_$v"; mkdir -p plug_$v/.claude-plugin; cp -R "$W"/agents "$W"/skills "$W"/scripts plug_$v/; if [ -n "$WITH_HOOKS" ]; then cp -R "$W"/hooks plug_$v/; fi; rm -rf ./plug_$v/scripts/__pycache__
  sed 's/"name": "murmuration"/"name": "w02c4"/;s/"displayName": "Murmuration"/"displayName": "w02c4"/' "$W"/.claude-plugin/plugin.json > plug_$v/.claude-plugin/plugin.json
done
for a in author explorer proof-adversary reproducer; do sed 's/ToolSearch/Skill, ToolSearch/' plug_ctl/agents/$a.md > plug_ctl/agents/$a.tmp; mv plug_ctl/agents/$a.tmp plug_ctl/agents/$a.md; done
rm -rf ./plug_old; mkdir -p plug_old/.claude-plugin; (cd "$W" && git archive HEAD agents skills scripts) | tar -x -C plug_old; cp plug_new/.claude-plugin/plugin.json plug_old/.claude-plugin/
rm -rf ./lab_base; mkdir lab_base
echo "Which row of data/measurements.csv fits a linear trend worst?" | python3 plug_new/scripts/lab_init.py --project "$SCRATCH/lab_base" > /dev/null
python3 - <<'PY'
import json, os, random
p = 'lab_base/.claude/settings.local.json'
d = json.load(open(p)); d.pop('agent', None); json.dump(d, open(p, 'w'), indent=2)
random.seed(7)
os.makedirs('lab_base/data', exist_ok=True)
rows = [(i, round(2.0 * i + 1 + random.gauss(0, 0.4), 2)) for i in range(1, 13)]
rows[8] = (9, 31.5)
open('lab_base/data/measurements.csv', 'w').write("x,y\n" + "".join("%d,%s\n" % r for r in rows))
PY
echo "setup done in $SCRATCH"
