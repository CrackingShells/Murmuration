import sys; sys.path.insert(0,"/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-5")
import json,datetime as dt
from my_check import D,T,UNTIL
recs=[json.loads(l) for l in open(D+'.jsonl')]
best={}
for r in recs:
    if r['type']=='assistant' and r.get('timestamp') and T(r['timestamp'])<=T(UNTIL):
        i=r['message']['id']; u=r['message']['usage']
        if i not in best or u.get('output_tokens',0)>=best[i][1].get('output_tokens',0): best[i]=(r['timestamp'],u,r['message'].get('model'))
win={'b':('02:12:35.413','02:12:43.123'),'c':('02:11:59.923','02:12:10.798'),'d':('02:17:05.638','02:17:37.562')}
for k,(a,b) in win.items():
    A=T('2026-10-19T'+a+'Z');B=T('2026-10-19T'+b+'Z')
    tot=0;n=0
    for i,(ts,u,m) in best.items():
        t=T(ts)
        if A<=t<=B:
            cc=u.get('cache_creation',{}) or {}
            w1=cc.get('ephemeral_1h_input_tokens',0); w5=cc.get('ephemeral_5m_input_tokens',0)
            c=(u.get('input_tokens',0)*4+w1*8+w5*5+u.get('cache_read_input_tokens',0)*0.2+u.get('output_tokens',0)*20)/1e6
            tot+=c;n+=1; print(k,ts,m,'%.4f'%c,u.get('cache_creation_input_tokens'),u.get('cache_read_input_tokens'),u.get('output_tokens'))
    print(k,'turns',n,'USD %.3f'%tot)
