import json,sys,glob
base='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
for sid in ['566fa912-7009-421a-9d79-11145e2b8db9','82e8a947-1a0c-441c-bc39-df8e2e5fa743']:
    for l in open(base+sid+'.jsonl'):
        try: r=json.loads(l)
        except: continue
        c=r.get('message',{}).get('content')
        if isinstance(c,list):
            for b in c:
                if b.get('type')=='tool_use' and b['name'].endswith('wrap_up'):
                    print(sid[:8],r['timestamp'][:19],json.dumps(b['input'],ensure_ascii=False)[:900]);print()
