# m1 field list: payload fields that `scripts/budget.py` and `scripts/handback.py` read, per event

Written by author-w06-3 for claim w06-c3, before any run, from the code at the commit that adds this file's
parent (`git log -1` of `scripts/budget.py` and `scripts/handback.py` is 9e4c055 or earlier; the files are not
changed by this wave). Method: read of `handle`, `handle_locked`, `dispatch`, `transcript_of`, `role_of`,
`lab_root`, `agent_name`, `message`, `gate`, `main` in the two files. Environment reads (not payload fields):
`CLAUDE_PROJECT_DIR` (lab_root's last fallback) and the process cwd (lab_root when `cwd` is absent). A server is a
resident process, so its own cwd and environment are not the hook's; `cwd` must reach it as a field.

Fields in the list (top-level unless a dotted path): `cwd`, `hook_event_name`, `tool_name`, `tool_use_id`,
`agent_id`, `agent_type`, `permission_mode`, `transcript_path`, `agent_transcript_path`, `tool_calls[].tool_name`,
`tool_input.subagent_type`, `tool_input.prompt`, `tool_input.name`, `tool_input.message`, `last_assistant_message`.

"Absence matters" marks a field whose being empty or absent changes the script's branch.

| # | Event, matcher | Script | Fields read | Absence matters |
|:--|:--|:--|:--|:--|
| E1 | SubagentStart | budget | `hook_event_name`, `cwd`, `agent_id`, `agent_type`, `transcript_path` (transcript derived), `agent_transcript_path` (if present; else derived from `transcript_path` + `agent_id`), `permission_mode` (logged) | `agent_id` empty = main thread = no-op; `agent_type` not `murmuration:*` = no-op |
| E2 | PreToolUse, `Agent\|Task` | budget (dispatch) | `hook_event_name`, `tool_name`, `cwd`, `agent_id` (must be absent: main thread only), `tool_input.subagent_type`, `tool_input.prompt`, `tool_input.name`, `tool_use_id` | `agent_id` |
| E3 | PostToolUse, no matcher | budget | `hook_event_name`, `tool_name`, `cwd`, `agent_id`, `agent_type`, `transcript_path`, `agent_transcript_path` (if present), `permission_mode` (logged) | `agent_id` |
| E4 | PostToolBatch | budget | `hook_event_name`, `cwd`, `agent_id`, `agent_type`, `transcript_path`, `agent_transcript_path` (if present), `permission_mode`, `tool_calls[].tool_name` (only to see whether `SubagentHandback` is in the batch) | `agent_id`; the array |
| E5 | SubagentStop (handback first, then budget) | handback + budget | `hook_event_name`, `cwd`, `agent_id`, `agent_type`, `transcript_path`, `agent_transcript_path`, `permission_mode` (`auto` makes a text a draft), `last_assistant_message` (text; absent = `missing` section) | `last_assistant_message` empty vs absent (both = no text); `permission_mode` |
| E6 | PreToolUse, `SubagentHandback` | handback (gate) | `hook_event_name`, `tool_name`, `cwd`, `agent_id`, `agent_type` (must equal `murmuration:explorer`), `transcript_path`, `agent_transcript_path` (name lookup) | `agent_id`; `agent_type` |
| E7 | PostToolUse, `SubagentHandback` | handback + budget (E3) | E3's fields, plus `tool_input.message` (the delivered text), `permission_mode`, `agent_transcript_path` / `transcript_path` for the name | `tool_input.message` empty = no section |

Derivations the server may use, as the scripts do: transcript of a subagent = `transcript_path[:-6] + "/subagents/agent-<agent_id>.jsonl"`
(`budget.transcript_of`); agent name from `<that stem>.meta.json`, else the brief's "Your name is".

Pass rule for m1 (from the protocol): every field above reaches the server on the events that need it, by
substitution or a stated derivation. The check is made on the server's own record of each call against the
platform's hook-input record of the same event (`--debug-file` and the transcript), field by field.
