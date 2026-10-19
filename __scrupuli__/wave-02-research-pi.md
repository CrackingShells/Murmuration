## S-w02-research-pi-1
The user's most consequential instructions of the study (how to decide, how to budget workers, what
to keep, the new 6-hour budget) came through the Desktop question dialog and are absent from
`__statera__/user_words.md`. The capture hook sees only `UserPromptSubmit`; an `AskUserQuestion`
answer is a tool result. So the lab's record of the user's words misses exactly the answers the PI
asked for. A `PostToolUse` hook on `AskUserQuestion` could append the answers; untested.
refs: this run's transcript, AskUserQuestion tool result (~12:50 JST); both copies of __statera__/user_words.md (last entry 11:04)

## S-w02-research-pi-2
Arm A of the experiment (shipped plugin, headless `claude -p`, `--permission-mode auto`) answered the
question well (bound, iff test, existence, exact counts at de Bruijn lengths, all verified), but
wrote no `__statera__/synthesis.md`. The PI opened a second wave with one explorer and ended its turn
to wait; the platform then printed "Background tasks still running 10m after the last turn
(subagent \"Probe maximiser counts n=2^m+m\"); stopping them. Set CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0
to wait indefinitely." and the process exited 0. A lab run headless loses its ending to a 10-minute
ceiling the plugin neither knows nor sets; nothing in the plugin tells a user to set it. Cost
USD 4.88, 21 min wall.
refs: scratchpad w02/expC/A/stderr.txt; A/stdout.jsonl (last result events); A/lab/__statera__/ (no synthesis.md)
