import json, glob, os, collections
P=os.path.expanduser("~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary")
PR={"claude-opus-5-5":(4,20,0.20,5,8),"claude-sonnet-5-5":(2,10,0.10,2.5,4),"claude-fable-5-1":(10,50,0.25,12.5,20),"claude-haiku-5-5":(0.10,0.5,0.01,0.125,0.2)}
def usd(u,model):
    p=PR.get(model); 
    if not p: return 0
    cc=u.get("cache_creation") or {}; w1=cc.get("ephemeral_1h_input_tokens",0); w5=cc.get("ephemeral_5m_input_tokens",0); t=u.get("cache_creation_input_tokens",0)
    if w1+w5!=t: w5+=t-w1-w5
    return (u.get("input_tokens",0)*p[0]+u.get("output_tokens",0)*p[1]+u.get("cache_read_input_tokens",0)*p[2]+w5*p[3]+w1*p[4])/1e6
perfile={}; owned={}; cs=0
for f in glob.glob(P+"/**/*.jsonl",recursive=True):
    for l in open(f,errors="replace"):
        try:r=json.loads(l)
        except: continue
        if r.get("type")=="cost-state": cs+=r["totalCostUSD"]; continue
        if r.get("type")!="assistant": continue
        m=r.get("message") or {}; u=m.get("usage"); mid=m.get("id")
        if not u or not mid: continue
        for d,k in ((perfile,(f,mid)),(owned,(r["sessionId"],mid))):
            if k not in d or u.get("output_tokens",0)>=d[k][0].get("output_tokens",0): d[k]=(u,m.get("model"))
tot=lambda d:sum(usd(u,m) for u,m in d.values())
print("cost-state sum",round(cs,2),"| per-file rule msgs",len(perfile),"USD",round(tot(perfile),2),"x",round(tot(perfile)/cs,3),"| owned rule msgs",len(owned),"USD",round(tot(owned),2),"x",round(tot(owned)/cs,3))
for name,d in (("perfile",perfile),("owned",owned)):
    s=collections.Counter()
    for u,m in d.values():
        s["cw"]+=u.get("cache_creation_input_tokens",0); s["cr"]+=u.get("cache_read_input_tokens",0); s["out"]+=u.get("output_tokens",0)
    print(name,dict(s))
