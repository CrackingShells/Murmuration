## m1 fields (platform stdin, recorded by a command hook beside the server, against what the server received)
| event | server calls | all fields equal to the platform's stdin | fields requested | requested fields empty on every call | derived subagent transcript path exists |
| PostToolUse | 36 | 36 | agent_id, agent_transcript_path, agent_type, cwd, hook_event_name, permission_mode, tool_input_command, tool_name, transcript_path | agent_transcript_path | 22 of 22 |
| PostToolBatch | 34 | 34 | agent_id, agent_transcript_path, agent_type, cwd, hook_event_name, permission_mode, tool_calls, transcript_path | agent_transcript_path | 16 of 16 |
| PreToolUse:Agent | 10 | 10 | agent_id, cwd, hook_event_name, tool_input_name, tool_input_prompt, tool_input_subagent_type, tool_name, tool_use_id | agent_id | - |
| SubagentStart | 6 | 6 | agent_id, agent_transcript_path, agent_type, cwd, hook_event_name, permission_mode, transcript_path | agent_transcript_path, permission_mode | 6 of 6 |
| PreToolUse:SubagentHandback | 4 | 4 | agent_id, agent_transcript_path, agent_type, cwd, hook_event_name, tool_name, transcript_path | agent_transcript_path | 4 of 4 |
| PostToolUse:SubagentHandback | 4 | 4 | agent_id, agent_transcript_path, agent_type, cwd, hook_event_name, permission_mode, tool_input_message, tool_name, transcript_path | agent_transcript_path | 4 of 4 |
| SubagentStop | 6 | 6 | agent_id, agent_transcript_path, agent_type, cwd, hook_event_name, last_assistant_message, permission_mode, transcript_path | - | 6 of 6 |

## m2 firing (server log against what the transcript implies: runs t_*, v*, m3_on_*, m3_open; one row per thread and event)
rows equal: 273
rows NOT equal: 0
rows not equal: 0; fired totals: {('PostToolUse', 'main'): 65, ('PostToolBatch', 'main'): 66, ('PreToolUse:Agent', 'main'): 43, ('PostToolUse', 'worker'): 121, ('PostToolBatch', 'worker'): 103, ('SubagentStart', 'worker'): 39, ('SubagentStop', 'worker'): 40, ('PreToolUse:SubagentHandback', 'worker'): 37, ('PostToolUse:SubagentHandback', 'worker'): 37}

## m3 request 0 (ON = plugin with the server answering nothing, OFF = same agents, no server, OPEN = control with the tool allowed)
| arm | run | thread | request-0 input tokens | shapeHash[:10] | tools in request | first user message sha[:8] |
|:--|:--|:--|--:|:--|--:|:--|
| off | m3_off0 | main | 46852 | 5ea9a0e71c | 15 | 7b149e5a |
| off | m3_off0 | worker a0db35 | 5941 | 01df2c578d | 5 | f24dfa45 |
| off | m3_off0 | worker aee751 | 5941 | 01df2c578d | 5 | 73a1873c |
| off | m3_off1 | main | 46417 | 5ea9a0e71c | 15 | 7b149e5a |
| off | m3_off1 | worker a0ebe5 | 5943 | 01df2c578d | 5 | f24dfa45 |
| off | m3_off1 | worker a80386 | 5943 | 01df2c578d | 5 | 73a1873c |
| off | m3_off2 | main | 46853 | 5ea9a0e71c | 15 | 7b149e5a |
| off | m3_off2 | worker a33b00 | 5942 | 01df2c578d | 5 | 73a1873c |
| off | m3_off2 | worker a989f6 | 5942 | 01df2c578d | 5 | f24dfa45 |
| on | m3_on_0 | main | 46386 | 5ea9a0e71c | 15 | 7b149e5a |
| on | m3_on_0 | worker a3dc25 | 5945 | 01df2c578d | 5 | f24dfa45 |
| on | m3_on_0 | worker adbcc4 | 5945 | 01df2c578d | 5 | 73a1873c |
| on | m3_on_1 | main | 46412 | 5ea9a0e71c | 15 | 7b149e5a |
| on | m3_on_1 | worker a10f22 | 5938 | 01df2c578d | 5 | 73a1873c |
| on | m3_on_1 | worker a32daa | 5938 | 01df2c578d | 5 | f24dfa45 |
| on | m3_on_2 | main | 46852 | 5ea9a0e71c | 15 | 7b149e5a |
| on | m3_on_2 | worker a12a71 | 5941 | 01df2c578d | 5 | 73a1873c |
| on | m3_on_2 | worker a13ced | 5941 | 01df2c578d | 5 | f24dfa45 |
| open | m3_open | main | 46869 | 5ea9a0e71c | 16 | 7b149e5a |
| open | m3_open | worker af0280 | 6006 | 337e7f85ac | 7 | f24dfa45 |
| open | m3_open | worker af6e8f | 6006 | 337e7f85ac | 7 | 73a1873c |

## m4 outage
| run | server starts | server calls | hook_success / non_blocking_error / cancelled(timedOut) records | waits >= 1 s: event settled in (s) | refused Agent call: refusal seen / worker started | model's final text mentions a hook failure |
|:--|--:|--:|:--|:--|:--|:--|
| m4a0 | 2 | 7 | 6 / 0 / 0 | - | no / 0 | no |
| m4a1 | 2 | 20 | 18 / 0 / 0 | - | yes / 0 | no |
| m4b0 | 1 | 2 | 2 / 25 / 0 | - | no / 1 | no |
| m4b1 | 1 | 2 | 2 / 26 / 0 | - | no / 1 | no |
| m4c0 | 1 | 2 | 2 / 22 / 1 | PostToolUse 10.0; PostToolBatch 10.0; PostToolUse 7.5; PostToolUse 7.4 | no / 1 | no |
| m4c1 | 1 | 2 | 2 / 23 / 1 | PostToolUse 10.0; PostToolBatch 10.0; PostToolUse 7.9; PostToolUse 7.9 | no / 1 | no |

## m5 latency (server alone, runs v*)
| hook (event:tool) | n | median ms | p90 ms | max ms |
|:--|--:|--:|--:|--:|
| PostToolBatch | 102 | 1.0 | 1 | 3 |
| PostToolUse:Agent | 25 | 6.0 | 7 | 9 |
| PostToolUse:Bash | 60 | 1.0 | 2 | 2 |
| PostToolUse:SubagentHandback | 50 | 5.5 | 7 | 13 |
| PreToolUse:Agent | 25 | 2.0 | 3 | 3 |
| PreToolUse:SubagentHandback | 25 | 2.0 | 4 | 5 |
| SubagentStart:wt:worker | 25 | -1.0 | -1 | -1 |
| SubagentStop | 25 | 0.0 | 1 | 1 |
| all (transcript durationMs) | 337 | 1.0 | 6 | 13 |
| all mcp_tool calls (debug log) | 337 | 1.0 | 6 | 15 |
| SubagentStart (debug log) | 25 | 6.0 | 6 | 15 |

## m6 effects
| run | effect | nonce | in the record that carries it to the model | quoted by the model in a later message |
|:--|:--|:--|:--|:--|
| t_auto0 | inject (SubagentStart) | 6e9bda31 | worker:hook_additional_context | main, worker |
| t_auto0 | block (PostToolUse) | b7cdf2c6 | worker:hook_blocking_error | main, worker |
| t_auto0 | inject (SubagentStart) | 827d763d | worker:hook_additional_context | main, worker |
| t_auto0 | block (PostToolUse) | 4b7e4007 | worker:hook_blocking_error | main, worker |
| t_auto0 | deny (PreToolUse:Agent) | 17cba21a | main:tool_result | main |
|  | refused call started a worker | | 0 workers whose brief holds DENYME (want 0) | |
| t_auto1 | inject (SubagentStart) | 802dc429 | worker:hook_additional_context | main, worker |
| t_auto1 | block (PostToolUse) | 18d6b8ce | worker:hook_blocking_error | main, worker |
| t_auto1 | inject (SubagentStart) | 82777666 | worker:hook_additional_context | main, worker |
| t_auto1 | block (PostToolUse) | 95c42dea | worker:hook_blocking_error | main, worker |
| t_auto1 | deny (PreToolUse:Agent) | bea1486c | main:tool_result | main |
|  | refused call started a worker | | 0 workers whose brief holds DENYME (want 0) | |
| t_byp0 | inject (SubagentStart) | 0a671a29 | main:tool_result, worker:hook_additional_context | main, worker |
| t_byp0 | block (PostToolUse) | c3154768 | main:tool_result, worker:hook_blocking_error | main, worker |
| t_byp0 | deny (PreToolUse:Agent) | e2ad6a81 | main:tool_result | main |
|  | refused call started a worker | | 0 workers whose brief holds DENYME (want 0) | |
| t_byp1 | inject (SubagentStart) | 67567b2c | worker:hook_additional_context | main, worker |
| t_byp1 | block (PostToolUse) | f35bb8ab | worker:hook_blocking_error | main, worker |
| t_byp1 | deny (PreToolUse:Agent) | f388c633 | main:tool_result | main |
|  | refused call started a worker | | 0 workers whose brief holds DENYME (want 0) | |
