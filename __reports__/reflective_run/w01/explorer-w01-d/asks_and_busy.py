"""For a session: (1) every mcp__ccd_turn__wrap_up call with its ask/actions, the next human prompt, whether that prompt is a verbatim
click on one of the offered actions, and the latency; (2) number of subagents running when each human prompt arrived.
usage: python3 -I asks_and_busy.py <session.jsonl> <subagent_dir> <table.json> <out.json>   (read-only)"""
import json,sys,glob,os
from datetime import datetime,timedelta
def ts(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
sess,subdir,tablef,outf=sys.argv[1:5]
table=json.load(open(tablef))
prompts=[r for r in table if r['channel'] in('A','B')]
wraps=[]
for i,l in enumerate(open(sess)):
    d=json.loads(l)
    if d.get('type')=='assistant' and not d.get('isSidechain'):
        for b in d['message']['content']:
            if b.get('type')=='tool_use' and b['name']=='mcp__ccd_turn__wrap_up':
                inp=b['input']; wraps.append(dict(line=i,ts=d['timestamp'],uuid=d['uuid'],recap=inp.get('recap',''),ask=inp.get('ask'),actions=inp.get('actions') or [],blocked=inp.get('blocked',False)))
# subagent spans
spans=[]
for f in glob.glob(os.path.join(subdir,'agent-*.jsonl')):
    a=b=None
    for l in open(f):
        try: d=json.loads(l)
        except: continue
        t=d.get('timestamp')
        if t:
            a=a or t; b=t
    meta=f.replace('.jsonl','.meta.json')
    m=json.load(open(meta)) if os.path.exists(meta) else {}
    spans.append((a,b,os.path.basename(f),m.get('agentType') or m.get('description','')))
for w in wraps:
    nxt=next((p for p in prompts if p['ts']>w['ts']),None)
    w['next_prompt_uuid']=nxt['uuid'] if nxt else None
    if nxt:
        w['latency_min']=round((ts(nxt['ts'])-ts(w['ts']))/timedelta(minutes=1),1)
        idx=[k for k,a in enumerate(w['actions']) if a.get('message','').strip()==nxt['text'].strip()]
        w['click_action_index']=idx[0] if idx else None
        w['verbatim_click']=bool(idx)
        w['action_labels']=[a.get('label') for a in w['actions']]
    w['subagents_running_after_wrap']=sum(1 for a,b,_,_ in spans if a<=w['ts']<=b)
for p in prompts:
    p['subagents_running']=sum(1 for a,b,_,_ in spans if a<=p['ts']<=b)
json.dump(dict(wraps=wraps,prompt_busy={p['uuid']:p['subagents_running'] for p in prompts},n_subagents=len(spans)),open(outf,'w'),ensure_ascii=False,indent=1)
print('wraps',len(wraps),'with ask',sum(1 for w in wraps if w['ask']),'verbatim clicks',sum(1 for w in wraps if w.get('verbatim_click')),'subagents',len(spans))
