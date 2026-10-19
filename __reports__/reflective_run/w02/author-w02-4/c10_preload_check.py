#!/usr/bin/env python3 -I
"""w02-c10: is the spend sentence in the skill text a worker is given at start? usage: SCRATCH=<dir> run from SCRATCH after
`for a in explorer author reproducer proof-adversary; do ./run_other.sh new $a; done` (setup.sh first). Reads only."""
import glob, json, os
for a in ['explorer', 'author', 'reproducer', 'proof-adversary']:
    e = json.load(open('e_new_%s.json' % a))
    g = glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents/agent-*.jsonl" % e['session_id']))[0]
    R = [json.loads(l) for l in open(g)]
    pre = [json.dumps(x['message']['content']) for x in R if x['type'] == 'user' and 'Base directory for this skill' in json.dumps(x['message']['content'])]
    print(a, 'preloaded', bool(pre), 'sentence_in_preload', any('spend figure shown to a worker is the whole' in t for t in pre))
