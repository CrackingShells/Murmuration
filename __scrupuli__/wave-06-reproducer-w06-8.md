## S-w06-reproducer-w06-8-1
In ordinary_default the explorer reported it had "no SubagentHandback tool", while in ordinary_auto (same agent file, same brief) it called `SubagentHandback` twice. Capture still worked (SubagentStop path, event=SubagentStop in the hand-back file), so nothing was lost, but the worker's tool list differs by permission mode or by `--allowedTools`. Is `SubagentHandback` deferred or filtered when `--allowedTools` is given, and does the gate (which only fires on that tool) therefore not apply to such workers?
refs: /private/tmp/murmuration-w06/reproducer-w06-8/runs/ordinary_default/lab/__statera__/handbacks/wave-99-explorer-w99-1.md, /private/tmp/murmuration-w06/reproducer-w06-8/runs/ordinary_default/stream.jsonl, /private/tmp/murmuration-w06/reproducer-w06-8/runs/ordinary_auto/lab/__statera__/harness.jsonl (deny event)

## S-w06-reproducer-w06-8-2
The guard costs 131 to 150 ms per Bash call (debug-file `finished with status 0 (N ms)`), against the budget hook's lean start of about 100 ms: it is `python3 permission_guard.py` without `-S -I` and without a lean start, and it runs unconditionally on every Bash call of every agent (21 of 21 here). w06-c9 optimised the 8 budget/handback rows; the guard row, the most frequent PreToolUse start, was not given the same treatment. Is that intended?
refs: /private/tmp/murmuration-w06/reproducer-w06-8/runs/ordinary_auto/dbg.log (lines `Hooks: PreToolUse:Bash [python3 ".../permission_guard.py"]`), /private/tmp/murmuration-w06/reproducer-w06-8/export/hooks/hooks.json

## S-w06-reproducer-w06-8-3
The docstring of `scripts/permission_guard.py` still says the hook rows start the script "only when a cheap `if` rule has matched (`Bash(*bypass*)` ...), so an ordinary tool call starts no process", but hooks.json at 47d2cd2 has an unconditional Bash row (v3) and the guard started on every Bash call here. The text is stale against the build.
refs: /private/tmp/murmuration-w06/reproducer-w06-8/export/scripts/permission_guard.py lines 4-6, /private/tmp/murmuration-w06/reproducer-w06-8/runs/ordinary_auto/guard.log

## S-w06-reproducer-w06-8-4
The denied Bash result shows the model the words `PreToolUse:Bash hook error: permission_guard (G1): ...`, although the hook exited 0 with a deny decision and no `hook_*_error` record exists. A reader grepping transcripts for "hook error" will count denials as errors; a check keyed on the record types `hook_non_blocking_error` and `hook_cancelled` will not. Which of the two does the lab mean by "hook error"?
refs: /private/tmp/murmuration-w06/reproducer-w06-8/runs/bypass_default/stream.jsonl (the first tool_result), /private/tmp/murmuration-w06/reproducer-w06-8/runs/bypass_default/dbg.log

## S-w06-reproducer-w06-8-5
Each Bash call starts two PreToolUse:Bash hooks on this machine, the guard and the user's colgrep-mcp policy hook (`uv run --no-project --quiet python ...`, 9 finishes in ordinary_auto). Counting "PreToolUse:Bash starts" from the stream gives 18 for 9 calls; only `guard.log` or the debug-file command string separates the two. Any future "once per Bash call" check must key on the command, not the hook name.
refs: /private/tmp/murmuration-w06/reproducer-w06-8/runs/ordinary_auto/dbg.log, /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/blissful-villani-34edd8/__instrumenta__/w06c14_combo_smoke_check.py

## S-w06-reproducer-w06-8-6
The guard answers an event whose `tool_input` is null (and probably one with no `command` key) with allow, while empty stdin, non-JSON, `[]` and an integer `command` give deny. Equal under both starts, so it is not a w06-c14 matter, but the fail-closed story is not uniform: a Bash event with no command is let through.
refs: `python3 -I __instrumenta__/w06c14_v2_cmd_equal_own.py <old tree> <new tree>` (row "malformed: null tool_input")

## S-w06-reproducer-w06-8-7
w06-c14's live fail-closed test uses an unreadable script, exit 2, which the platform blocks by convention whatever `onFailure` says; it does not show that `"onFailure": "block"` does anything. My crash test (exit 1) does: the call was blocked in both trees. Whether the field is documented or only the exit-2 rule holds on another platform version is not established here.
refs: /private/tmp/murmuration-w06/reproducer-w06-8/runs/r2_crashnew_failclosed_default/stream.jsonl, /private/tmp/murmuration-w06/reproducer-w06-8/runs/r2_crashnew_failclosed_default/dbg.log
