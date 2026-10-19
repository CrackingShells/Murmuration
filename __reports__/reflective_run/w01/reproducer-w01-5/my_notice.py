import json,os,re,datetime as dt
from my_check import T,UNTIL,D
recs=[json.loads(l) for l in open(D+'.jsonl')]
seen=set()
for r in recs:
    if r.get('timestamp') and T(r['timestamp'])>T(UNTIL): continue
    s=json.dumps(r)
    for m in re.finditer(r'<task-notification>.*?</task-notification>',s.replace('\\n',' ')):
        t=m.group(0)
        tid=re.search(r'task-id>([^<\\]+)',t)
        key=tid.group(1) if tid else t[:80]
        if key in seen: continue
        seen.add(key)
        print(r['timestamp'],r['type'],key,re.sub(r'\s+',' ',t)[:230])
