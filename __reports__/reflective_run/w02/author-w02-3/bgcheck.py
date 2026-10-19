#!/usr/bin/env python3
"""Background-dispatch check (w02-c6 addendum): per cell, did the parent dispatch with run_in_background, what shape did the platform record
for the worker, which hook texts are in the worker's transcript, what the log says, and did the worker hand back.
usage: bgcheck.py <scratch> <cell>...   Read-only; stdlib only; prints counts and a few fields, no raw text."""
import glob, json, os, sys
S = os.path.abspath(sys.argv[1])
for cell in sys.argv[2:]:
    base = os.path.join(S, "runs", cell)
    meta = json.load(open(os.path.join(base, "meta.json")))
    sid = next(json.loads(l)["session_id"] for l in open(os.path.join(base, "stdout.jsonl")) if '"session_id"' in l)
    parent = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sid))[0]
    flags = [(b["input"].get("run_in_background"), b["input"].get("subagent_type")) for l in open(parent) for r in [json.loads(l)]
             if r.get("type") == "assistant" for b in r["message"]["content"] if b.get("type") == "tool_use" and b["name"] == "Agent"]
    sub = glob.glob(os.path.dirname(parent) + "/%s/subagents/agent-*.jsonl" % sid)[0]
    shape = json.load(open(sub.replace(".jsonl", ".meta.json"))).get("requestShape")
    recs = [json.loads(l) for l in open(sub)]
    att = [r["attachment"] for r in recs if r.get("type") == "attachment"]
    note = sum(a.get("type") == "hook_additional_context" and "Lab harness note" in json.dumps(a) for a in att)
    block = sum(a.get("type") == "hook_blocking_error" and "Call SubagentHandback now" in json.dumps(a) for a in att)
    start = sum(a.get("type") == "hook_additional_context" and "Budget: your budget" in json.dumps(a) for a in att)
    tools = [b["name"] for r in recs if r.get("type") == "assistant" for b in r["message"]["content"] if b.get("type") == "tool_use"]
    log = [json.loads(l) for l in open(os.path.join(base, "lab", "__statera__", "harness.jsonl"))]
    hb = glob.glob(os.path.join(base, "lab", "__statera__", "handbacks", "*.md"))
    print(cell, "| Agent calls (run_in_background, type):", flags, "| worker requestShape:", shape, "| transcript: start note %d, 80%% note %d, hand-back notice %d" % (start, note, block),
          "| log:", [(x["event"], x.get("which"), x.get("t_frac")) for x in log if x["event"] != "start"], "| SubagentHandback calls:", tools.count("SubagentHandback"),
          "| hand-back file:", bool(hb), "| USD", round(meta["usd"], 4))
