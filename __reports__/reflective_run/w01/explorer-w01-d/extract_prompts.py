"""Extract candidate human prompts (origin.kind == human) from a transcript, with the platform wrappers stripped.
usage: python3 -I extract_prompts.py <session.jsonl> > out.json   (read-only on the transcript)"""
import json,sys,re
SR=re.compile(r'<system-reminder>.*?</system-reminder>',re.S)
def text_of(c):
    if isinstance(c,str): return c
    return '\n'.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
out=[]
for i,l in enumerate(open(sys.argv[1])):
    d=json.loads(l)
    if d.get('type')!='user' or d.get('isSidechain'): continue
    o=d.get('origin')
    raw=text_of(d['message']['content'])
    if isinstance(d['message']['content'],list) and any(x.get('type')=='tool_result' for x in d['message']['content'] if isinstance(x,dict)): continue
    kind=(o or {}).get('kind') if o else None
    stripped=SR.sub('',raw).strip()
    out.append(dict(line=i,uuid=d['uuid'],ts=d['timestamp'],kind=kind,promptSource=d.get('promptSource'),turnOrigin=d.get('turnOrigin'),isMeta=d.get('isMeta',False),
        raw_len=len(raw),sr_len=len(raw)-len(SR.sub('',raw)),text=stripped,sr=SR.findall(raw)))
json.dump(out,sys.stdout)
