## S-w07-reproducer-w07-2-1
The record of a prompt reaches the transcript file only after the sync UserPromptSubmit hooks return, yet its in-memory timestamp precedes the hook start (explorer-w07-f, n=2). Both facts hold in my runs: the v0 sync script (0.3 s poll) missed in 2 of 2 (entry stored, hook 0.45 and 0.60 s), while the v1 async hook found it 0.13 to 0.4 s after its start in 7 of 7. What the platform waits for before persisting is still an inference from timings.
refs: __reports__/wave-07/reproducer-w07-2/live_table.txt (rows v0-i0, v0-i1, i0..i2, c0, c1, s0, s1), dbg-v0-i0.hooklines.txt

## S-w07-reproducer-w07-2-2
A crash of user_words.py is loud under a sync row (a `hook_non_blocking_error` attachment with the traceback and exitCode 1 lands in the session transcript) and silent under an async row (one [ERROR] line in the debug file, nothing in the transcript). So v1 turns the lab's recorder into something that can stop recording with nobody told. Does the lab want a different visibility channel (for example a canary line in `__statera__`)?
refs: dbg-x-sync.hooklines.txt, dbg-x-async.hooklines.txt, runs.jsonl rows x-sync, x-async; transcripts `~/.claude/projects/*reproducer-w07-2-live-lab-x-sync` (attachment type hook_non_blocking_error)

## S-w07-reproducer-w07-2-3
The interactive typed-prompt path (origin human) and a quit right after a prompt were not run: `claude` under a python pty exits within 0.7 s ("Skipping SessionEnd:other hook execution - workspace trust not accepted"), before any prompt, even with a window size set. Cause not found (trust dialog, terminal query, or a TTY check). So the one path a person really uses (interactive) is covered only by the lab's recorded transcripts (origin human 2114 records, 0 dropped by the rule) and by the offline replay, not by a live async hook. The prompt-then-quit cancellation risk is unmeasured.
refs: /private/tmp/murmuration-w07/reproducer-w07-2/live/pty-p1.txt, dbg-p1.hooklines.txt (not copied: no hook ran)

## S-w07-reproducer-w07-2-4
Offline, 3 of 63 entries of the user's words files have only dropped matches: all three are the known wrong ones (first message of a spawned session, "Background (from the session that started this one)"), so the rule drops no typed entry I could match; 8 entries match no record by their first 50 characters (quoted text, `>` prefix) and could not be checked. The text-only fallback `other` category (1472 records `none:None/None/claude-desktop`, plus 9 `cli`) is still decided by the text rule, so old-version peer or harness messages without origin keep reaching the file as on main.
refs: __reports__/wave-07/reproducer-w07-2/r1_words_entries.txt, r1.txt

## S-w07-reproducer-w07-2-5
A FIFO as the transcript path hangs the hook for both main's script and v1's (killed at the 10 s timeout, prompt not stored): not a regression, but a crashing-or-hanging transcript read loses a prompt in v1 exactly as in main. With async, the hang blocks nothing.
refs: __reports__/wave-07/reproducer-w07-2/fail_v1.txt, fail_main.txt (row "FIFO")

## S-w07-reproducer-w07-2-6
Time from the user record to the first api-request: v1 async median 0.158 s (n=7, 0.131 to 0.352), main sync 0.250 s (n=4, 0.149 to 0.463), v0 sync 0.634 and 0.495 s (n=2). The floor is the user-level sync hook inject_plan_directive.py (about 0.1 to 0.25 s). The arms are not randomised or paired (interleaved in a fixed order), so the main/v1 difference of about 0.09 s is not shown to be more than noise at these n.
refs: __reports__/wave-07/reproducer-w07-2/live_table.txt
