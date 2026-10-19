"""Count the kinds of 'user'-type records in a transcript: genuine human text versus platform text. usage: python3 -I platform_counts.py <session.jsonl> (read-only)"""
import json,sys,collections
c=collections.Counter()
for l in open(sys.argv[1]):
    d=json.loads(l)
    if d['type']!='user': continue
    if d.get('isSidechain'): c['sidechain']+=1; continue
    cont=d['message']['content']
    if isinstance(cont,list) and any(isinstance(x,dict) and x.get('type')=='tool_result' for x in cont): c['tool_result']+=1; continue
    o=(d.get('origin') or {}).get('kind')
    txt=cont if isinstance(cont,str) else ' '.join(x.get('text','') for x in cont if isinstance(x,dict))
    t=txt.strip()
    if d.get('isMeta'): c['isMeta (skill text, image note)']+=1
    elif o=='human' and t.startswith('<command-message>'): c['human slash command']+=1
    elif o=='human': c['human prompt (typed or button click)']+=1
    elif o=='peer': c['peer: subagent hand-back or other-session message']+=1
    elif o=='task-notification': c['task-notification']+=1
    elif t.startswith('[Request interrupted'): c['interrupt marker (human act)']+=1
    elif '<side-sessions-event>' in t[:40]: c['side-sessions-event']+=1
    else: c['other: '+t[:30].replace('\n',' ')]+=1
print(sys.argv[1].split('/')[-1][:8],sum(c.values()),dict(c))
