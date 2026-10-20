# prints, per run, the ordered tool calls (name + command/path, truncated) and result length from stream-json run.jsonl files; input: run folders under a run root; output: text on stdout; flags target-name mentions
import json,sys,os
root=sys.argv[1]; ids=sys.argv[2:]
T=["strings_binary_maximum_distinct_substrings_bruteforce","steps_longest_collatz_stopping_time_below_limit"]
for i in ids:
    print("=====",i)
    res={}
    calls=[]
    for l in open(os.path.join(root,i,"run.jsonl")):
        try:o=json.loads(l)
        except: continue
        m=o.get("message")
        if not isinstance(m,dict) or not isinstance(m.get("content"),list): continue
        for c in m["content"]:
            if c.get("type")=="tool_use": calls.append(c)
            elif c.get("type")=="tool_result":
                x=c.get("content"); 
                if isinstance(x,list): x="".join(y.get("text","") for y in x if isinstance(y,dict))
                res[c.get("tool_use_id")]=x or ""
    for n,c in enumerate(calls):
        inp=c["input"]; s=inp.get("command") or inp.get("file_path") or json.dumps(inp)
        r=res.get(c["id"],"")
        flag=[t[:12] for t in T if t in s]
        rf=[t[:12] for t in T if t in r]
        print(n,c["name"],repr(s[:230]),"| res",len(r),"cmd-has",flag,"res-has",rf)
