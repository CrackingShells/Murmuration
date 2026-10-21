| event | record | command label / status message | n | median ms | p90 ms | sum s |
|:--|:--|:--|--:|--:|--:|--:|
| SubagentStart | hook_success | Loading the colgrep search policy | 128 | 276 | 654 | 48.8 |
| SubagentStart | hook_success | Loading tool routing policy... | 128 | 164 | 381 | 30.8 |
| SubagentStart | hook_success | python3 "${CLAUDE_PLUGIN_ROOT}/scripts/budget.py" | 20 | 605 | 1085 | 14.1 |
| UserPromptSubmit | hook_success | plugin:probe:stub/record | 52 | 2 | 10 | 12.2 |
| PreToolUse | hook_cancelled | uv run --no-project --quiet python "${CLAUDE_PLUGIN_ROOT}/ho | 1 | 10238 | 10238 | 10.2 |
| SessionStart | hook_success | bash ${CLAUDE_PLUGIN_ROOT}/../logger.sh SessionStart | 16 | 450 | 594 | 7.4 |
| SubagentStart | hook_success | bash ${CLAUDE_PLUGIN_ROOT}/../logger.sh SubagentStart@probe: | 6 | 588 | 1233 | 4.4 |
| SubagentStart | hook_success | bash ${CLAUDE_PLUGIN_ROOT}/../logger.sh SubagentStart | 6 | 541 | 1067 | 4.2 |
| SessionStart | hook_success | Loading the colgrep search policy | 4 | 516 | 531 | 1.9 |
| PostToolBatch | hook_success | python3 "${CLAUDE_PLUGIN_ROOT}/scripts/budget.py" | 10 | 110 | 316 | 1.6 |
| SessionStart | hook_success | Loading tool routing policy... | 4 | 286 | 287 | 1.0 |
| SessionStart | hook_success | python3 "${CLAUDE_PLUGIN_ROOT}/scripts/resume_brief.py" | 1 | 179 | 179 | 0.2 |
| PostToolUse | hook_success | plugin:probe:stub/record | 35 | 3 | 5 | 0.1 |
| PreToolUse | hook_success | plugin:probe:stub/record | 25 | 3 | 6 | 0.1 |
| Stop | hook_success | plugin:probe:stub/record | 20 | 3 | 6 | 0.1 |
| SubagentStart | hook_success | plugin:probe:stub/record | 11 | 3 | 4 | 0.0 |
| SubagentStop | hook_success | plugin:probe:stub/record | 12 | 2 | 4 | 0.0 |
| PostToolBatch | hook_success | plugin:probe:stub/record | 21 | 1 | 2 | 0.0 |
| UserPromptExpansion | hook_success | plugin:probe:stub/record | 1 | 11 | 11 | 0.0 |
| SessionStart | hook_success | plugin:probe:stub/record | 3 | 2 | 2 | 0.0 |
| PreToolUse | hook_success | plugin:probe:stub/decide | 1 | 5 | 5 | 0.0 |
