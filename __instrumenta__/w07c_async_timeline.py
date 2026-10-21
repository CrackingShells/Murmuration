"""Prints the timeline of the w07-c `async` run: each Bash tool call's tool_use and tool_result time (transcript), the async hooks that acted (hooks.log start/end, ms after the first tool_use), and the transcript records of async results (async_hook_response, hook_blocking_error, hook_additional_context); input: the run directory; output: text lines on stdout, time in ms since the first tool_use.
"""
import json, sys, os
from datetime import datetime
d = sys.argv[1]
T = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000
ev = []
for l in open(os.path.join(d, "transcript.jsonl")):
    r = json.loads(l); ts = r.get("timestamp")
    if not ts: continue
    t = T(ts)
    if r["type"] == "assistant":
        for c in r["message"]["content"]:
            if c["type"] == "tool_use": ev.append((t, "tool_use  " + c["input"].get("command", "")))
    elif r["type"] == "user" and isinstance(r["message"]["content"], list):
        for c in r["message"]["content"]:
            if c.get("type") == "tool_result": ev.append((t, "tool_result " + str(c["content"])[:40]))
    elif r["type"] == "attachment":
        a = r["attachment"]
        if a.get("type") in ("async_hook_response", "hook_blocking_error", "hook_additional_context", "hook_non_blocking_error"):
            ev.append((t, "RECORD %s %s %s" % (a["type"], a.get("hookName", ""), (str(a.get("stdout") or a.get("content") or a.get("stderr") or a.get("blockingError") or "")[:90]).replace("\n", " "))))
for l in open(os.path.join(d, "hooks.log")):
    r = json.loads(l)
    if r["acted"]: ev.append((r["t0_ns"] / 1e6, "  hook START %s (%s)" % (r["label"], r["cmd"]))); ev.append((r["t1_ns"] / 1e6, "  hook END   %s (%s)" % (r["label"], r["cmd"])))
ev.sort(); t0 = min(t for t, s in ev if s.startswith("tool_use"))
for t, s in ev:
    if t >= t0 - 1: print("%8.0f  %s" % (t - t0, s))
