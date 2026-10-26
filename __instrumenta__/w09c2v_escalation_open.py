# Computes, from the PI transcripts (label=path lines in argv[1]) and my wakes.jsonl (argv[2]), for each reproducer ESCALATE hand-back whether the PI in the wake turn (a) opened the claim file __pondus__/<id>.md by view/query/Read, (b) named the claim id in any tool call, (c) states a decision word in its text; and the first earlier turn that touched the claim file by any tool call; prints one line per hand-back. Independent of w09c2_escalations.py.
import json,re,sys
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from w09c2v_extract import opened_paths
files=dict(l.strip().split('=',1) for l in open(sys.argv[1]) if '=' in l)
W=[json.loads(l) for l in open(sys.argv[2])]
DEC=re.compile(r'decid|decision|restat|supersed|accept|narrow|split|stands|withdr',re.I)
for w in W:
    if w['role']!='reproducer': continue
    esc=[x for x in w['body'].split('\n') if 'ESCALATE' in x]
    if not esc: continue
    m=re.search(r'w\d\d-c\d+',esc[0]) or re.search(r'w\d\d-c\d+',w['body'])
    cid=m.group(0)
    openedwake=[(p,k) for t in w['tus'] for p,k in opened_paths(t) if '__pondus__' in p and cid in p]
    anywake=[t['name'] for t in w['tus'] if 'pondus' in json.dumps(t['input']) and cid in json.dumps(t['input'])]
    dec=[bool(DEC.search(x)) and cid in x for x in w['texts']]
    # earlier turns: any tool_use (not SendMessage) in the same transcript before the wake naming pondus/<id>
    first=None
    for i,l in enumerate(open(files[w['lab']])):
        if i>=w['idx']: break
        if '"tool_use"' in l and ('__pondus__/'+cid) in l:
            d=json.loads(l)
            if d.get('type')!='assistant': continue
            for b in d['message'].get('content',[]):
                if b.get('type')=='tool_use' and ('__pondus__/'+cid) in json.dumps(b['input']):
                    ops=opened_paths({'name':b['name'],'input':b['input']})
                    if any(('__pondus__/'+cid) in p for p,_ in ops): first=(i,b['name']); break
            if first: break
    print(w['lab'],w['idx'],w['sender'],cid,'| wake: view/query/Read of claim file =',len(openedwake),'| id in any non-view tool call =',anywake,'| text states decision =',any(dec),'| earlier open (jsonl line, tool) =',first)
