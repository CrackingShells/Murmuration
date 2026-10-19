# Independent: classify every ended-session cell by "has any message with no record carrying stop_reason" (unfinished), main or subagent.
import json, glob, os, collections
H=os.path.expanduser("~/.claude/projects")
folders=[d for d in glob.glob(H+"/*") if "Murmuration" in d or "murmuration" in d or d.endswith("combinatorics-on-binary")]
PR={"claude-opus-5-5":(4,20,0.20,5,8),"claude-sonnet-5-5":(2,10,0.10,2.5,4),"claude-fable-5-1":(10,50,0.25,12.5,20),"claude-haiku-5-5":(0.10,0.5,0.01,0.125,0.2)}
msgs={}; fin=collections.defaultdict(bool); where={}; cost={}
for d in folders:
  for f in glob.glob(d+"/**/*.jsonl",recursive=True):
    sub="/subagents/" in f
    for l in open(f,errors="replace"):
        try:r=json.loads(l)
        except: continue
        if r.get("type")=="cost-state": cost[r["sessionId"]]=r; continue
        if r.get("type")!="assistant": continue
        m=r.get("message") or {}; u=m.get("usage"); mid=m.get("id")
        if not u or not mid: continue
        k=(r["sessionId"],mid)
        if m.get("stop_reason"): fin[k]=True
        where[k]=where.get(k,False) or sub
        p=msgs.get(k)
        if p is None or u.get("output_tokens",0)>=p[0].get("output_tokens",0): msgs[k]=(u,m.get("model"))
cells=collections.defaultdict(collections.Counter)
for k,(u,model) in msgs.items():
    c=cells[(k[0],model)]; cc=u.get("cache_creation") or {}
    w1=cc.get("ephemeral_1h_input_tokens",0); w5=cc.get("ephemeral_5m_input_tokens",0); t=u.get("cache_creation_input_tokens",0)
    if w1+w5!=t: w5+=t-w1-w5
    for a,b in (("in","input_tokens"),("out","output_tokens"),("cr","cache_read_input_tokens")): c[a]+=u.get(b,0)
    c["w5"]+=w5; c["w1"]+=w1; c["n"]+=1
    if not fin[k]: c["unfinished"]+=1
    if not fin[k] and where[k]: c["unfinished_sub"]+=1
res=collections.Counter()
for sid,r in cost.items():
    for model,mu in r["modelUsage"].items():
        c=cells.get((sid,model),collections.Counter()); p=PR[model]
        mine=(c["in"]*p[0]+c["out"]*p[1]+c["cr"]*p[2]+c["w5"]*p[3]+c["w1"]*p[4])/1e6
        ratio=mine/mu["costUSD"] if mu["costUSD"] else 0
        grp="complete" if c["unfinished"]==0 else "has-unfinished"
        ok=abs(ratio-1)<=5e-4
        res[(grp,ok)]+=1
        if grp=="complete" and not ok: print("complete but off:",sid[:8],model,round(ratio,4),c["n"],"cs in/out",mu["inputTokens"],mu["outputTokens"],"mine",c["in"],c["out"])
print(dict(res))
n=0; tot=0
for (sid,model),c in cells.items():
    if c["unfinished"]>c["unfinished_sub"]:
        n+=1; tot+=c["unfinished"]-c["unfinished_sub"]
        if n<=8: print("main-thread unfinished:",sid[:8],model,c["unfinished"]-c["unfinished_sub"],"of",c["n"], "ended" if sid in cost else "OPEN")
print("cells with main-thread unfinished msgs:",n,"msgs",tot)
