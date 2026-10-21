#!/usr/bin/env python3
"""List a PI session transcript as time-ordered events (JST): assistant tool calls with output tokens, text blocks, queue notifications, user messages; writes to stdout. With --usage prints instead the per-request cache read/create tokens (one row per distinct message id).

Usage: wave_pi_event_list.py SESSION.jsonl [--usage]
"""
import json,sys,datetime as dt
JST=dt.timezone(dt.timedelta(hours=9))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(JST)
usage='--usage' in sys.argv
seen=set(); prev=None
if usage: print('time\tgap_before_s\tcache_read\tcache_create\tinput\toutput')
for l in open(sys.argv[1]):
    d=json.loads(l)
    if not d.get('timestamp'): continue
    t=ts(d['timestamp']); hh=t.strftime('%H:%M:%S'); ty=d['type']; m=d.get('message') if isinstance(d.get('message'),dict) else {}; c=m.get('content')
    if usage:
        if ty=='assistant' and m.get('id') not in seen:
            seen.add(m.get('id')); u=m.get('usage',{}); gap=(t-prev).total_seconds() if prev else 0
            print(f"{hh}\t{gap:.0f}\t{u.get('cache_read_input_tokens')}\t{u.get('cache_creation_input_tokens')}\t{u.get('input_tokens')}\t{u.get('output_tokens')}")
        prev=t; continue
    if ty=='queue-operation': print(hh,'Q',d.get('operation'),(d.get('content') or '')[:100].replace('\n',' '))
    elif ty=='assistant' and isinstance(c,list):
        for b in c:
            if b['type']=='tool_use':
                i=b['input']; print(hh,'A TU',b['name'],(i.get('name') or i.get('to') or i.get('description') or i.get('command') or json.dumps(i))[:110].replace('\n',' '),'out_tok=%s'%m.get('usage',{}).get('output_tokens'))
            elif b['type']=='text': print(hh,'A TXT',len(b['text']),b['text'][:80].replace('\n',' '))
            elif b['type']=='thinking': print(hh,'A THINK')
    elif ty=='user' and isinstance(c,list):
        for b in c:
            if b['type']=='text': print(hh,'U TXT',b['text'][:140].replace('\n',' '))
    elif ty=='user' and isinstance(c,str): print(hh,'U STR',c[:120].replace('\n',' '))
    elif ty=='system': print(hh,'SYS',d.get('subtype'),str(d.get('hookInfos') or d.get('content'))[:100])
