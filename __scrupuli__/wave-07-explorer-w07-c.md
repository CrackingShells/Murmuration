## S-w07-explorer-w07-c-1
`asyncRewake` is documented as a background hook that wakes Claude on exit 2, but in this `-p` session it ran in the foreground: the debug log says "finished with status 2 (2572ms)" with no "moved to the background", and the tool result waited about 3 s for it. It may be a `-p` effect (nobody is idle to wake) or the field may be treated as a synchronous hook in 2.1.304. One session; I had no sessions left to separate the two.
refs: __reports__/wave-07/explorer-w07-c/async_timeline.txt (16698 to 18706 ms), __reports__/wave-07/explorer-w07-c/runs/async/dbg.log (grep `post-async-rewake`)

## S-w07-explorer-w07-c-2
A dead or hanging `http` hook with `onFailure: block` on `PostToolBatch` ends the whole session with exit code 0, `is_error: false`, empty `result` and empty stderr; only `terminal_reason: "hook_stopped"` and a transcript record say why. In the lab that would be a worker that stops with no hand-back and no SubagentStop of the lab's own making. The lab reads neither field. What does the PI see when a worker dies this way (its `Agent` result text)? Not run with a real subagent: `batch_dead` was the main thread only.
refs: __reports__/wave-07/explorer-w07-c/runs/batch_dead/run.json, runs/batch_dead/transcript.jsonl (`hook_stopped_continuation`), runs/batch_hang/run.json

## S-w07-explorer-w07-c-3
The same hook script costs 116 ms (shell form) and 36 ms (exec form, `command: python3`, `args: [...]`) as the platform records it, and the sibling launch interval is 40 ms against 14 ms. The micro-benchmark outside Claude Code shows the same direction (bash -c 107 ms, sh -c 152 ms, exec 54 ms) but `sh -c ':'` alone costs 81 ms and `bash -c ':'` 40 ms, which is more than a shell should cost on an M3 Pro. All numbers come from a machine at load 9. Is the shell start the "unexplained floor" of wave 7's second bullet? And does the platform use `sh`, or the `CLAUDE_CODE_SHELL` shell, for hooks? I only set `CLAUDE_CODE_SHELL=/bin/bash` as the brief says, and never ran the other.
refs: __reports__/wave-07/explorer-w07-c/shell_vs_exec.md, __reports__/wave-07/explorer-w07-c/siblings_table.md

## S-w07-explorer-w07-c-4
In the one run with the user's own settings (`runs/async`), the user's `colgrep_policy` PreToolUse hook (`uv run python ...`) took a median 431 ms per Bash call (n = 10, max 583), against about 36 to 116 ms for a lean Python hook; SessionStart hooks of the user took 573 to 943 ms. This is outside the plugin, but it is the largest hook cost per Bash call in the PI's own environment and the seven waves of work on the lab's ten registrations never counted it. Is it also 400 ms in the PI's interactive session (the run was at load 9)?
refs: __reports__/wave-07/explorer-w07-c/runs/async/dbg.log (lines `colgrep_policy`)

## S-w07-explorer-w07-c-5
The `if` field with rules like `Bash(echo H-DOWN*)` matched a longer command (`echo H-DOWNC`), as globs do, and I lost three sessions of 15 to it. The lab's 30 `if` rows on Write/Edit/NotebookEdit use path globs, but its Bash guard is unconditional, so it is unaffected. What does bother me: the docs say `if` holds exactly one permission rule, so merging the 30 rows into fewer cannot use alternation unless braces work in the glob, and nobody has tested braces. That test costs one session.
refs: __reports__/wave-07/explorer-w07-c/runs/http_pre_run1_prefixbug/, hooks/hooks.json (the `if` rows), docs_hooks_2026-10-22.md (search "exactly one permission rule")
