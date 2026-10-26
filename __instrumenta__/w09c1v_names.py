"""Re-derives, from the lab's `__statera__/harness.jsonl` start records (wave-9 live file left out) and the subagent .meta.json names in ~/.claude/projects, the name-binding check of w08-c12 per dispatch (first non-resumed start of an agent id): meta name vs harness name, batched (same-type start within 5 s), before/after 2026-10-24T03:18:27+09:00, to stdout; independent of w09f/w09c1 scripts."""
import json,glob,os,collections,datetime
root=os.path.expanduser("~/.claude/projects")
meta={}
for m in glob.glob(root+"/*/*/subagents/agent-*.meta.json"):
    try: meta[os.path.basename(m)[6:-10]]=json.load(open(m)).get("name") or ""
    except Exception: pass
T=datetime.datetime.fromisoformat
recs=[]
for f in sorted(glob.glob("/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/*/__statera__/harness.jsonl")):
    if "wave-9" in f: continue
    recs+=[json.loads(l)|{"_f":f.split("/")[-3]} for l in open(f)]
starts=[r for r in recs if r["event"]=="start"]
print("start records",len(starts),"resumed",sum(r["resumed"] for r in starts))
first={}
for r in sorted(starts,key=lambda r:T(r["t"])):
    if not r["resumed"]: first.setdefault(r["agent_id"],r)
print("dispatches",len(first),"with meta name",sum(1 for a in first if meta.get(a)),"no meta file",sum(1 for a in first if a not in meta))
M=T("2026-10-24T03:18:27+09:00")
allst=sorted(starts,key=lambda r:T(r["t"]))
rows=[]
for a,r in first.items():
    t=T(r["t"]); mn=meta.get(a,"")
    batched=any(o["type"]==r["type"] and o["agent_id"]!=a and abs((T(o["t"])-t).total_seconds())<=5 for o in allst)
    rows.append((t<M,batched,bool(mn) and r["name"]!=mn,bool(mn),r["name"],mn,r.get("source"),r["type"].split(":")[-1]))
for pre in (True,False):
    s=[x for x in rows if x[0]==pre]
    print("pre" if pre else "post","n",len(s),"with meta",sum(x[3] for x in s),"wrong",sum(x[2] for x in s),"batched",sum(x[1] for x in s),"wrong&batched",sum(x[1] and x[2] for x in s),"wrong&unbatched",sum((not x[1]) and x[2] for x in s))
print([x[4:7] for x in rows if x[2]])
