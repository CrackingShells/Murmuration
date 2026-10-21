# w06-c3 stage-1 test server: a stdio MCP server (Python standard library only) with one tool `hook`; records each call's arguments to $WT_OUT/server.jsonl and answers as the event requires (inject / deny / block / nothing), from the `mcp_tool` hooks of a throwaway plugin; inputs: JSON-RPC on stdin, env WT_OUT, file $WT_OUT/mode (live|quiet); outputs: JSON-RPC on stdout, $WT_OUT/server.jsonl, $WT_OUT/server.pid, $WT_OUT/server.starts
import json, os, sys, time, secrets

OUT = os.environ.get("WT_OUT") or os.getcwd()
os.makedirs(OUT, exist_ok=True)
# outage simulation for m4 (a test device, stated in the claim): a file $WT_OUT/refuse makes a (re)started server exit at once ("exit") or never answer ("hang")
try:
    _r = open(os.path.join(OUT, "refuse")).read().strip()
except OSError:
    _r = ""
if _r == "exit":
    sys.exit(1)
if _r == "hang":
    time.sleep(600)
open(os.path.join(OUT, "server.pid"), "w").write(str(os.getpid()))
with open(os.path.join(OUT, "server.starts"), "a") as fh:
    fh.write(json.dumps({"pid": os.getpid(), "t": time.time()}) + "\n")
LOG = open(os.path.join(OUT, "server.jsonl"), "a", buffering=1)
TOOL = {"name": "hook", "description": "Record a hook event.",
        "inputSchema": {"type": "object", "additionalProperties": True}}


def mode():
    try:
        return open(os.path.join(OUT, "mode")).read().strip()
    except OSError:
        return "quiet"


def answer(args):
    """The hook answer for these arguments, as text ('' for nothing), and a tag for the log."""
    if mode() != "live":
        return "", "quiet"
    ev = args.get("event", "")
    nonce = secrets.token_hex(4)
    if ev == "SubagentStart":
        return json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart",
                                                  "additionalContext": "WT-CANARY-%s: this line was injected by the resident hook server." % nonce}}), "inject:" + nonce
    if ev == "PreToolUse:Agent" and "DENYME" in args.get("tool_input_prompt", ""):
        return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                  "permissionDecisionReason": "WT-DENY-%s: the resident hook server refused this Agent call." % nonce}}), "deny:" + nonce
    if ev == "PostToolUse" and "BLOCKME" in args.get("tool_input_command", ""):
        return json.dumps({"decision": "block", "reason": "WT-BLOCK-%s: the resident hook server blocks this result; hand back now." % nonce}), "block:" + nonce
    return "", "none"


def send(i, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": i, "result": result}) + "\n")
    sys.stdout.flush()


for line in sys.stdin:
    try:
        m = json.loads(line)
    except ValueError:
        continue
    i, meth = m.get("id"), m.get("method")
    if i is None:
        continue
    if meth == "initialize":
        send(i, {"protocolVersion": m["params"].get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}}, "serverInfo": {"name": "wt-res", "version": "0"}})
    elif meth == "tools/list":
        send(i, {"tools": [TOOL]})
    elif meth == "tools/call":
        t0 = time.perf_counter()
        args = (m.get("params") or {}).get("arguments") or {}
        text, tag = answer(args)
        send(i, {"content": [{"type": "text", "text": text}]})
        LOG.write(json.dumps({"t": time.time(), "pid": os.getpid(), "us": round((time.perf_counter() - t0) * 1e6), "tag": tag, "args": args}) + "\n")
    else:
        send(i, {})
