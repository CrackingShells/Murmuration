## S-w07-author-w07-3-1
The shell form is far more expensive here than wave 6 recorded, and the platform's shell is `/bin/sh`, not `CLAUDE_CODE_SHELL`. The guard's platform-recorded start in A is 123 ms pooled (n = 71, load 3 to 5) against 65 to 72 ms in w06-c14 (load 2.4) and 36 to 42 ms in exec form (explorer-w07-c, mine 42 ms). The error text of the missing-`python3` run in A names `/bin/sh: python3: command not found`, although the runs set `CLAUDE_CODE_SHELL=/bin/bash`, so the answer to explorer-w07-c's open question (which shell runs a hook) is `/bin/sh` for hooks (one run, one error line). Why a `sh -c` costs 80 ms here when `sh :` was 33 ms in wave 6 (dyld, code signing of the interpreter under 12-concurrent sessions, the platform wrapper) is not known; the two arms ran at the same time, which loads both, but only A pays for the shell.
refs: __reports__/wave-07/author-w07-3/x4_table.md, __reports__/wave-07/author-w07-3/x3_nopy.txt (tool_results A 0), __pondus__/w06-c14.md

## S-w07-author-w07-3-2
In exec form a repeated spawn failure is reported once. With `python3` off PATH, B's first blocked Bash call says `Error occurred while executing hook command: Executable not found in $PATH: "python3"`; its second blocked call says only `failed; blocking because onFailure is "block"` with no cause; the transcript holds 1 of 3 `PostToolBatch` failure records in B and 3 of 3 in A, although the debug file has 3 `failed to start` lines in B. Deduplication of identical spawn errors is my reading; one pair, so not isolated, and no session was left to repeat it. Both calls were still blocked, so the guard failed closed, but a worker would see less text the second time.
refs: __reports__/wave-07/author-w07-3/x3_nopy.txt (tool_results B 2, attachments B)

## S-w07-author-w07-3-3
The README says Claude Code 2.1.271 or later, but the hook rows carry `onFailure: "block"`, which the docs and the changelog say needs 2.1.295. On 2.1.271 to 2.1.294 the field is presumably ignored, which would make the guard fail open on a crash; `args` (2.1.139) is not the binding minimum. Not tested (no such version is installed: 2.1.296, 2.1.302, 2.1.304 are).
refs: README.md line 72, ~/.claude/cache/changelog.md lines 620 and 5678, __reports__/wave-07/explorer-w07-c/docs_hooks_2026-10-22.md line 447

## S-w07-author-w07-3-4
The 70 ms hook saving does not show in the downstream numbers of ten pairs. Hook time per session is lower by a median 3.0 s in B (10 of 10), but the transcript's tool_use to tool_result interval has a per-pair median difference of 54 ms with a range of -598 to +597 ms (6 of 10 lower in B), and the session wall time is not lower in B (A 40.3 s, B 43.6 s). Either the hooks overlap with the classifier and the model's own wait, so the saving is off the critical path in `-p` auto mode, or the noise (model time, classifier time) hides it. The wave-07 note's argument "the classifier call dominates" would predict this; it is not shown that the hook start sits off the path.
refs: __reports__/wave-07/author-w07-3/toolgap_table.md, __reports__/wave-07/author-w07-3/x4_pairs_load.log, __reports__/wave-07/author-w07-3/x4_table.md (last block)

## S-w07-author-w07-3-5
The platform refused a standalone `sleep 100` in arm A but the same prompt ran `sleep` in arm B (guard.log of x2_1_B has a `sleep 100` allow, A has none; A's tool_result: "Blocked: standalone sleep 100"). That lost the live threshold note in A. Same model, same prompt, same plugin apart from `hooks.json`: either the model chose differently (B may have backgrounded it) or the block depends on something the hooks change. I read it as model variation; one pair.
refs: /private/tmp/murmuration-w07/author-w07-3/runs/x2_1_A/transcripts/agent-*.jsonl (tool_result), x2_1_B/guard.log (not committed: raw); __reports__/wave-07/author-w07-3/x2_live_compare.md

## S-w07-author-w07-3-6
The two rows that stay on plain `python3` (no `-S -I`) are the slowest of the exec-form hooks: `user_words` UserPromptSubmit 113.5 ms in B (n = 20), against 41 ms for `run_hook.py` with `-S -I`. They run once per user prompt, not per tool call, so the saving is small, but `-S -I` on them was outside P3's rule (command strings only for the form change) and has not been checked for `user_words.py` and `resume_brief.py` (they import `subprocess`, `datetime`, `json`, `re`, all standard library).
refs: __reports__/wave-07/author-w07-3/x4_table.md (last table, `user_words UserPromptSubmit`)

## S-w07-author-w07-3-7
A `Write` hook-denial test needed care with the guard itself: my first helper heredoc was refused by the plugin's own guard (G1) because the file text held the bypass flag literally, so every test file builds the flag from parts. The same guard that protects the lab blocks authoring its own attack tests; the brief anticipated it ("build such test commands in files written with the Write tool"), but a helper-script author who writes the flag in a Bash heredoc loses the whole command silently except for the deny text.
refs: __instrumenta__/w07c3_run_arm.py (FLAG built from parts), __instrumenta__/w07c3_x2_process.py
