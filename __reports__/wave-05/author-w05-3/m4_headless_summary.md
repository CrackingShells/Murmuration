# m4: three headless runs of the second lean build (ede2770 scripts, exported at 54eaaf8), one sonnet explorer each (haiku parent), 150 station files, no --max-budget-usd

| run | role | budget B USD | what it did | run total USD (total_cost_usd) | wall s |
|:--|:--|--:|:--|--:|--:|
| m4a | pilot (excluded) | 0.30 | read all 150 files, handed back itself at 95% after notes at 51, 75, 90% | 0.312 | 260 |
| m4b | pilot (excluded) | 0.05 | handed back at 110% after the over-budget note (finish or hand back) | 0.051 | 66 |
| m4c | decisive | 0.05 | told to go on past any note; block at 164%; handed back; hand-back delivered | 0.099 | 118 |

## m4c: the hook log (`__statera__/harness.jsonl` of the run's lab, identifiers left out)

| event | requests | used USD | fraction of B |
|:--|--:|--:|--:|
| note | 7 | 0.025 | 0.51 |
| note | 14 | 0.039 | 0.78 |
| note | 17 | 0.045 | 0.90 |
| note | 18 | 0.047 | 0.94 |
| note | 20 | 0.051 | 1.02 |
| note | 21 | 0.054 | 1.08 |
| stop | 22 | 0.082 | 1.64 |
| end | 23 | 0.094 | 1.88 |

## m4c: what the worker's transcript shows (records of its own subagent file; `hook_additional_context` and `hook_blocking_error` are the platform's attachment types)

- notes at 51%, 78%, 90%, 94%, 102%, 108% arrive as `hook_additional_context` attachments of `PostToolUse:Bash` and are in the next request's input (6 of 6).
- at 164% the PostToolUse hook answers `decision: block`; the platform records a `hook_blocking_error` attachment with the text "Spent 0.08 of USD 0.05 (164%); ... Hand back now with SubagentHandback ..." (1 of 1), and the worker's next assistant record calls SubagentHandback.
- the hand-back file of the run holds one section, `event=PostToolUse status=delivered`.

md5 of ~/.claude/plugins/installed_plugins.json before and after: 755ec41b514a71a3fdd6e869a5bf2d58 both. Seeds 20261101 (m4a), 20261102 (m4b), 20261103 (m4c) fix the station files; the model has no seed.
