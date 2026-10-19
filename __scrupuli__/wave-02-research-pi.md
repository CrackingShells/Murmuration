## S-w02-research-pi-1
The user's most consequential instructions of the study (how to decide, how to budget workers, what
to keep, the new 6-hour budget) came through the Desktop question dialog and are absent from
`__statera__/user_words.md`. The capture hook sees only `UserPromptSubmit`; an `AskUserQuestion`
answer is a tool result. So the lab's record of the user's words misses exactly the answers the PI
asked for. A `PostToolUse` hook on `AskUserQuestion` could append the answers; untested.
refs: this run's transcript, AskUserQuestion tool result (~12:50 JST); both copies of __statera__/user_words.md (last entry 11:04)
