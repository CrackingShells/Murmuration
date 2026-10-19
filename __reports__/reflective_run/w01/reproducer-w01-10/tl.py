import json,sys,collections
p=sys.argv[1]
W='/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e'
M='/Users/hacker/Documents/src/CrackingShells/Murmuration'
rows=[]
for i,l in enumerate(open(p),1):
    try:d=json.loads(l)
    except Exception: continue
    rows.append((i,d.get('timestamp'),d.get('cwd'),d.get('type'),(d.get('attachment') or {}).get('type') if isinstance(d.get('attachment'),dict) else None))
print('total lines',i,'records',len(rows))
c=collections.Counter(r[2] for r in rows);print(c)
def lab(c):
    return 'W' if c==W else 'M' if c==M else c
c2=collections.Counter(lab(r[2]) for r in rows);print(c2)
first=next(r for r in rows if r[2]==M);print('first main',first)
last=[r for r in rows if r[2]==M][-1];print('last main',last)
for a,b in [('2026-10-19T01:56:00','2026-10-19T01:57:10'),('2026-10-19T02:01:30','2026-10-19T02:04:40')]:
    for r in rows:
        if r[1] and a<=r[1]<=b: print(r[0],r[1],lab(r[2]),r[3],r[4])
# user prompts
for i,l in enumerate(open(p),1):
    d=json.loads(l)
    if d.get('type')=='user' and not d.get('isSidechain') and isinstance(d['message'].get('content'),str):
        print('PROMPT',i,d['timestamp'],lab(d.get('cwd')),d['message']['content'][:60].replace('\n',' '))
