| event | record | command label / status message | n | median ms | p90 ms | sum s |
|:--|:--|:--|--:|--:|--:|--:|
| SubagentStart | hook_success | Loading the colgrep search policy | 31 | 305 | 1240 | 15.9 |
| SubagentStart | hook_success | Loading tool routing policy... | 31 | 132 | 662 | 10.3 |
| PreToolUse | hook_cancelled | uv run --no-project --quiet python "${CLAUDE_PLUGIN_ROOT}/ho | 1 | 10238 | 10238 | 10.2 |
| SubagentStart | hook_success | python3 "${CLAUDE_PLUGIN_ROOT}/scripts/budget.py" | 15 | 515 | 1072 | 10.1 |
| PostToolBatch | hook_success | python3 "${CLAUDE_PLUGIN_ROOT}/scripts/budget.py" | 10 | 110 | 316 | 1.6 |
| SessionStart | hook_success | Loading the colgrep search policy | 1 | 531 | 531 | 0.5 |
| SessionStart | hook_success | Loading tool routing policy... | 1 | 287 | 287 | 0.3 |
