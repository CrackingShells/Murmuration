import json,sys,re,statistics
base='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
tot={}
for sid in ['566fa912-7009-421a-9d79-11145e2b8db9','82e8a947-1a0c-441c-bc39-df8e2e5fa743','3ccc590f-0187-4f79-b7af-4955944f1374','2947f9dc-1c3a-452b-97a5-39d4510a1271']:
    wraps=[];prompts=[]
    for i,l in enumerate(open(base+sid+'.jsonl')):
        d=json.loads(l)
        if d.get('type')=='assistant':
            for b in d['message']['content']:
                if b.get('type')=='tool_use' and b['name']=='mcp__ccd_turn__wrap_up':
                    wraps.append((i,b['input']))
        if d.get('type')=='queue-operation' and d.get('operation')=='enqueue' and d.get('content'):
            prompts.append((i,d['timestamp'],str(d['content'])))
    withask=[w for w in wraps if w[1].get('ask')]
    acts=[a['message'] for w in wraps for a in w[1].get('actions',[])]
    hits=[(ts,p[:80]) for i,ts,p in prompts if p.strip() in acts]
    rl=[len(w[1].get('recap','').split()) for w in wraps]
    print(sid[:8],'wraps',len(wraps),'with ask',len(withask),'n actions',len(acts),'button clicks matched in prompts',len(hits),'recap words median',statistics.median(rl) if rl else None,'max',max(rl) if rl else None)
    for h in hits: print('   click',h)
