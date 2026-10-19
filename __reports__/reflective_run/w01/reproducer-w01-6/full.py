import json,glob,sys
P='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
def L(s): return [json.loads(l) for l in open(glob.glob(P+s+'*.jsonl')[0])]
def txt(d):
    c=d.get('message',{}).get('content')
    if isinstance(c,str): return c
    return '\n'.join(b.get('text','') for b in c or [] if isinstance(b,dict) and b.get('type')=='text')
sess,idx0,idx1=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
data=L(sess)
for i in range(idx0,idx1+1):
    d=data[i]
    if d.get('type') in('assistant','user') and not d.get('isSidechain'):
        t=txt(d).strip()
        if t: print(f'#{i} {d["type"]} {d.get("timestamp")} [{len(t.split())}w]\n{t[:int(sys.argv[4]) if len(sys.argv)>4 else 3000]}\n')
