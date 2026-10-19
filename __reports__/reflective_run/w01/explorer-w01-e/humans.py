import json,sys,re
base='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
for sid in sys.argv[1:]:
    out=open(f'human_{sid[:8]}.tsv','w')
    n=0
    for i,l in enumerate(open(base+sid+'.jsonl')):
        try:d=json.loads(l)
        except: continue
        if d.get('type')!='user': continue
        m=d.get('message',{})
        c=m.get('content')
        if isinstance(c,str): t=c
        else:
            t='\n'.join(b.get('text','') for b in c if b.get('type')=='text')
            if not t.strip(): continue
        if d.get('isMeta') or d.get('toolUseResult'): continue
        t=t.strip()
        if t.startswith('<system-reminder>') or t.startswith('<task-notification') or t.startswith('<local-command') : kind='sys'
        else: kind='human'
        n+=1
        out.write(json.dumps({'line':i,'ts':d.get('timestamp'),'kind':kind,'len':len(t),'text':t})+'\n')
    print(sid[:8],n)
