# Independent re-derivation (reproducer-w01-3): dedup by message id owned under record sessionId; compare with cost-state.
import json, glob, os, sys, collections
P = os.path.expanduser(sys.argv[1] if len(sys.argv)>1 else "~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary")
# price per MTok: in, out, cread, w5m, w1h
PR = {"claude-opus-5-5":(4,20,0.20,5,8),"claude-sonnet-5-5":(2,10,0.10,2.5,4),"claude-fable-5-1":(10,50,0.25,12.5,20),"claude-haiku-5-5":(0.10,0.5,0.01,0.125,0.2)}
owners = collections.defaultdict(set)   # msg id -> set of (sessionId)
msgs = {}  # (sid, mid) -> (usage, model, nrecords)
files_per_sid = collections.defaultdict(set)
cost = {}
raw_records = 0
for f in glob.glob(P+"/**/*.jsonl", recursive=True):
    for l in open(f, errors="replace"):
        try: r = json.loads(l)
        except: continue
        if r.get("type")=="cost-state":
            cost[r["sessionId"]] = r; continue   # last wins
        if r.get("type")!="assistant": continue
        m = r.get("message") or {}
        u = m.get("usage"); mid = m.get("id")
        if not u or not mid: continue
        raw_records += 1
        sid = r["sessionId"]
        owners[mid].add(sid)
        k = (sid, mid)
        prev = msgs.get(k)
        # keep record with the largest output_tokens (final value), tie -> later
        if prev is None or u.get("output_tokens",0) >= prev[0].get("output_tokens",0):
            msgs[k] = (u, m.get("model"), (prev[2] if prev else 0)+1)
        else:
            msgs[k] = (prev[0], prev[1], prev[2]+1)
print("raw assistant records w/ usage", raw_records, "distinct (sid,mid)", len(msgs), "mids with >1 owner", sum(1 for v in owners.values() if len(v)>1))
cells = collections.defaultdict(lambda: collections.Counter())
for (sid,mid),(u,model,n) in msgs.items():
    c = cells[(sid,model)]
    cc = u.get("cache_creation") or {}
    w1 = cc.get("ephemeral_1h_input_tokens",0); w5 = cc.get("ephemeral_5m_input_tokens",0)
    tot = u.get("cache_creation_input_tokens",0)
    if w1+w5 != tot: w5 += tot-(w1+w5)   # unsplit remainder as 5m
    c["in"]+=u.get("input_tokens",0); c["out"]+=u.get("output_tokens",0); c["cr"]+=u.get("cache_read_input_tokens",0)
    c["w5"]+=w5; c["w1"]+=w1; c["n"]+=1
tot_cs=tot_me=0
for sid, r in sorted(cost.items()):
    for model, mu in r["modelUsage"].items():
        c = cells.get((sid,model), collections.Counter())
        p = PR.get(model)
        mine = None
        if p: mine = (c["in"]*p[0]+c["out"]*p[1]+c["cr"]*p[2]+c["w5"]*p[3]+c["w1"]*p[4])/1e6
        ok = lambda a,b: "=" if a==b else f"{a}/{b}"
        print(sid[:8], model, "n",c["n"], "in",ok(c["in"],mu["inputTokens"]),"cr",ok(c["cr"],mu["cacheReadInputTokens"]),"cw",ok(c["w5"]+c["w1"],mu["cacheCreationInputTokens"]),"out",ok(c["out"],mu["outputTokens"]),
              "cs$%.4f"%mu["costUSD"], "mine$%s"%("%.4f"%mine if mine is not None else None), "ratio %.4f"%(mine/mu["costUSD"]) if mine and mu["costUSD"] else "")
