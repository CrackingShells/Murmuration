# Independent: all project folders of the Murmuration family; dedup rule check + cost-state cells; random sample.
import json, glob, os, collections, random, sys
sys.path.insert(0, ".")
H = os.path.expanduser("~/.claude/projects")
folders = [d for d in glob.glob(H+"/*") if "Murmuration" in d or "murmuration" in d]
PR = {"claude-opus-5-5":(4,20,0.20,5,8),"claude-sonnet-5-5":(2,10,0.10,2.5,4),"claude-fable-5-1":(10,50,0.25,12.5,20),"claude-haiku-5-5":(0.10,0.5,0.01,0.125,0.2)}
owners = collections.defaultdict(set); msgs = {}; cost = {}; sidcwd = collections.defaultdict(set); sidfiles=collections.defaultdict(set)
for d in folders:
  for f in glob.glob(d+"/**/*.jsonl", recursive=True):
    for l in open(f, errors="replace"):
        try: r=json.loads(l)
        except: continue
        if r.get("type")=="cost-state": cost[r["sessionId"]]=r; continue
        if r.get("cwd") and r.get("sessionId"): sidcwd[r["sessionId"]].add(r["cwd"])
        if r.get("type")!="assistant": continue
        m=r.get("message") or {}; u=m.get("usage"); mid=m.get("id")
        if not u or not mid: continue
        sid=r["sessionId"]; owners[mid].add(sid); sidfiles[sid].add(f); side=("/subagents/" in f) or bool(r.get("isSidechain"))
        k=(sid,mid); p=msgs.get(k)
        if p is None or u.get("output_tokens",0)>=p[0].get("output_tokens",0): msgs[k]=(u,m.get("model"),side or (p[2] if p else False))
print("folders",len(folders),"sessions seen",len(sidcwd),"with cost-state",len(cost),"msg ids",len(owners),"multi-owner ids",sum(1 for v in owners.values() if len(v)>1))
cells=collections.defaultdict(collections.Counter)
sidecell=collections.defaultdict(bool)
for (sid,mid),(u,model,sd) in msgs.items():
    sidecell[(sid,model)]|=sd
    c=cells[(sid,model)]; cc=u.get("cache_creation") or {}
    w1=cc.get("ephemeral_1h_input_tokens",0); w5=cc.get("ephemeral_5m_input_tokens",0); tot=u.get("cache_creation_input_tokens",0)
    if w1+w5!=tot: w5+=tot-(w1+w5)
    c["in"]+=u.get("input_tokens",0); c["out"]+=u.get("output_tokens",0); c["cr"]+=u.get("cache_read_input_tokens",0); c["w5"]+=w5; c["w1"]+=w1; c["n"]+=1
rows=[]
for sid,r in cost.items():
    for model,mu in r["modelUsage"].items():
        c=cells.get((sid,model),collections.Counter()); p=PR.get(model)
        mine=(c["in"]*p[0]+c["out"]*p[1]+c["cr"]*p[2]+c["w5"]*p[3]+c["w1"]*p[4])/1e6 if p else None
        rows.append((sid,model,c,mu,mine))

tally=collections.Counter()
for sid,model,c,mu,mine in rows:
    sd=sidecell[(sid,model)]
    eq=(c["in"],c["cr"],c["w5"]+c["w1"],c["out"])==(mu["inputTokens"],mu["cacheReadInputTokens"],mu["cacheCreationInputTokens"],mu["outputTokens"])
    ratio=mine/mu["costUSD"] if mine and mu["costUSD"] else None
    within=ratio is not None and abs(ratio-1)<=5e-4
    key=("subagent" if sd else "no-subagent", "within" if within else "outside")
    tally[key]+=1
    if not sd and not within: print("no-subagent outside:",sid[:8],model,c["n"],ratio,"cs",round(mu["costUSD"],4),(c["in"],c["cr"],c["w5"]+c["w1"],c["out"]),(mu["inputTokens"],mu["cacheReadInputTokens"],mu["cacheCreationInputTokens"],mu["outputTokens"]))
    if not sd: tally["nosub_tokens_equal" if eq else "nosub_tokens_unequal"]+=1
print(tally)
