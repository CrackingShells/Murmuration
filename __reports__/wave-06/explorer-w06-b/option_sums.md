| build (wave 4: 1788 starts, main 193) | serial wall s | CPU s | wall vs current |
|:--|--:|--:|--:|
| current (every registration starts budget.py / handback.py / ...) | 160.9 | 75.1 | 1.00 |
| sh gate on the main thread's PostToolUse and PostToolBatch (193 starts) | 150.1 | 67.7 | 0.93 |
| ... plus one dispatcher for SubagentStop and the hand-back PostToolUse (52 starts folded) | 145.4 | 65.5 | 0.90 |
| every start a compiled binary (std only), no gate | 91.2 | 10.7 | 0.57 |
| compiled binary, sh gate on the main thread | 87.8 | 10.2 | 0.55 |
| resident server, every per-call and lifecycle hook an mcp_tool (SessionStart/End stay commands) | 3.6 | 0.0 | 0.02 |
