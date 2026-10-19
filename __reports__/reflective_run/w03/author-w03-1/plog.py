#!/usr/bin/env python3
"""Logging-only probe hook. Appends one JSON line per event to $PROBE_LOG. PROBE_MODE: log | ctx | block | ctxuse.
ctx: PostToolBatch answers additionalContext 'PROBE-CTX-<n>' (n counts batches of that agent).
block: PostToolBatch answers decision block, reason 'PROBE-BLOCK-REASON', once per agent.
ctxuse: PostToolUse answers additionalContext 'PROBE-USE-<n>' for comparison."""
import json, os, sys, time
raw = sys.stdin.read()
try:
    ev = json.loads(raw)
except Exception:
    ev = {"unparsed": raw[:200]}
log = os.environ.get("PROBE_LOG")
mode = os.environ.get("PROBE_MODE", "log")
kind = ev.get("hook_event_name")
aid = ev.get("agent_id") or "main"
state = (log or "/tmp/author-w03-1/none") + ".state"
os.makedirs(state, exist_ok=True)
def bump(key):
    p = os.path.join(state, "%s.%s" % (aid, key))
    n = (int(open(p).read()) if os.path.exists(p) else 0) + 1
    open(p, "w").write(str(n)); return n
rec = dict(t=time.time(), kind=kind, agent_id=ev.get("agent_id"), agent_type=ev.get("agent_type"), tool_name=ev.get("tool_name"),
           tool_use_id=ev.get("tool_use_id"), keys=sorted(ev.keys()),
           batch=[{k: (c.get(k) if k != "tool_response" else "..") for k in ("tool_name", "tool_use_id")} for c in ev.get("tool_calls", [])] if isinstance(ev.get("tool_calls"), list) else None,
           mode=mode)
out = None
if kind == "PreToolUse" and mode == "deny" and ev.get("tool_name") == "Bash" and "d1.txt" in json.dumps(ev.get("tool_input")):
    out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "PROBE-DENY: refused by the probe"}}
if kind == "PostToolBatch":
    n = bump("batch"); rec["n"] = n
    if mode == "ctx":
        out = {"hookSpecificOutput": {"hookEventName": "PostToolBatch", "additionalContext": "PROBE-CTX-%d" % n}}
    elif mode == "block" and n == 1:
        out = {"decision": "block", "reason": "PROBE-BLOCK-REASON"}
elif kind == "PostToolUse":
    n = bump("use"); rec["n"] = n
    if mode == "blockuse" and n == 1 and ev.get("agent_id"):
        out = {"decision": "block", "reason": "PROBE-USEBLOCK-REASON: hand back now"}
    if mode == "ctxuse":
        out = {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "PROBE-USE-%d" % n}}
rec["answered"] = bool(out)
if kind in ("SubagentStart", "SubagentStop") and ev.get("agent_id") and ev.get("transcript_path"):
    tp = ev.get("agent_transcript_path") or os.path.join(ev["transcript_path"][:-6], "subagents", "agent-%s.jsonl" % ev["agent_id"])
    try:
        recs = [json.loads(x) for x in open(tp)]
        users = [r for r in recs if r.get("type") == "user"]
        rec["tx"] = dict(exists=True, records=len(recs), users=len(users), last_user=json.dumps(users[-1].get("message"))[:400] if users else None)
    except OSError:
        rec["tx"] = dict(exists=False)
if log:
    with open(log, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
        if kind == "PostToolBatch" and os.environ.get("PROBE_FULL"):
            fh.write(json.dumps(dict(full=ev)) [:20000] + "\n")
if out:
    print(json.dumps(out))
