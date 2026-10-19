import json,sys,glob,hashlib
for f in sys.argv[1:]:
    recs=[json.loads(l) for l in open(f)]
    out=[]
    for i,r in enumerate(recs):
        if r.get('type')=='attachment' and r['attachment'].get('type')=='skill_listing':
            a=r['attachment']
            # find previous non-attachment record
            j=i-1
            while j>=0 and recs[j].get('type')=='attachment': j-=1
            prev=recs[j] if j>=0 else {}
            pc=prev.get('message',{}).get('content')
            kind=''
            if isinstance(pc,list):
                kind=','.join(c.get('type','')+':'+str(c.get('name',''))[:30] for c in pc if isinstance(c,dict))
            out.append((i,a.get('isInitial'),a.get('skillCount'),hashlib.md5(json.dumps(a['names']).encode()).hexdigest()[:6],len(a['content']),prev.get('type'),kind[:80]))
    print(f.split('/')[-1],len(recs),len(out))
    for o in out: print('  ',o)
