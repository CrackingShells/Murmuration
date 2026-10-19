import json,sys,re
base='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
sid=sys.argv[1]; start=int(sys.argv[2]) if len(sys.argv)>2 else 0
out=[]
for i,l in enumerate(open(base+sid+'.jsonl')):
    if i<start: continue
    try:d=json.loads(l)
    except: continue
    if d.get('type')!='user': continue
    m=d.get('message',{}); c=m.get('content')
    if isinstance(c,str): t=c
    else:
        if any(b.get('type')=='tool_result' for b in c): continue
        t='\n'.join(b.get('text','') for b in c if b.get('type')=='text')
    t=re.sub(r'<system-reminder>.*?</system-reminder>','',t,flags=re.S)
    t=re.sub(r'<task-notification>.*?</task-notification>','',t,flags=re.S).strip()
    if not t: continue
    out.append({'line':i,'ts':d.get('timestamp'),'len':len(t),'text':t})
json.dump(out,open(f'prompts_{sid[:8]}.json','w'),indent=0)
for o in out: print(o['line'],o['ts'],o['len'],'|',o['text'][:100].replace('\n',' '))
