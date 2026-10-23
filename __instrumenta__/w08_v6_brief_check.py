# w08_v6_brief_check.py: for each subagent transcript of one PI session, prints name, first-record timestamp, model, brief length, any sentence of the brief mentioning "character", and first-handback chars; inputs: session dir; output: text on stdout (no raw transcript beyond the "character" sentences).
import json, sys, glob, os, re
sess = sys.argv[1]
for f in sorted(glob.glob(os.path.join(sess, "subagents", "agent-*.jsonl"))):
    brief=None; ts=None; models=set(); hb=[]
    for line in open(f, errors="replace"):
        try: r=json.loads(line)
        except ValueError: continue
        m=r.get("message") or {}; c=m.get("content")
        if brief is None and r.get("type")=="user":
            brief=c if isinstance(c,str) else " ".join(b.get("text","") for b in c or [] if isinstance(b,dict)); ts=r.get("timestamp")
        if r.get("type")=="assistant":
            if m.get("model"): models.add(m["model"])
            if isinstance(c,list):
                for b in c:
                    if isinstance(b,dict) and b.get("type")=="tool_use" and b.get("name")=="SubagentHandback":
                        hb.append((r.get("timestamp"),len(str(b["input"].get("message","")))))
    g=re.search(r"Your name is ([a-z0-9-]+)",brief or ""); n=g.group(1) if g else "?"
    sents=[s.strip()[:160] for s in re.split(r"(?<=[.])\s", brief or "") if re.search(r"character|hand-?back|short|length", s, re.I)]
    print("##",n,ts,sorted(models),"brieflen",len(brief or ""),"handbacks",hb)
    for s in sents[:4]: print("   >",s.replace("\n"," "))
