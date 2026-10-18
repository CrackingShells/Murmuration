#!/usr/bin/env bash
# Run one headless probe session with the probe plugin loaded for this session only.
#   probes/run.sh <run-name> [extra claude flags ...] -- "<prompt>"
# Logs: out/events.jsonl (hook inputs), out/mcp_calls.jsonl (stub MCP), out/<run>.debug.log,
#       out/<run>.stream.jsonl (stream-json incl. hook events). cwd = out/work (gitignored).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$1"; shift
EXTRA=()
while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do EXTRA+=("$1"); shift; done
shift  # --
PROMPT="${1:-}"
export PROBE_RUN="$RUN" PROBE_OUT="$HERE/out/events.jsonl" PROBE_MCP_OUT="$HERE/out/mcp_calls.jsonl"
mkdir -p "$HERE/out/work"
cd "$HERE/out/work" || exit 1
claude -p "$PROMPT" \
  --plugin-dir "$HERE/plugin" \
  --setting-sources project \
  --permission-mode bypassPermissions \
  --disallowedTools Bash WebFetch WebSearch \
  --output-format stream-json --verbose --include-hook-events \
  --debug-file "$HERE/out/$RUN.debug.log" \
  "${EXTRA[@]}" \
  > "$HERE/out/$RUN.stream.jsonl" 2> "$HERE/out/$RUN.stderr.log"
echo "exit=$? run=$RUN"
