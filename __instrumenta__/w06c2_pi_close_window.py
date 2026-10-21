# Computes, from one PI transcript JSONL (read only, argv[1]), the count of non-tool-result user messages by kind (hand-back / task-notification / other) after the first prompt, and the time window of the Bash calls that write puzzle dispositions against the last hand-back; prints text to stdout, no identifiers.
import json, sys, re
from datetime import datetime
def ts(s): return datetime.fromisoformat(s.replace("Z","+00:00"))
kinds={}; handbacks=[]; disp=[]; reqs={}
for line in open(sys.argv[1]):
    try: r=json.loads(line)
    except: continue
    t=r.get("timestamp")
    if not t: continue
    m=r.get("message") or {}
    c=m.get("content")
    if r.get("type")=="user":
        txt=c if isinstance(c,str) else " ".join(x.get("text","") for x in c if isinstance(x,dict) and x.get("type")=="text") if isinstance(c,list) and not any(isinstance(x,dict) and x.get("type")=="tool_result" for x in c) else None
        if txt:
            if "<agent-message" in txt and "hand-" in txt: k="peer message labelled hand-back"; handbacks.append(t)
            elif "<task-notification" in txt: k="task-notification"
            elif "<agent-message" in txt: k="peer message other"
            else: k="other (first prompt, skill text)"
            kinds[k]=kinds.get(k,0)+1
    if r.get("type")=="assistant" and isinstance(c,list):
        for x in c:
            if x.get("type")=="tool_use":
                cmd=(x.get("input") or {}).get("command","") or ""
                if re.search(r"dispo\.py|## Puzzle dispositions",cmd): disp.append((t,len(cmd)))
print("user-message kinds:",kinds)
print("last hand-back at",handbacks[-1] if handbacks else None)
for t,n in disp: print("disposition-writing Bash call at",t,"cmd chars",n)
if disp and handbacks:
    last=ts(handbacks[-1])
    print("disposition calls before the last hand-back:",sum(1 for t,_ in disp if ts(t)<last),"of",len(disp))
