#!/usr/bin/env python3
"""Reads stream-json stdout of E6b cells (<scratch>/runs/<cell>/stdout.jsonl) and prints, per cell: init tool list, tool_use names in order with their results (Agent result text in full up to 300 chars), is_error flags, dummy MCP tool presence, disallowedTools-named tools present; independent of the author's table script. usage: w05c6_stream_check.py <scratch> <cell>... ; stdlib only."""
import json, sys, os
for cell in sys.argv[2:]:
    recs=[]
    for l in open(os.path.join(sys.argv[1],"runs",cell,"stdout.jsonl")):
        try: recs.append(json.loads(l))
        except ValueError: pass
    init=[r for r in recs if r.get("type")=="system" and r.get("subtype")=="init"]
    tools=init[0]["tools"]
    print("==",cell,"init tools",len(tools)); print(" ",sorted(tools))
    uses={}
    for r in recs:
        if r.get("isSidechain") or r.get("parent_tool_use_id"): side=True
        else: side=False
        m=r.get("message") or {}
        c=m.get("content")
        if not isinstance(c,list): continue
        for b in c:
            if b.get("type")=="tool_use" and not side: uses[b["id"]]=b["name"]; 
            if b.get("type")=="tool_result" and b.get("tool_use_id") in uses:
                t=b.get("content"); t=json.dumps(t) if not isinstance(t,str) else t
                print("  ",uses[b["tool_use_id"]],"is_error=",b.get("is_error"),t[:300].replace("\n"," "))
    res=[r for r in recs if r.get("type")=="result"][0]
    print("  result:",res.get("subtype"),res.get("is_error"),res.get("total_cost_usd"),repr(res.get("result"))[:100])
