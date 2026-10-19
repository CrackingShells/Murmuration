import json,sys
f=sys.argv[1]; lo=sys.argv[2]; hi=sys.argv[3]
for l in open(f):
    try: r=json.loads(l)
    except: continue
    ts=r.get('timestamp','')
    if not (lo<=ts<=hi): continue
    m=r.get('message',{})
    c=m.get('content')
    kinds=[]
    if isinstance(c,list):
        for b in c:
            if b.get('type')=='tool_use': kinds.append('TOOL:'+b['name'])
            elif b.get('type')=='text': kinds.append('text:'+b['text'][:100].replace('\n',' '))
            elif b.get('type')=='tool_result': kinds.append('result')
    elif isinstance(c,str): kinds.append('str:'+c[:100].replace('\n',' '))
    print(ts[:19], r.get('type'), r.get('isSidechain'), kinds)
