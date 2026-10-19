import json,glob,sys,os
sys.path.insert(0,'.')
import indep
P=os.path.expanduser("~/.claude/projects/")
for n in ("ins-auto","ins-bypass","des-auto","des-bypass"):
    d="scratch/"+n; sid=None
    for l in open(d+"/stdout.jsonl"):
        try:j=json.loads(l)
        except: continue
        if j.get("type")=="system" and j.get("subtype")=="init": sid=j["session_id"]
        if j.get("type")=="result": r=j
    mu=r["modelUsage"]; truth={k:sum(v[m] for v in mu.values()) for k,m in indep.K}
    main=glob.glob(P+"*"+n+"*/"+sid+".jsonl")[0]
    tot={k:0 for k,_ in indep.K}; null=nreq=0
    for f in [main]+sorted(glob.glob(main[:-6]+"/subagents/*.jsonl")):
        for u,s in indep.reqs(f).values():
            for k,_ in indep.K: tot[k]+=u.get(k,0)
            if f!=main: nreq+=1; null+= s is None
    print(n,"diff",{k:tot[k]-truth[k] for k,_ in indep.K},"subagent null-last",null,"/",nreq,"cost",r["total_cost_usd"])
