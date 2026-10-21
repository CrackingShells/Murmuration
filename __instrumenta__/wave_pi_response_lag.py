#!/usr/bin/env python3
"""Compute, for each worker hand-back that reached the PI, the lag from the hand-back message to the PI's first assistant record, and to its first Agent/SendMessage dispatch after it, from a PI transcript; prints TSV (lag in seconds).

Usage: wave_pi_response_lag.py PI_SESSION.jsonl
"""
import json,sys,re,datetime as dt
JST=dt.timezone(dt.timedelta(hours=9))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(JST)
ev=[]
for l in open(sys.argv[1]):
    d=json.loads(l)
    if not d.get('timestamp'): continue
    t=ts(d['timestamp']); ty=d['type']; m=d.get('message') if isinstance(d.get('message'),dict) else {}; c=m.get('content')
    if ty=='queue-operation' and d.get('operation')=='enqueue' and '<agent-message from=' in (d.get('content') or ''):
        who=re.search(r'from="([^"]+)"',d['content']).group(1); ev.append((t,'HB',who))
    elif ty=='assistant' and isinstance(c,list):
        disp=[b['name'] for b in c if b.get('type')=='tool_use' and b['name'] in('Agent','SendMessage')]
        ev.append((t,'A','D' if disp else ''))
print('handback_from\tat\tlag_first_assistant_s\tlag_first_dispatch_s')
for i,(t,k,w) in enumerate(ev):
    if k!='HB': continue
    a=next(((e[0]-t).total_seconds() for e in ev[i+1:] if e[1]=='A'),None)
    d=next(((e[0]-t).total_seconds() for e in ev[i+1:] if e[1]=='A' and e[2]=='D'),None)
    print(f"{w}\t{t:%H:%M:%S}\t{a:.0f}\t{'' if (d is None or d>180) else f'{d:.0f}'}")
