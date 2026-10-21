#!/usr/bin/env python3
"""Per cell, sums input+cache tokens over all distinct model requests, and prints the tool calls (name, first 140 chars of input) of the session, from stdout.jsonl session ids and ~/.claude/projects transcripts; input: runs dir and optional cell names; output: stdout."""
import json,glob,os,sys
runs=sys.argv[1]; want=sys.argv[2:] or sorted(os.listdir(runs))
for c in want:
    so=os.path.join(runs,c,'stdout.jsonl'); sid=None
    for l in open(so): sid=json.loads(l).get('session_id',sid)
    tp=glob.glob(os.path.expanduser('~/.claude/projects/*/%s.jsonl'%sid))[0]
    by={}; calls=[]
    for l in open(tp):
        r=json.loads(l)
        if r.get('type')=='assistant':
            m=r['message']; u=m.get('usage') or {}
            by[m['id']]=u.get('input_tokens',0)+u.get('cache_creation_input_tokens',0)+u.get('cache_read_input_tokens',0)
            for b in m.get('content',[]):
                if b.get('type')=='tool_use': calls.append(b['name']+' '+json.dumps(b['input'])[:140])
    print(c,'per-request',list(by.values()),'sum',sum(by.values()))
    if len(want)<6:
        for x in calls: print('   ',x.replace('/private/tmp/murmuration-w07/author-w07-1/runs/',''))
