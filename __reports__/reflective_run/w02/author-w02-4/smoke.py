#!/usr/bin/env python3
"""Smoke-start measurements for the non-explorer workers: smoke.py (reads only)."""
import glob, json, os
for tag in ['new_author', 'new_reproducer', 'new_proof-adversary', 'ctl_author']:
    e = json.load(open('e_%s.json' % tag))
    g = glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents/agent-*.jsonl" % e['session_id']))
    R = [json.loads(l) for l in open(g[0])]
    a = [x for x in R if x['type'] == 'assistant']; u = a[0]['message']['usage']
    ctx = u['input_tokens'] + u.get('cache_read_input_tokens', 0) + u.get('cache_creation_input_tokens', 0)
    lst = [len(x['attachment']['content']) for x in R if x.get('type') == 'attachment' and x['attachment'].get('type') == 'skill_listing']
    pre = any('Base directory for this skill' in json.dumps(x['message']['content']) for x in R if x['type'] == 'user')
    print(tag, 'first_turn_ctx', ctx, 'listing_chars', lst, 'preloaded', pre, 'usd', round(e['total_cost_usd'], 4))
