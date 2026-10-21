import json, sys
for line in sys.stdin:
    try: m = json.loads(line)
    except ValueError: continue
    i, meth = m.get("id"), m.get("method")
    if meth == "initialize": r = {"protocolVersion": m["params"].get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}}, "serverInfo": {"name": "noop", "version": "0"}}
    elif meth == "tools/list": r = {"tools": [{"name": "nop", "description": "nothing", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}}}]}
    elif meth == "tools/call": r = {"content": [{"type": "text", "text": ""}]}
    elif i is None: continue
    else: r = {}
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": i, "result": r}) + "\n"); sys.stdout.flush()
