"""Command hook for the w07-c probes: logs its own start and end (ns clock) with the hook event, tool, tool_use_id and command, and behaves as told; inputs: JSON on stdin, argv LABEL [--sleep S] [--emit ctx|deny|none] [--exit N] [--only SUBSTR] [--stderr TEXT] [--dump PATH]; output: appends one JSON line to $W7C_LOG (label, event, tool, tool_use_id, t0_ns, t1_ns, acted) and prints the chosen reply on stdout.
`--only SUBSTR`: act (sleep, emit, exit) only when the tool command contains SUBSTR; otherwise log and exit 0 at once. `--emit ctx` prints additionalContext 'CMDCTX-NONCE-<label>-<event>-<last 6 of id>'; `--emit deny` on PreToolUse prints a deny with reason 'CMDDENY-NONCE-<label>'.
"""
import json, os, sys, time
t0 = time.time_ns()
argv = sys.argv[1:]; label = argv[0]
opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d
raw = sys.stdin.read()
try: p = json.loads(raw)
except Exception: p = {}
ev = p.get("hook_event_name", ""); tool = p.get("tool_name", ""); cmd = (p.get("tool_input") or {}).get("command", "") if isinstance(p.get("tool_input"), dict) else ""
only = opt("--only"); acted = only is None or only in cmd
if opt("--dump"):
    with open(opt("--dump"), "a") as f: f.write(json.dumps({"ts_ns": t0, "body": p}) + "\n")
ident = (p.get("tool_use_id") or p.get("agent_id") or "xxxxxx")[-6:]
if acted:
    if opt("--sleep"): time.sleep(float(opt("--sleep")))
    emit = opt("--emit", "none")
    if emit == "ctx": print(json.dumps({"hookSpecificOutput": {"hookEventName": ev, "additionalContext": "CMDCTX-NONCE-%s-%s-%s" % (label, ev, ident)}}))
    elif emit == "deny" and ev == "PreToolUse": print(json.dumps({"hookSpecificOutput": {"hookEventName": ev, "permissionDecision": "deny", "permissionDecisionReason": "CMDDENY-NONCE-" + label}}))
    elif emit == "block": print(json.dumps({"decision": "block", "reason": "CMDBLOCK-NONCE-" + label}))
    if opt("--stderr"): sys.stderr.write(opt("--stderr") + "\n")
t1 = time.time_ns()
with open(os.environ.get("W7C_LOG", "/dev/null"), "a") as f:
    f.write(json.dumps({"label": label, "event": ev, "tool": tool, "tool_use_id": p.get("tool_use_id"), "agent_id": p.get("agent_id"), "cmd": cmd[:60], "t0_ns": t0, "t1_ns": t1, "acted": acted, "pid": os.getpid()}) + "\n")
if acted and opt("--exit"): sys.exit(int(opt("--exit")))
