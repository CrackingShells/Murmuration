#!/usr/bin/env bash
# Probe logger. Disposable; never shipped.
#
# Usage in a hook:  bash logger.sh <label>
# Reads the raw hook input (JSON) on stdin and appends one JSON line to
# $PROBE_OUT (default: probes/out/events.jsonl):
#   {ts, run, label, event, pid, env{...}, input:<raw hook input>}
#
# Behavioural switches (off unless set in the environment of the claude run):
#   PROBE_INJECT=1   SubagentStart/UserPromptSubmit/SessionStart emit additionalContext
#   PROBE_WATCH=<p>  SessionStart emits watchPaths [<p>]
#   PROBE_TITLE=<t>  SessionStart emits sessionTitle
#   PROBE_BLOCK=1    SubagentStop emits decision:block once (stop_hook_active guard)
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROBE_OUT="${PROBE_OUT:-$HERE/out/events.jsonl}"

log_event() {
  local label="$1" input
  input="$(cat)"
  [ -z "$input" ] && input="null"
  mkdir -p "$(dirname "$PROBE_OUT")"
  jq -nc --arg label "$label" --arg run "${PROBE_RUN:-}" --argjson input "$input" \
    --arg entry "${CLAUDE_CODE_ENTRYPOINT:-}" --arg pdir "${CLAUDE_PROJECT_DIR:-}" \
    --arg proot "${CLAUDE_PLUGIN_ROOT:-}" --arg ppid "$PPID" \
    '{ts: (now|todate), run: $run, label: $label, event: ($input.hook_event_name? // null), pid: $ppid,
      env: {entrypoint: $entry, project_dir: $pdir, plugin_root: $proot}, input: $input}' \
    >> "$PROBE_OUT" 2>>"$HERE/out/logger_errors.log" \
  || printf '{"label":"%s","logger_error":true,"raw":%s}\n' "$label" "$(printf '%s' "$input" | jq -Rs .)" >> "$PROBE_OUT"
  printf "%s" "$input"
}

respond() {  # $1=event name, $2=raw input
  local ev="$1" in="$2"
  case "$ev" in
    SessionStart)
      if [ -n "${PROBE_WATCH:-}" ] || [ "${PROBE_INJECT:-}" = 1 ] || [ -n "${PROBE_TITLE:-}" ]; then
        jq -nc --arg w "${PROBE_WATCH:-}" --arg inj "${PROBE_INJECT:-}" --arg t "${PROBE_TITLE:-}" '
          {hookSpecificOutput: ({hookEventName:"SessionStart"}
             + (if $inj=="1" then {additionalContext:"PROBE-CONTEXT-SESSIONSTART: the codeword is MAGNOLIA."} else {} end)
             + (if $w!="" then {watchPaths:($w|split(":"))} else {} end)
             + (if $t!="" then {sessionTitle:$t} else {} end))}'
      fi;;
    SubagentStart)
      [ "${PROBE_INJECT:-}" = 1 ] && jq -nc '{hookSpecificOutput:{hookEventName:"SubagentStart",additionalContext:"PROBE-CONTEXT-SUBAGENTSTART: your partner codeword is HELIOTROPE."}}';;
    UserPromptSubmit)
      [ "${PROBE_INJECT:-}" = 1 ] && jq -nc '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:"PROBE-CONTEXT-UPS: ups-codeword is QUINCE."}}';;
    FileChanged)
      [ "${PROBE_INJECT:-}" = 1 ] && jq -nc '{systemMessage:"PROBE-SYSMSG-FILECHANGED", hookSpecificOutput:{hookEventName:"FileChanged",additionalContext:"PROBE-CTX-FILECHANGED"}}';;
    SubagentStop)
      if [ "${PROBE_BLOCK:-}" = 1 ]; then
        if [ "$(printf '%s' "$in" | jq -r '.stop_hook_active // false')" = "false" ]; then
          jq -nc '{decision:"block", reason:"PROBE-BLOCK: before finishing, append the word PINEAPPLE to your final message."}'
        fi
      fi;;
  esac
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  label="${1:-unlabelled}"
  raw="$(log_event "$label")"
  ev="$(printf '%s' "$raw" | jq -r '.hook_event_name // empty' 2>/dev/null)"
  respond "$ev" "$raw"
  exit 0
fi
