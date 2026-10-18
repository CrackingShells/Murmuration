#!/usr/bin/env bash
# show.sh <run>: compact table of the hook inputs logged for one run (drops the common fields).
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
jq -c --arg r "$1" 'select(.run==$r)
  | [.ts[11:19], .label, (.input | del(.session_id,.transcript_path,.cwd,.hook_event_name,.prompt_id,.permission_mode,.effort,.scratchpad_dir) | tostring | .[0:'"${2:-330}"'])]' "$HERE/out/events.jsonl"
