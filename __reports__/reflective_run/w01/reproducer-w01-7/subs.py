import json,glob,csv,os
base='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
A=list(csv.DictReader(open('../explorer-w01-d/asks.csv')))
def spans(sid):
    out=[]
    for f in glob.glob(base+sid+'/subagents/*.jsonl'):
        ts=[]
        for l in open(f):
            try: r=json.loads(l)
            except: continue
            if r.get('timestamp'): ts.append(r['timestamp'])
        if ts: out.append((min(ts),max(ts),os.path.basename(f)))
    return out
S={'G':spans('566fa912-7009-421a-9d79-11145e2b8db9'),'D':spans('82e8a947-1a0c-441c-bc39-df8e2e5fa743')}
print({k:len(v) for k,v in S.items()})
for i,a in enumerate(A):
    t=a['wrap_up_ts_utc']
    n=[s for s in S[a['session']] if s[0]<t<s[1]]
    print(i,a['session'],t[:19],'running by span:',len(n),'explorer col:',a['subagents_running'])
