#!/usr/bin/env python3
"""Measures, in the wave-class murmuration worker transcripts, the characters of each ToolSearch result (the schemas a worker pulled in), grouped by the query; input: ~/.claude/projects/*/*/subagents/agent-*.jsonl; output: TSV on stdout (agent type, query, result chars, whether a tool call to a loaded name followed).
Read-only; no credentials printed."""
import glob, json, os
root = os.path.expanduser("~/.claude/projects"); print("type\tquery\tresult_chars")
for f in glob.glob(os.path.join(root, "*", "*", "subagents", "agent-*.jsonl")):
    p = f.split(os.sep)[-4]
    if not ("claude-worktrees-Murmuration" in p and "---" not in p and "-runs-" not in p and "scratch" not in p): continue
    try: at = json.load(open(f[:-6] + ".meta.json")).get("agentType", "")
    except Exception: continue
    if not at.startswith("murmuration"): continue
    pend = {}
    for l in open(f):
        if "ToolSearch" not in l and "tool_result" not in l: continue
        r = json.loads(l); c = r.get("message", {}).get("content", [])
        if not isinstance(c, list): continue
        for b in c:
            if not isinstance(b, dict): continue
            if b.get("type") == "tool_use" and b["name"] == "ToolSearch": pend[b["id"]] = str(b["input"].get("query", ""))[:60]
            if b.get("type") == "tool_result" and b.get("tool_use_id") in pend:
                print("%s\t%s\t%d" % (at.split(":")[-1], pend.pop(b["tool_use_id"]), len(json.dumps(b.get("content")))))
