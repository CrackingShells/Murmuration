import json,glob,os,re,sys,datetime as dt
UNTIL='2026-10-19T02:24:30Z'
D=os.path.expanduser('~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087')
def T(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00'))
def load(f):
    out=[]
    for l in open(f):
        try: r=json.loads(l)
        except: continue
        if r.get('timestamp') and T(r['timestamp'])>T(UNTIL): continue
        out.append(r)
    return out
def ctx(u): return u.get('input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0)
def analyse(f):
    recs=load(f)
    # per message id: last usage seen (max ctx), first ts
    mids=[];mu={}
    for r in recs:
        if r['type']=='assistant':
            i=r['message']['id']
            if i not in mu: mids.append(i); mu[i]=[r['timestamp'],r['message']['usage']]
            else:
                if ctx(r['message']['usage'])>=ctx(mu[i][1]): mu[i][1]=r['message']['usage']
    wakes=[r for r in recs if r['type']=='user' and r.get('origin')]
    res=[]
    for w in wakes:
        wt=T(w['timestamp'])
        before=[r for r in recs if r['type'] in('assistant','user') and T(r['timestamp'])<wt and not r.get('origin')]
        last=max(T(r['timestamp']) for r in before)
        nb=len({r['message']['id'] for r in before if r['type']=='assistant'})
        after=[i for i in mids if T(mu[i][0])>wt]
        if not after: continue
        u=mu[after[0]][1]
        res.append(dict(turns_before=nb,gap=(wt-last).total_seconds(),ctx=ctx(u),cw=u.get('cache_creation_input_tokens',0),cr=u.get('cache_read_input_tokens',0),turns_after=len(after),wake=w['timestamp']))
    return len(mids),res
if __name__=='__main__':
    for a in ['ac6c27171353e66ed','a1f4458ce75dacdec','a996dba2994d53126']:
        n,res=analyse(f'{D}/subagents/agent-{a}.jsonl')
        print(a,'total turns',n)
        for r in res: print('  ',r, 'cw share %.4f'%(r['cw']/r['ctx']), 'exposure %.3f'%(r['ctx']*2.30/1e6))
