import sys; sys.path.insert(0,"/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-5")
import json
from my_check import load,D,T
def cost(u,pin=2.0,pout=10.0,pr=0.2):
    cc=u.get('cache_creation',{}) or {}
    w5=cc.get('ephemeral_5m_input_tokens',u.get('cache_creation_input_tokens',0)); w1=cc.get('ephemeral_1h_input_tokens',0)
    return (u.get('input_tokens',0)*pin + w5*pin*1.25 + w1*pin*2 + u.get('cache_read_input_tokens',0)*pr + u.get('output_tokens',0)*pout)/1e6, w1
for a in ['ac6c27171353e66ed','a1f4458ce75dacdec','a996dba2994d53126']:
    recs=load(f'{D}/subagents/agent-{a}.jsonl')
    best={}
    for r in recs:
        if r['type']=='assistant':
            i=r['message']['id']; u=r['message']['usage']
            if i not in best or u.get('output_tokens',0)>=best[i].get('output_tokens',0): best[i]=u
    tot=sum(cost(u)[0] for u in best.values()); w1=sum(cost(u)[1] for u in best.values())
    outs=sum(u.get('output_tokens',0) for u in best.values())
    print(a,len(best),'run USD %.3f'%tot,'1h writes',w1,'output cost share %.3f'%(outs*10/1e6/tot))
