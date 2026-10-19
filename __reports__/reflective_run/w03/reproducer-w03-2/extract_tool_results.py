"""Prints tool_use and tool_result lines (first 300 chars) from a `claude -p --output-format stream-json` file; no account fields.
usage: python3 -I extract_tool_results.py <run.jsonl>"""
import json, sys
for l in open(sys.argv[1]):
    r = json.loads(l)
    c = (r.get("message") or {}).get("content")
    if isinstance(c, list):
        for b in c:
            if b.get("type") == "tool_use":
                print("USE", b["name"].replace("mcp__plugin_colgrep-mcp_colgrep__", "cg:"), json.dumps(b["input"]))
            if b.get("type") == "tool_result":
                print("  RES", str(b.get("content"))[:300].replace("\n", " | "))
    if r.get("type") == "result":
        print("total_cost_usd", r.get("total_cost_usd"))
