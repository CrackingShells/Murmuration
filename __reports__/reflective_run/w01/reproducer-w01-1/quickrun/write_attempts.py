#!/usr/bin/env python3
"""List every Write/Edit/NotebookEdit tool_use in the subagent transcripts of this run, with its result.
Usage: write_attempts.py <subagents-dir>   Output: TSV on stdout. Read-only.
Why python: JSONL joins of tool_use to tool_result by id."""
import json, sys, glob, os
d = sys.argv[1]
print("agent\ttype\ttool\tfile_path\tis_error\tresult_head")
files = [d] if d.endswith(".jsonl") else sorted(glob.glob(os.path.join(d, "agent-*.jsonl")))   # a subagents dir, or one transcript (the main thread)
for f in files:
    aid = os.path.basename(f)[6:-6] if os.path.basename(f).startswith("agent-") else "main"
    meta = {}
    try: meta = json.load(open(f[:-6] + ".meta.json")) if aid != "main" else {"agentType": "main-thread"}
    except Exception: pass
    uses, res = {}, {}
    for line in open(f, encoding="utf-8"):
        r = json.loads(line)
        m = r.get("message")
        if not isinstance(m, dict) or not isinstance(m.get("content"), list): continue
        for b in m["content"]:
            if b.get("type") == "tool_use" and b.get("name") in ("Write", "Edit", "NotebookEdit"):
                uses[b["id"]] = b
            elif b.get("type") == "tool_result":
                c = b.get("content")
                if isinstance(c, list): c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                res[b["tool_use_id"]] = (b.get("is_error"), c or "")
    for i, b in uses.items():
        e, c = res.get(i, (None, "NO RESULT"))
        print("\t".join([aid, str(meta.get("agentType") or meta.get("name") or ""), b["name"], b["input"].get("file_path", ""), str(e), c.replace("\n", " ")[:110]]))
