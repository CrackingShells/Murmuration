"""Build the human-prompt table for a session transcript (read-only).
usage: python3 -I build_table.py <session.jsonl> <out.json>
Channels of genuine human text, all with origin.kind == 'human' stamped by the harness:
  A  user entry (agent idle or turn boundary)
  B  attachment type queued_command (typed while the agent was running; delivered at next tool boundary)
Also recorded, not counted as prompts: interrupts ('[Request interrupted by user]'), slash-command invocations.
Platform text excluded: origin peer / task-notification, isMeta, <system-reminder> blocks inside the prompt, side-sessions-event.
"""
import json,sys,re
from datetime import datetime
SR=re.compile(r'<system-reminder>.*?</system-reminder>',re.S)
def ts(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
def text_of(c):
    if isinstance(c,str): return c
    return '\n'.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
rows=[];events=[]  # events: main-thread timeline
for i,l in enumerate(open(sys.argv[1])):
    d=json.loads(l); t=d.get('type')
    if d.get('isSidechain'): continue
    if t=='assistant':
        txt='';tools=[]
        for b in d['message']['content']:
            if b.get('type')=='text': txt+=b['text']
            elif b.get('type')=='tool_use': tools.append((b['name'],b['input'].get('subagent_type') or b['input'].get('description','')[:40] if isinstance(b['input'],dict) else ''))
        events.append(dict(i=i,kind='asst',ts=d['timestamp'],text=txt,tools=tools,stop=d['message'].get('stop_reason'),uuid=d['uuid']))
    elif t=='user':
        c=d['message']['content']
        if isinstance(c,list) and any(isinstance(x,dict) and x.get('type')=='tool_result' for x in c):
            events.append(dict(i=i,kind='toolres',ts=d['timestamp'])); continue
        raw=text_of(c); o=(d.get('origin') or {}).get('kind')
        st=SR.sub('',raw).strip()
        if d.get('isMeta'): events.append(dict(i=i,kind='meta',ts=d['timestamp'])); continue
        if o=='human':
            if st.startswith('<command-message>'): k='slashcmd'
            else: k='A'
        elif o is None and st.startswith('[Request interrupted'): k='interrupt'
        elif o is None and st.startswith('<command-message>'): k='slashcmd'
        elif o is None and st.startswith('<side-sessions-event>'): k='platform_side'
        else: k='platform_'+str(o)
        events.append(dict(i=i,kind=k,ts=d['timestamp'],uuid=d['uuid'],text=st,sr_len=len(raw)-len(st)))
    elif t=='attachment':
        a=d['attachment']
        if a.get('type')=='queued_command' and (a.get('origin') or {}).get('kind')=='human':
            events.append(dict(i=i,kind='B',ts=d['timestamp'],enq_ts=a.get('timestamp'),uuid=a.get('source_uuid') or d['uuid'],text=SR.sub('',a.get('prompt') if isinstance(a.get('prompt'),str) else text_of(a.get('prompt'))).strip(),sr_len=0))
        elif a.get('type')=='queued_command':
            events.append(dict(i=i,kind='platform_queued',ts=d['timestamp']))
# derive
out=[];prev=None;last_asst=None;last_text=None;since=dict(asst=0,tools=0,agents=0)
for e in events:
    if e['kind']=='asst':
        last_asst=e
        if e['text'].strip(): last_text=e
        since['asst']+=1; since['tools']+=len(e['tools']); since['agents']+=sum(1 for n,_ in e['tools'] if n in('Agent','Task'))
    elif e['kind'] in('A','B'):
        if e['kind']=='B' and e['text'] in [x['text'] for x in out]: continue
        r=dict(n=len(out)+1,line=e['i'],uuid=e['uuid'],ts=e['ts'],channel=e['kind'],text=e['text'],sr_len=e['sr_len'],
               enq_ts=e.get('enq_ts'))
        r['gap_since_prev_human_min']=round((ts(e['ts'])-ts(prev))/__import__('datetime').timedelta(minutes=1),1) if prev else None
        r['asst_turns_since_prev_human']=since['asst'];r['tool_calls_since_prev_human']=since['tools'];r['agent_dispatches_since_prev_human']=since['agents']
        if last_text: r['last_text_ts']=last_text['ts']; r['last_text_tail']=last_text['text'][-900:]; r['last_text_age_min']=round((ts(e['ts'])-ts(last_text['ts']))/__import__('datetime').timedelta(minutes=1),1)
        if last_asst:
            r['last_asst_ts']=last_asst['ts'];r['last_asst_stop']=last_asst['stop']
            r['think_gap_min']=round((ts(e['ts'])-ts(last_asst['ts']))/__import__('datetime').timedelta(minutes=1),1)
            r['last_asst_tail']=last_asst['text'][-700:]
            r['last_asst_text_len']=len(last_asst['text'])
        out.append(r);prev=e['ts'];since=dict(asst=0,tools=0,agents=0)
    elif e['kind'] in('interrupt','slashcmd'):
        out.append(dict(n=len(out)+1,line=e['i'],uuid=e['uuid'],ts=e['ts'],channel=e['kind'],text=e['text'][:300]))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
print(len(out),'rows; A',sum(r['channel']=='A' for r in out),'B',sum(r['channel']=='B' for r in out))
