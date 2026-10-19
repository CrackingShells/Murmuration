import json,sys,time,os
d=json.load(sys.stdin)
out={"t":time.time(),"prompt":d.get("prompt"),"prompt_id":d.get("prompt_id"),"keys":sorted(d.keys())}
tp=d.get("transcript_path"); recs=[]
try:
    for l in open(tp):
        r=json.loads(l)
        if r.get("type")=="user" and r.get("promptId")==d.get("prompt_id") and not r.get("isMeta"):
            c=r["message"]["content"]
            recs.append({"origin":r.get("origin"),"turnOrigin":r.get("turnOrigin"),"promptSource":r.get("promptSource"),
                         "blocks":[ (b.get("type"), b.get("text")) for b in c] if isinstance(c,list) else [("str",c)]})
except Exception as e: out["err"]=repr(e)
out["transcript_user_records_at_hook_time"]=recs
open(sys.argv[1],"a").write(json.dumps(out)+"\n")
