#!/usr/bin/env python3
"""Print one worker transcript as a time-ordered event list (JST, model-gap and tool-duration per call); input: subagent .jsonl; output: stdout.

Usage: wave_worker_events.py AGENT.jsonl
"""
import json,sys,datetime as dt
JST=dt.timezone(dt.timedelta(hours=9))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(JST)
tu={}; prev=None
for l in open(sys.argv[1]):
    d=json.loads(l)
    if not d.get('timestamp'): continue
    t=ts(d['timestamp']); m=d.get('message') if isinstance(d.get('message'),dict) else {}
    c=m.get('content')
    if d['type']=='assistant' and isinstance(c,list):
        gap=(t-prev).total_seconds() if prev else 0
        for b in c:
            if b['type']=='tool_use':
                tu[b['id']]=t; i=b['input']
                print(f"{t:%H:%M:%S} model+{gap:5.0f}s  {b['name']}: {(i.get('description') or i.get('command') or json.dumps(i))[:130]!r}".replace('\\n',' '))
        prev=t
    elif d['type']=='user' and isinstance(c,list):
        for b in c:
            if b.get('type')=='tool_result' and b['tool_use_id'] in tu:
                s=(t-tu[b['tool_use_id']]).total_seconds()
                if s>=20: print(f"{t:%H:%M:%S}   -> tool took {s:.0f}s")
        prev=t
    elif d['type']=='user': prev=t
