import json, sys, glob, datetime, os
H="/Users/hacker/.claude/projects/"
DIRS=[H+"-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/subagents",
      H+"-Users-hacker-Documents-explore-combinatorics-on-binary/566fa912-7009-421a-9d79-11145e2b8db9/subagents",
      H+"-Users-hacker-Documents-explore-combinatorics-on-binary/82e8a947-1a0c-441c-bc39-df8e2e5fa743/subagents"]
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
def analyse(path):
    recs=[]
    for l in open(path):
        try: d=json.loads(l)
        except: continue
        if d.get("timestamp") and d.get("type") in("user","assistant"): recs.append((ts(d["timestamp"]),d))
    recs.sort(key=lambda x:x[0])
    out=[]; prev=None; first_user=True; seen=set(); pending=None
    for t,d in recs:
        c=d["message"].get("content")
        if d["type"]=="user":
            is_res = isinstance(c,list) and any(isinstance(b,dict) and b.get("type")=="tool_result" for b in c)
            if not is_res:
                if first_user: first_user=False
                elif prev is not None: pending=(t, t-prev)
            prev=t
        else:
            mid=d["message"].get("id")
            u=d["message"].get("usage") or {}
            if pending and mid not in seen:
                cw=u.get("cache_creation_input_tokens",0); cr=u.get("cache_read_input_tokens",0); inp=u.get("input_tokens",0)
                ctx=cw+cr+inp
                out.append((pending[1],ctx,cw,cr,cw/ctx if ctx else None, pending[0])); pending=None
            seen.add(mid); prev=t
    return out
rows=[]
for D in DIRS:
    for p in glob.glob(D+"/agent-*.jsonl"):
        for r in analyse(p): rows.append((os.path.basename(p)[6:15],)+r)

seen=set(); R=[]
for r in rows:
    k=(r[0],r[2],r[3],r[4])
    if r[1]<1 or k in seen: continue
    seen.add(k); R.append(r)
R.sort(key=lambda r:r[1])
for r in R: print("%s gap %7.1f ctx %7d cw %7d cr %7d share %.3f  wake %s  %s"%(r[0],r[1],r[2],r[3],r[4],r[5],datetime.datetime.fromtimestamp(r[6],datetime.timezone.utc).strftime("%m-%dT%H:%M:%S"), "COLD" if r[5]>=0.8 else "warm"))
print(len(R))
