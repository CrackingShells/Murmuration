| run | N siblings | event | start spread (last-first t0) ms, median over calls | consecutive start gap ms, median | platform duration per hook ms, median / p90 | sleeper calls: first start to last end ms (sleep 500 each) | tool_use to tool_result ms, median |
|:--|--:|:--|--:|--:|:--|--:|--:|
| sib1 | 1 | PreToolUse | 0.0 | None | 114.0 / 599 | 509.5 | 314.5 |
| sib1 | 1 | PostToolUse | 0.0 | None | 116.0 / 171 | n/a | 314.5 |
| sib8 | 8 | PreToolUse | 311.7 | 40.4 | 365.0 / 779 | 859.6 | 985.0 |
| sib8 | 8 | PostToolUse | 271.4 | 39.0 | 284.0 / 454 | n/a | 985.0 |
| exec1 | 1 | PreToolUse | 0.0 | None | 42.5 / 539 | 506.8 | 174.0 |
| exec1 | 1 | PostToolUse | 0.0 | None | 36.0 / 54 | n/a | 174.0 |
| exec8 | 8 | PreToolUse | 132.3 | 15.0 | 133.5 / 626 | 644.6 | 444.5 |
| exec8 | 8 | PostToolUse | 128.8 | 13.9 | 97.5 / 196 | n/a | 444.5 |
