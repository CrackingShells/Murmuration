#!/bin/sh
# Reproduces every table in this directory from the transcripts (read-only on them).  About 20 s.
# usage: sh run_all.sh      (cwd-independent)
D=$(cd "$(dirname "$0")" && pwd)
python3 -I "$D/extract_calls.py" "$D"      # tool_calls.csv, agents.csv   (all tool_use + joined tool_result, 5 sessions + subagents)
python3 -I "$D/analyze.py" "$D"            # dedup by tool_use_id; outcome classes; t1..t5, calls_dedup_classified.csv
python3 -I "$D/extra.py" "$D"              # t6 bash kinds, t7 ToolSearch context growth, t8 prefix toolNames, t9 shell-search attempts
python3 -I "$D/per_agent_mcp.py" "$D"      # t10 per-agent tool families
python3 -I "$D/agent_context.py" "$D"      # agent_context.csv: deferred names, first-turn input tokens
python3 -I "$D/inventory.py" "$D"          # t11 MCP servers connected / failed per session
