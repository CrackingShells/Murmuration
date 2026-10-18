#!/usr/bin/env bash
# analyze.sh <tag-or-run-substring>: verdict-oriented view of out/events.jsonl and out/mcp_calls.jsonl.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
E="$HERE/out/events.jsonl"; M="$HERE/out/mcp_calls.jsonl"; T="${1:-}"
hdr() { printf '\n== %s\n' "$1"; }
hdr "Subagent events (which matcher spellings fired; agent_type/agent_id; fields)"
jq -c --arg t "$T" 'select((.run|contains($t)) and (.event=="SubagentStart" or .event=="SubagentStop"))
  | [.run,.label,.input.agent_type,.input.agent_id,(.input.agent_transcript_path|tostring|.[-40:]),.input.stop_hook_active,(.input|keys|join(","))]' "$E"
hdr "PostToolUse/PreToolUse for Agent, Task, SendMessage, SubagentHandback (tool_name, response keys)"
jq -c --arg t "$T" 'select((.run|contains($t)) and (.event=="PostToolUse" or .event=="PreToolUse") and (.input.tool_name|test("Agent|Task|SendMessage|SubagentHandback")))
  | [.run,.label,.event,.input.tool_name,(.input.tool_input|tostring|.[0:150]),(.input.tool_response|if type=="object" then keys|join(",") else tostring|.[0:100] end)]' "$E"
hdr "UserPromptSubmit prompts, classified"
jq -r --arg t "$T" 'select((.run|contains($t)) and .event=="UserPromptSubmit")
  | .run+" | "+(.input.prompt|if test("^<cross-session-message") then "CROSS-SESSION" elif test("^<task-notification") then "TASK-NOTIFICATION" elif test("agent-message") then "AGENT-MESSAGE" else "GENUINE?" end)+" | "+(.input.prompt|.[0:200]|gsub("\n";"\\n"))' "$E"
hdr "mcp_tool calls received by the stub server (event, agent_type, tool_name)"
jq -c --arg t "$T" 'select((.run|contains($t)) and .kind=="call")|[.run,.args.event,.args.agent_type,.args.tool_name,(.args.extra|tostring|.[0:60])]' "$M"
hdr "PostCompact / SessionStart(compact) / PreCompact"
jq -c --arg t "$T" 'select((.run|contains($t)) and (.event=="PostCompact" or .event=="PreCompact" or (.event=="SessionStart" and .input.source=="compact")))|[.run,.event,(.input|del(.session_id,.transcript_path,.cwd,.hook_event_name)|tostring|.[0:300])]' "$E"
hdr "Injected context seen by subagents (CONTEXT-SEEN) and PINEAPPLE (block honoured)"
for f in "$HERE"/out/*"$T"*.stream.jsonl; do [ -f "$f" ] && { echo "-- $f"; grep -o 'CONTEXT-SEEN:[^"\\]*' "$f" | sort | uniq -c; grep -c PINEAPPLE "$f"; }; done
hdr "Tools used by the main thread (m3 runs)"
for f in "$HERE"/out/m3_*"$T"*.stream.jsonl; do [ -f "$f" ] && { echo "-- $f"; jq -r 'select(.type=="assistant")|.message.content[]?|select(.type=="tool_use")|.name' "$f" | sort | uniq -c; jq -r 'select(.type=="result")|.result' "$f" | head -20; }; done
