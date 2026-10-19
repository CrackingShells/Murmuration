#!/usr/bin/env python3
"""List the tool calls of one run's subagent: calls.py <tag>  (reads only)."""
import glob, json, os, sys
S = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1]
e = json.load(open(os.path.join(S, "e_%s.json" % tag)))
f = glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents/agent-*.jsonl" % e["session_id"]))[0]
for l in open(f):
    x = json.loads(l)
    if x.get("type") == "assistant":
        for c in x["message"]["content"]:
            if c["type"] == "tool_use":
                print(c["name"], json.dumps(c["input"])[:int(sys.argv[2]) if len(sys.argv) > 2 else 150])
            elif c["type"] == "text":
                print("TEXT", c["text"][:150].replace("\n", " "))
    if x.get("type") == "user" and isinstance(x["message"]["content"], list):
        for c in x["message"]["content"]:
            if c.get("type") == "tool_result" and c.get("is_error"):
                print("ERROR_RESULT", json.dumps(c["content"])[:300])
