import json,os,sys,glob,random,collections
R="/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/author-w01-2/runs"
K=[("input_tokens","inputTokens"),("output_tokens","outputTokens"),("cache_read_input_tokens","cacheReadInputTokens"),("cache_creation_input_tokens","cacheCreationInputTokens")]
def reqs(path):
    d={}
    for l in open(path,errors="replace"):
        try:j=json.loads(l)
        except: continue
        if j.get("type")!="assistant": continue
        m=j["message"]; k=j.get("requestId") or m.get("id")
        d[k]=(m.get("usage") or {}, m.get("stop_reason"))   # last record wins
    return d
def cell(c):
    b=R+"/"+c
    cj=json.load(open(b+"/cell.json"))
    res=[json.loads(l) for l in open(b+"/stdout.jsonl") if l.startswith("{") and '"type":"result"' in l.replace(' ','')]
    mu=res[-1]["modelUsage"]
    truth={k:sum(v[m] for v in mu.values()) for k,m in K}
    hs=[json.loads(l) for l in open(b+"/hooks/hooks.jsonl")]
    tp=[h for h in hs if h["event"]=="SessionStart"][0]["input"]["transcript_path"]
    pm=[h["input"].get("permission_mode") for h in hs if h["event"]=="SubagentStop"]
    files=[tp]+sorted(glob.glob(tp[:-6]+"/subagents/agent-*.jsonl"))
    tot=collections.Counter(); null_sub=0; nsub=0
    for f in files:
        rq=reqs(f)
        for u,s in rq.values():
            for k,_ in K: tot[k]+=u.get(k,0)
            if f!=tp:
                nsub+=1; null_sub+= s is None
    return dict(cell=c,bin=cj["bin"],pm=pm[0] if pm else None,mode=cj.get("mode"),think=cj.get("think"),length=cj.get("length"),
        diff={k:tot[k]-truth[k] for k,_ in K},nsubreq=nsub,nullsub=null_sub,nfiles=len(files)-1)
if __name__=="__main__":
    cells=sorted(os.listdir(R)); random.seed(20261019)
    info={}
    for c in cells:
        try:
            cj=json.load(open(R+"/"+c+"/cell.json"))
            hs=[json.loads(l) for l in open(R+"/"+c+"/hooks/hooks.jsonl")]
            pm=[h["input"].get("permission_mode") for h in hs if h["event"]=="SubagentStop"]
            info[c]=(cj["bin"],pm[0] if pm else None)
        except Exception as e: pass
    groups=collections.defaultdict(list)
    for c,k in info.items(): groups[k].append(c)
    print({k:len(v) for k,v in groups.items()})
    sample=[]
    for k,v in groups.items(): sample+=random.sample(v,min(4,len(v)))
    n=0;agree=0
    for c in sample:
        try: r=cell(c)
        except Exception as e: print(c,"ERR",e); continue
        exact=r["diff"]["output_tokens"]==0
        det=(r["nullsub"]==0 and r["nsubreq"]>0)
        inex=any(r["diff"][k] for k in ("input_tokens","cache_read_input_tokens","cache_creation_input_tokens"))
        n+=1;agree+=(exact==det)
        print(r["bin"],r["pm"],r["mode"],r["think"],r["length"],"outdiff",r["diff"]["output_tokens"],"in/cache diff",inex,"null/sub",r["nullsub"],"/",r["nsubreq"],"exact",exact,"det",det,"AGREE" if exact==det else "DISAGREE",c[:40])
    print("n",n,"agree",agree)
