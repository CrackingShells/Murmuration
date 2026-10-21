#!/bin/zsh
# Headless check of the colgrep `paths` form: from a scratch lab holding a script that exists nowhere else, one search with the relative path ["__instrumenta__"] and one with the absolute path of the lab's folder; output: the paths the server echoes and the hit file names, as the model reports them (stream in <scratch>/run.jsonl).
# usage: w05c2_colgrep_path_probe.sh <scratch dir outside the repo>. Cost about USD 0.01 (haiku). Needs the colgrep MCP server of the user's config.
B=$1; rm -rf $B; mkdir -p $B/lab/__instrumenta__; cd $B/lab && git init -q . || exit 1
printf '# zz_lab_only_probe: computes the harmonic mean of a list of numbers read from stdin; exists only in the c2 test lab.\nimport sys\nxs=[float(x) for x in sys.stdin.read().split()]\nprint(len(xs)/sum(1/x for x in xs))\n' > __instrumenta__/zz_lab_only_probe.py
git add -A && git -c user.name=t -c user.email=t@example.invalid commit -qm init
cat > $B/prompt.txt <<EOT
Call the colgrep search tool (mcp__plugin_colgrep-mcp_colgrep__search; load it with ToolSearch first if it is deferred) exactly twice, query "harmonic mean of numbers read from stdin", limit 5. Call 1: paths ["__instrumenta__"]. Call 2: paths ["$B/lab/__instrumenta__"]. For each call, report the "paths" value the tool echoes back and the file names of the hits (or the exact error). Do nothing else.
EOT
env -u CLAUDE_PROJECT_DIR COLGREP_DATA_DIR=$B/colgrep timeout 200 claude -p --model haiku --permission-mode auto --output-format stream-json --verbose "$(cat $B/prompt.txt)" < /dev/null > $B/run.jsonl 2> $B/run.err
python3 -c "
import json,sys
for l in open('$B/run.jsonl'):
    d=json.loads(l)
    if d.get('type')=='result': print('COST',d['total_cost_usd']); print(d['result'][:1500])"
