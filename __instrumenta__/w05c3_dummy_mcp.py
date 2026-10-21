#!/usr/bin/env python3
"""A minimal stdio MCP server (stdlib only) with one tool `echo(text)` that returns its text; input: JSON-RPC lines on stdin; output: JSON-RPC lines on stdout. Used by wave-5 E6 to test whether an `mcp__<server>__*` or `mcp__*` entry in an agent's `tools:` line keeps MCP tools for a main-thread agent."""
import json, sys
TOOLS = [{"name": "echo", "description": "Return the text it is given.", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}]
for line in sys.stdin:
    try:
        m = json.loads(line)
    except ValueError:
        continue
    i, meth = m.get("id"), m.get("method")
    if meth == "initialize":
        r = {"protocolVersion": m["params"].get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}}, "serverInfo": {"name": "dummy", "version": "0"}}
    elif meth == "tools/list":
        r = {"tools": TOOLS}
    elif meth == "tools/call":
        r = {"content": [{"type": "text", "text": "ECHO:" + str(m["params"].get("arguments", {}).get("text", ""))}]}
    elif i is None:
        continue
    else:
        r = {}
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": i, "result": r}) + "\n"); sys.stdout.flush()
