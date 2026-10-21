#!/usr/bin/env python3
"""Compute a PI-thread wall-clock timeline (model, tool, idle intervals) from a Claude Code session transcript; writes a per-interval TSV and prints class totals.

Usage: wave_timeline_pi.py TRANSCRIPT.jsonl OUT.tsv
Intervals (JST): model = input-record -> assistant record; tool = tool_use -> tool_result (foreground);
idle = after an assistant stop with no pending tool until the next user/queue record; bg_ack = Agent calls (returns at once).
"""
import json, sys, datetime as dt, collections
JST = dt.timezone(dt.timedelta(hours=9))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(JST)
rows=[]
for i,l in enumerate(open(sys.argv[1])):
    d=json.loads(l)
    if d.get('timestamp') and d.get('type') in ('assistant','user','queue-operation','system','attachment'):
        d['_t']=ts(d['timestamp']); d['_i']=i; rows.append(d)
rows.sort(key=lambda d:(d['_t'],d['_i']))
# map tool_use id -> (t, name, desc)
tu={}; tr={}
for d in rows:
    m=d.get('message') if isinstance(d.get('message'),dict) else {}
    c=m.get('content')
    if isinstance(c,list):
        for b in c:
            if b.get('type')=='tool_use': tu[b['id']]=(d['_t'],b['name'],json.dumps(b['input'])[:140],m.get('id'))
            if b.get('type')=='tool_result' and d['type']=='user': tr[b['tool_use_id']]=d['_t']
# Walk: state machine
out=[]; last_t=rows[0]['_t']; state='start'
pending=set()
def emit(a,b,cls,lab):
    if (b-a).total_seconds()>=0: out.append((a,b,cls,lab))
prev=rows[0]
for d in rows[1:]:
    t=d['_t']; ty=d['type']
    m=d.get('message') if isinstance(d.get('message'),dict) else {}
    c=m.get('content')
    kinds=set()
    if isinstance(c,list):
        for b in c:
            kinds.add(b.get('type'))
    if ty=='assistant':
        names=[b['name'] for b in c if b.get('type')=='tool_use'] if isinstance(c,list) else []
        emit(prev['_t'],t,'model',','.join(names) or ','.join(sorted(kinds)))
        prev=d
    elif ty=='user':
        is_tr='tool_result' in kinds
        if is_tr:
            ids=[b['tool_use_id'] for b in c if b.get('type')=='tool_result']
            nm=','.join(tu[i][1] for i in ids if i in tu)
            # find the matching tool_use time
            t0=min((tu[i][0] for i in ids if i in tu),default=prev['_t'])
            # tool interval from max(prev tool_use ts) to result
            emit(max(prev['_t'],t0) if prev['type']=='assistant' else prev['_t'],t,'tool',nm)
        else:
            emit(prev['_t'],t,'idle','user/notif input')
        prev=d
    elif ty=='queue-operation':
        if d.get('operation')=='enqueue':
            emit(prev['_t'],t,'idle','queue enqueue'); prev=d
    # attachments/system ignored for state
import csv
with open(sys.argv[2],'w') as f:
    w=csv.writer(f,delimiter='\t'); w.writerow(['start_jst','end_jst','secs','class','label'])
    for a,b,cl,lb in out: w.writerow([a.strftime('%H:%M:%S.%f')[:-3],b.strftime('%H:%M:%S.%f')[:-3],round((b-a).total_seconds(),2),cl,lb])
tot=collections.Counter()
for a,b,cl,lb in out: tot[cl]+=(b-a).total_seconds()
print({k:round(v) for k,v in tot.items()}, 'span', rows[0]['_t'].strftime('%H:%M:%S'), rows[-1]['_t'].strftime('%H:%M:%S'))
