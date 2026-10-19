import json, sys, csv, glob
P='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
rows={r['uuid'][:8]:r for r in csv.DictReader(open('../explorer-w01-d/prompts.csv'))}
cache={}
def load(s):
    if s not in cache:
        fn=glob.glob(P+s+'*.jsonl')[0]
        cache[s]=[json.loads(l) for l in open(fn)]
    return cache[s]
def text_of(m):
    c=m.get('message',{}).get('content')
    if isinstance(c,str): return c
    return '\n'.join(b.get('text','') for b in c or [] if isinstance(b,dict) and b.get('type')=='text')
def show(u8,maxprev=1800,nprev=2):
    r=rows[u8]
    full=[k for k in rows if k==u8][0]
    uid=r['uuid']
    sid=r['session']
    sess={'G':'566fa912','D':'82e8a947'}.get(sid,sid)
    data=load(sess)
    idx=[i for i,d in enumerate(data) if d.get('uuid')==uid]
    print('='*100); print(u8,r['cls'],r['phase'],r['ts_utc'],'idx',idx)
    if not idx: print('NOT FOUND',sid); return
    i=idx[0]
    print('HUMAN:',r['human_text'][:1500])
    k=0
    for j in range(i-1,-1,-1):
        d=data[j]
        if d.get('type')=='assistant' and not d.get('isSidechain'):
            t=text_of(d).strip()
            if t:
                print(f'--- PI text block (idx {j}, {d.get("timestamp")}, {len(t.split())} words):'); print(t[:maxprev] + (' [...]' if len(t)>maxprev else '')); k+=1
                if k>=nprev: break
for u in sys.argv[1:]: show(u)
