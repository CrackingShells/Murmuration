import json,sys
from datetime import datetime
for f in sys.argv[1:]:
    recs=[json.loads(l) for l in open(f)]
    t0=None;turn=0;last=None
    print(f.split('/')[-1][:20])
    seen_msg=set()
    for i,r in enumerate(recs):
        if r.get('type')=='assistant':
            mid=r['message'].get('id')
            if mid in seen_msg: continue
            seen_msg.add(mid); turn+=1
            u=r['message']['usage']
            ctx=u['input_tokens']+u['cache_read_input_tokens']+u['cache_creation_input_tokens']
            last=(turn,ctx,u['cache_creation_input_tokens'],u['cache_read_input_tokens'])
        if r.get('type')=='attachment' and r['attachment'].get('type')=='skill_listing':
            ts=datetime.fromisoformat(r['timestamp'].replace('Z','+00:00'))
            if t0 is None:t0=ts
            print('  rec',i,'turn_before',turn,'t+%.0fs'%(ts-t0).total_seconds(),'last_asst(turn,ctx,cw,cr)',last)
    # next assistant after each
