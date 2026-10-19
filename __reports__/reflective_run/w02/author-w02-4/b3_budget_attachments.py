#!/usr/bin/env python3 -I
"""w02-c10: the `budget_usd` attachments one worker saw, against its hand-back figure.
usage: python3 -I b3_budget_attachments.py <B3 arm folder> <agent id, e.g. a2b354341eefe6892>   (reads only)"""
import glob, json, os, sys
arm, aid = sys.argv[1], sys.argv[2]
sid = [json.loads(l) for l in open(os.path.join(arm, "stdout.jsonl")) if '"type":"result"' in l.replace(" ", "")][-1]["session_id"]
g = glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents/agent-%s.jsonl" % (sid, aid)))[0]
for l in open(g):
    x = json.loads(l); a = x.get("attachment")
    if a and a.get("type") == "budget_usd":
        print(x["timestamp"], "used %.4f total %s remaining %.4f" % (a["used"], a["total"], a["remaining"]))
