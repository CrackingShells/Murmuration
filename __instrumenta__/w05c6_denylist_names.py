#!/usr/bin/env python3
"""Lists, for a Desktop transcript's first prompt_snapshot (tool schemas + deferred names) and an agent file's disallowedTools: line, which entries match nothing, which names each entry removes, and whether the must-keep tools (Agent, SendMessage, AskUserQuestion, ScheduleWakeup, Monitor, ccd_turn*, ccd_session*) remain, loaded or deferred; own code, does not import the author's projection. usage: w05c6_denylist_names.py <transcript.jsonl> <agent.md>; stdout. Stdlib only."""
import fnmatch, json, sys
tr, ag = sys.argv[1:3]
line=[l for l in open(ag) if l.startswith("disallowedTools:")][0]
pats=[p.strip() for p in line.split(":",1)[1].split(",") if p.strip()]
snap=None; deferred=[]
for l in open(tr):
    r=json.loads(l)
    if r.get("type")!="attachment": continue
    a=r["attachment"]
    if a.get("type")=="deferred_tools_delta" and snap is None: deferred+=a.get("addedNames",[])
    if a.get("type")=="prompt_snapshot" and "tools" in a and snap is None: snap=a["tools"]; break
loaded=[t["name"] for t in snap]
print("loaded",len(loaded),"chars",sum(len(json.dumps(t)) for t in snap),"deferred",len(deferred))
for p in pats:
    hl=[n for n in loaded if fnmatch.fnmatchcase(n,p)]; hd=[n for n in deferred if fnmatch.fnmatchcase(n,p)]
    sz=sum(len(json.dumps(t)) for t in snap if t["name"] in hl)
    print(f"{p:42s} loaded:{len(hl):2d} chars:{sz:6d} deferred:{len(hd)}  {(hl+hd)[:4]}")
allnames=loaded+deferred
removed={n for n in allnames if any(fnmatch.fnmatchcase(n,p) for p in pats)}
for key in ["Agent","SendMessage","AskUserQuestion","ScheduleWakeup","Monitor","ccd_turn","ccd_session","ListAgents","SendUserFile"]:
    m=[n for n in allnames if key in n]
    print(f"must-keep {key:16s} present:{len(m):2d} removed:{[n for n in m if n in removed]}")
print("all removed:",len(removed),sorted(removed)[:60])
