#!/usr/bin/env python3
"""Stub MCP server for the platform probes: one tool, `record`.

Speaks newline-delimited JSON-RPC on stdio (no dependencies). Every call to
`record` appends {ts, pid, args, meta} to out/mcp_calls.jsonl, so a hook's
`mcp_tool` handler can be seen to arrive, with the substituted arguments.
Disposable probe code; never shipped.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("PROBE_MCP_OUT", os.path.join(HERE, "..", "out", "mcp_calls.jsonl"))


def log(kind, **kw):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rec = {"ts": time.time(), "pid": os.getpid(), "kind": kind, "run": os.environ.get("PROBE_RUN", "")}
    rec.update(kw)
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")


TOOLS = [{
    "name": "record",
    "description": "Probe tool: append the given arguments to the probe log and return 'ok'.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "event": {"type": "string"},
            "session_id": {"type": "string"},
            "agent_id": {"type": "string"},
            "agent_type": {"type": "string"},
            "tool_name": {"type": "string"},
            "prompt": {"type": "string"},
            "extra": {"type": "string"},
        },
        "additionalProperties": True,
    },
}]


def reply(id_, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    log("start", argv=sys.argv, cwd=os.getcwd())
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError:
            continue
        method = req.get("method")
        id_ = req.get("id")
        if method == "initialize":
            p = req.get("params", {})
            log("initialize", clientInfo=p.get("clientInfo"), protocolVersion=p.get("protocolVersion"))
            reply(id_, {
                "protocolVersion": p.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "probe-stub", "version": "0.0.1"},
            })
        elif method == "tools/list":
            reply(id_, {"tools": TOOLS})
        elif method == "tools/call":
            p = req.get("params", {})
            log("call", tool=p.get("name"), args=p.get("arguments"), meta=p.get("_meta"))
            ex = str((p.get("arguments") or {}).get("extra", ""))
            if ex.startswith("sleep:"):  # timing probe: block this long before answering
                time.sleep(float(ex[6:]))
                log("slept", seconds=ex[6:])
            reply(id_, {"content": [{"type": "text", "text": "ok"}], "isError": False})
        elif method == "ping":
            reply(id_, {})
        elif id_ is not None:
            reply(id_, error={"code": -32601, "message": "method not found: %s" % method})
    log("stdin_closed")


if __name__ == "__main__":
    main()
