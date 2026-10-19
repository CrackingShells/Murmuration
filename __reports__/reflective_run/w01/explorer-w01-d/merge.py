"""Merge the extraction tables, the hand classification and the asks into prompts.csv, asks.csv and summary.json.
usage: python3 -I merge.py <dir with *.table.json and *.asks.json> <out dir>   (reads classes.csv and asks_judgement.csv next to this script)"""
import json,csv,sys,os,statistics,collections
from datetime import datetime,timedelta
here=os.path.dirname(os.path.abspath(__file__))
src,out=sys.argv[1:3]
SESS={'G':'566fa912-7009-421a-9d79-11145e2b8db9','D':'82e8a947-1a0c-441c-bc39-df8e2e5fa743'}
def ts(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
cls={r['uuid8']:r for r in csv.DictReader(open(os.path.join(here,'classes.csv')))}
rows=[];seen={};seenw=set()
allclick={}
asks_out=[]
aj={(r['session'],r['wrap_up_ts_utc']):r for r in csv.DictReader(open(os.path.join(here,'asks_judgement.csv')))}
for k,s in SESS.items():
    t=json.load(open(f'{src}/{s}.table.json')); a=json.load(open(f'{src}/{s}.asks.json'))
    actions=[(x['ts'],i,x['actions']) for x in a['wraps'] for i in [0]]
    msgs={}
    for w in a['wraps']:
        for j,ac in enumerate(w['actions']): msgs[ac['message'].strip()]=(w['ts'],ac['label'],j)
    prev=None;prevhuman=None
    for r in t:
        u8=r['uuid'][:8]
        if u8 in seen: prev=r['ts']; continue
        c=cls.get(u8)
        if c is None: print('UNCLASSIFIED',k,r['n'],r['text'][:60]); continue
        seen[u8]=1
        click=msgs.get(r['text'].strip())
        # last wrap_up recap before prompt
        rec=[w for w in a['wraps'] if w['ts']<r['ts']]
        recap=(rec[-1]['recap'] if rec else '')
        gap=round((ts(r['ts'])-ts(prev))/timedelta(minutes=1),1) if prev else ''
        prev=r['ts']
        think=r.get('think_gap_min','')
        busy=a['prompt_busy'].get(r['uuid'],'')
        state=''
        if r['channel'] in('A','B'):
            if r['channel']=='B' or (think!='' and think<1.0): state='mid-run'
            elif busy not in('',0): state='bg-subagents-running'
            else: state='idle'
        rows.append(dict(session=k,phase=c['phase'],uuid=r['uuid'],ts_utc=r['ts'],channel=r['channel'],state_at_prompt=state,
            verbatim_click=('yes:'+click[1]) if click else ('' if r['channel'] in('A','B') else ''),
            cls=c['cls'],who=c['who'],agent_asked=c['agent_asked'],gap_since_prev_human_min=gap,agent_idle_before_min=think,
            subagents_running=busy,main_turns_since_prev=r.get('asst_turns_since_prev_human',''),tool_calls_since_prev=r.get('tool_calls_since_prev_human',''),
            agent_dispatches_since_prev=r.get('agent_dispatches_since_prev_human',''),chars=len(r['text']),
            agent_had_shown=recap[:260].replace('\n',' '),human_text=r['text'][:420].replace('\n',' / '),note=c['note']))
    for w in a['wraps']:
        if w['uuid'] in seenw: continue
        seenw.add(w['uuid'])
        if w['ask']:
            j=aj.get((k,w['ts'][:19]))
            asks_out.append(dict(session=k,wrap_up_ts_utc=w['ts'],ask=w['ask'],options=' | '.join(w['action_labels']) if 'action_labels' in w else ' | '.join(x['label'] for x in w['actions']),blocked=w['blocked'],
              latency_to_next_human_prompt_min=w.get('latency_min',''),verbatim_click=('' if w.get('click_action_index') is None else w.get('click_action_index')),subagents_running=w['subagents_running_after_wrap'],
              judgement_class=j['class'] if j else 'UNLABELLED',why=j['why'] if j else ''))
cols=list(rows[0].keys())
with open(os.path.join(out,'prompts.csv'),'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
with open(os.path.join(out,'asks.csv'),'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(asks_out[0].keys()));w.writeheader();w.writerows(asks_out)
# summary
S={}
def cnt(rs,key): return dict(collections.Counter(r[key] for r in rs))
research=[r for r in rows if r['cls'] not in('ADMIN',) and r['channel']!='interrupt']
S['unique_rows']=len(rows)
S['by_channel']=cnt(rows,'channel')
S['genuine_prompts(excl interrupt,slashcmd)']=sum(1 for r in rows if r['channel'] in('A','B'))
S['by_phase']=cnt(rows,'phase')
S['by_cls']=cnt(rows,'cls')
S['by_who']=cnt(rows,'who')
S['clicks']=sum(1 for r in rows if r['verbatim_click'])
S['clicks_by_session']=cnt([r for r in rows if r['verbatim_click']],'session')
S['by_state']=cnt([r for r in rows if r['state_at_prompt']],'state_at_prompt')
S['cls_by_phase']={p:cnt([r for r in rows if r['phase']==p],'cls') for p in sorted({r['phase'] for r in rows})}
S['who_by_phase']={p:cnt([r for r in rows if r['phase']==p],'who') for p in sorted({r['phase'] for r in rows})}
S['agent_asked']=cnt(rows,'agent_asked')
S['asks']=len(asks_out);S['asks_by_class']=cnt(asks_out,'judgement_class')
S['asks_by_session']=cnt(asks_out,'session')
lat=[(a['judgement_class'],float(a['latency_to_next_human_prompt_min'])) for a in asks_out if a['latency_to_next_human_prompt_min']!='']
S['ask_latency_median_by_class']={c:round(statistics.median([l for cc,l in lat if cc==c]),1) for c in {c for c,_ in lat}}
S['ask_latency_list_by_class']={c:[l for cc,l in lat if cc==c] for c in {c for c,_ in lat}}
S['asks_declined_default']=sum(1 for a in asks_out if a['verbatim_click'] not in('',0,'0'))
S['asks_taken_idx0']=sum(1 for a in asks_out if a['verbatim_click'] in(0,'0'))
S['asks_answered_typed_or_other']=sum(1 for a in asks_out if a['verbatim_click']=='')
json.dump(S,open(os.path.join(out,'summary.json'),'w'),indent=1)
print(json.dumps(S,indent=1))
