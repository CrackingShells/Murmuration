## Keys of each hook event

| run | event | keys |
|:--|:--|:--|
| r2 | PreToolUse | cwd, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_use_id, transcript_path |
| r2 | PostToolUse | cwd, duration_ms, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_response, tool_use_id, transcript_path |
| r2 | SubagentStart | agent_id, agent_type, cwd, hook_event_name, prompt_id, scratchpad_dir, session_id, transcript_path |
| r2 | SubagentStop | agent_id, agent_transcript_path, agent_type, background_tasks, cwd, effort, hook_event_name, last_assistant_message, permission_mode, prompt_id, scratchpad_dir, session_crons, session_id, stop_hook_active, transcript_path |
| r3 | PreToolUse | cwd, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_use_id, transcript_path |
| r3 | PostToolUse | cwd, duration_ms, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_response, tool_use_id, transcript_path |
| r3 | SubagentStart | agent_id, agent_type, cwd, hook_event_name, prompt_id, scratchpad_dir, session_id, transcript_path |
| r3 | SubagentStop | agent_id, agent_transcript_path, agent_type, background_tasks, cwd, effort, hook_event_name, last_assistant_message, permission_mode, prompt_id, scratchpad_dir, session_crons, session_id, stop_hook_active, transcript_path |
| r4 | PreToolUse | cwd, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_use_id, transcript_path |
| r4 | PostToolUse | cwd, duration_ms, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_response, tool_use_id, transcript_path |
| r4 | SubagentStart | agent_id, agent_type, cwd, hook_event_name, prompt_id, scratchpad_dir, session_id, transcript_path |
| r4 | SubagentStop | agent_id, agent_transcript_path, agent_type, background_tasks, cwd, effort, hook_event_name, last_assistant_message, permission_mode, prompt_id, scratchpad_dir, session_crons, session_id, stop_hook_active, transcript_path |
| py_fg | PreToolUse | cwd, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_use_id, transcript_path |
| py_fg | PostToolUse | cwd, duration_ms, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_response, tool_use_id, transcript_path |
| py_fg | SubagentStart | agent_id, agent_type, cwd, hook_event_name, prompt_id, scratchpad_dir, session_id, transcript_path |
| py_fg | SubagentStop | agent_id, agent_transcript_path, agent_type, background_tasks, cwd, effort, hook_event_name, last_assistant_message, permission_mode, prompt_id, scratchpad_dir, session_crons, session_id, stop_hook_active, transcript_path |
| py_bg | PreToolUse | cwd, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_use_id, transcript_path |
| py_bg | PostToolUse | cwd, duration_ms, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_response, tool_use_id, transcript_path |
| py_bg | SubagentStart | agent_id, agent_type, cwd, hook_event_name, prompt_id, scratchpad_dir, session_id, transcript_path |
| py_bg | SubagentStop | agent_id, agent_transcript_path, agent_type, background_tasks, cwd, effort, hook_event_name, last_assistant_message, permission_mode, prompt_id, scratchpad_dir, session_crons, session_id, stop_hook_active, transcript_path |
| rs_fg | PreToolUse | cwd, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_use_id, transcript_path |
| rs_fg | PostToolUse | cwd, duration_ms, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_response, tool_use_id, transcript_path |
| rs_fg | SubagentStart | agent_id, agent_type, cwd, hook_event_name, prompt_id, scratchpad_dir, session_id, transcript_path |
| rs_fg | SubagentStop | agent_id, agent_transcript_path, agent_type, background_tasks, cwd, effort, hook_event_name, last_assistant_message, permission_mode, prompt_id, scratchpad_dir, session_crons, session_id, stop_hook_active, transcript_path |
| rs_bg | PreToolUse | cwd, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_use_id, transcript_path |
| rs_bg | PostToolUse | cwd, duration_ms, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_response, tool_use_id, transcript_path |
| rs_bg | SubagentStart | agent_id, agent_type, cwd, hook_event_name, prompt_id, scratchpad_dir, session_id, transcript_path |
| rs_bg | SubagentStop | agent_id, agent_transcript_path, agent_type, background_tasks, cwd, effort, hook_event_name, last_assistant_message, permission_mode, prompt_id, scratchpad_dir, session_crons, session_id, stop_hook_active, transcript_path |

## SubagentStart fields against the dispatch payloads of the same session

| field | starts | value found in PreToolUse payloads (sum over starts) | of possible | found in PostToolUse answers (sum) |
|:--|--:|--:|--:|--:|
| agent_id | 28 | 0 | 112 | 28 |
| agent_type | 28 | 112 | 112 | 112 |
| cwd | 28 | 112 | 112 | 112 |
| prompt_id | 28 | 112 | 112 | 112 |
| scratchpad_dir | 28 | 112 | 112 | 112 |
| session_id | 28 | 112 | 112 | 112 |
| transcript_path | 28 | 112 | 112 | 112 |

## Runs

| run | event order (P pre, A answer, S start, E stop) | start lines | start lines with name_unconfirmed | start names that differ from the end line's name | `named` lines | note path correct |
|:--|:--|--:|--:|--:|--:|:--|
| r2 | PSPSPSPSEAEAEAEA | n/a | n/a | n/a | n/a | n/a |
| r3 | PASPASPASPASEEEE | n/a | n/a | n/a | n/a | n/a |
| r4 | PSPSPSPSEAEAEAEA | n/a | n/a | n/a | n/a | n/a |
| py_fg | PSPSPSPSEAEEAEAA | 4 | 0 | 0 | 4 | 4 of 4 workers |
| py_bg | PASPASPASPASEEEE | 4 | 0 | 0 | 1 | 4 of 4 workers |
| rs_fg | PASPASPPASSAEEEE | 4 | 2 | 0 | 3 | 4 of 4 workers |
| rs_bg | PASPASPPASASEEEE | 4 | 0 | 0 | 1 | 4 of 4 workers |
