"""Quote-replies: prompts that begin with '> ' quote a sentence of the agent's previous output. Locate the quoted sentence in the
agent's earlier output (assistant text block, or wrap_up recap/ask) and report where and how old it was.
usage: python3 -I quotes.py <session.jsonl> <prompts.csv> <session letter G|D> > quotes.csv   (read-only)"""
import json,sys,csv,re
from datetime import datetime
sess,pcsv,letter=sys.argv[1:4]
def ts(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
norm=lambda s:re.sub(r'[\s’‘“”*`]+',' ',s).strip().lower()
outs=[]
for i,l in enumerate(open(sess)):
    d=json.loads(l)
    if d['type']!='assistant' or d.get('isSidechain'): continue
    for b in d['message']['content']:
        if b.get('type')=='text' and b['text'].strip(): outs.append((d['timestamp'],'text',b['text']))
        if b.get('type')=='tool_use' and b['name']=='mcp__ccd_turn__wrap_up':
            outs.append((d['timestamp'],'wrap_up',b['input'].get('recap','')+' '+(b['input'].get('ask') or '')))
w=csv.writer(sys.stdout);w.writerow(['session','uuid8','ts_utc','quoted_first_chars','found_in','agent_output_age_min','quote_len_chars','reply_len_chars_truncated_at_420'])
for r in csv.DictReader(open(pcsv)):
    if r['session']!=letter: continue
    t=r['human_text']
    if not t.startswith('>'): continue
    q=t[1:].split(' / ')[0].strip()
    nq=norm(q)[:40]
    hit=None
    for ots,kind,txt in outs:
        if ots<r['ts_utc'] and nq and nq in norm(txt): hit=(ots,kind)
    w.writerow([r['session'],r['uuid'][:8],r['ts_utc'][:19],q[:70],hit[1] if hit else 'NOT FOUND',round((ts(r['ts_utc'])-ts(hit[0])).total_seconds()/60,1) if hit else '',len(q),len(t)])
