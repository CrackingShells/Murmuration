#!/usr/bin/env bash
# Like run.sh but keeps the session open on stdin (stream-json input), so a feeder can
# send several user messages and touch files between them.
#   probes/run_stream.sh <run-name> [claude flags ...] -- '<feeder>'
# The feeder is a bash snippet; it may call `msg "<text>"` and `sleep`, `touch`.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$1"; shift
EXTRA=()
while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do EXTRA+=("$1"); shift; done
shift
FEEDER="${1:-}"
export PROBE_RUN="$RUN" PROBE_OUT="$HERE/out/events.jsonl" PROBE_MCP_OUT="$HERE/out/mcp_calls.jsonl"
mkdir -p "$HERE/out/work"
cd "$HERE/out/work" || exit 1
msg() { jq -nc --arg t "$1" '{type:"user",message:{role:"user",content:$t}}'; }
export -f msg 2>/dev/null
{ eval "$FEEDER"; } | claude -p \
  --input-format stream-json --output-format stream-json --verbose --include-hook-events \
  --plugin-dir "$HERE/plugin" --setting-sources project \
  --permission-mode bypassPermissions --disallowedTools Bash WebFetch WebSearch \
  --debug-file "$HERE/out/$RUN.debug.log" \
  "${EXTRA[@]}" > "$HERE/out/$RUN.stream.jsonl" 2> "$HERE/out/$RUN.stderr.log"
echo "exit=$? run=$RUN"
