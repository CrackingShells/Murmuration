import json,sys
base='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
sid=sys.argv[1]; target=int(sys.argv[2]); n=int(sys.argv[3]) if len(sys.argv)>3 else 1; mx=int(sys.argv[4]) if len(sys.argv)>4 else 3000
msgs=[]
for i,l in enumerate(open(base+sid+'.jsonl')):
    if i>=target: break
    d=json.loads(l)
    if d.get('type')=='assistant':
        t='\n'.join(b.get('text','') for b in d['message']['content'] if b.get('type')=='text').strip()
        if t: msgs.append((i,t))
for i,t in msgs[-n:]:
    print('--- assistant line',i,'len',len(t)); print(t[:mx]); print()
