#!/usr/bin/env python3
"""List tool calls longer than a threshold (tool_use -> tool_result wall time) in a session transcript and its subagent transcripts; prints TSV: agent, start JST, secs, tool, background flag, command head.

Usage: wave_long_tool_calls.py SESSION.jsonl SUBAGENT_DIR MIN_SECS [OUT.tsv]
"""
import json, sys, glob, os, datetime as dt
JST=dt.timezone(dt.timedelta(hours=9))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(JST)
def scan(path,name):
    tu={}; res=[]
    for l in open(path):
        d=json.loads(l)
        if not d.get('timestamp'): continue
        c=(d.get('message') or {}).get('content') if isinstance(d.get('message'),dict) else None
        if not isinstance(c,list): continue
        for b in c:
            if b.get('type')=='tool_use': tu[b['id']]=(ts(d['timestamp']),b['name'],b['input'])
            elif b.get('type')=='tool_result' and b['tool_use_id'] in tu:
                t0,nm,inp=tu[b['tool_use_id']]; s=(ts(d['timestamp'])-t0).total_seconds()
                res.append((name,t0,s,nm,inp))
    return res
sess,sd,mn=sys.argv[1],sys.argv[2],float(sys.argv[3])
allr=scan(sess,'PI')
for f in sorted(glob.glob(sd+'/agent-*.jsonl')):
    meta=json.load(open(f.replace('.jsonl','.meta.json')))
    allr+=scan(f,meta.get('name'))
allr.sort(key=lambda r:-r[2])
lines=[]
for n,t0,s,nm,inp in allr:
    if s<mn: break
    head=(inp.get('command') or inp.get('description') or inp.get('prompt') or json.dumps(inp))[:150].replace('\n',' ').replace('\t',' ')
    lines.append(f"{n}\t{t0:%H:%M:%S}\t{s:.0f}\t{nm}\t{'bg' if inp.get('run_in_background') else ''}\t{head}")
print('\n'.join(lines))
if len(sys.argv)>4: open(sys.argv[4],'w').write('agent\tstart\tsecs\ttool\tbg\thead\n'+'\n'.join(lines)+'\n')
