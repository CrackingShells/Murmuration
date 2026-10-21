## S-w07-author-w07-2-1
The prompt's transcript record is not on disk while the UserPromptSubmit hooks run, and appears right after they exit. With the branch script as a hook (it polls for 0.3 s) the record became readable 0.30 to 0.38 s after hook start in 10 of 10 first prompts; with a probe hook that returned at once, 0.088 s (first prompt) and 0.045 s (a later prompt). A first test, not saved, had a probe poll for 2 s inside the hook and the transcript file was created 2.0 s after hook start. This fits "the platform persists the prompt after the hooks finish", but explorer-w07-f saw the record's timestamp 0.2 s and 0.9 s before the hook's end in Desktop (n = 2), which does not tell where the write happens. Is Desktop different from headless here? Nothing in my runs says so, and nothing says it is the same.
refs: __reports__/wave-07/author-w07-2/q2_live.txt, q2_probe.jsonl, q2_runs.jsonl; __instrumenta__/w07c2_probe_hook.py

## S-w07-author-w07-2-2
The fields that tell a Desktop spawned session's first message from a headless `claude -p` are only `entrypoint` in the record and `CLAUDE_CODE_ENTRYPOINT` in the hook's environment, and both are inherited by a `claude -p` started from a Desktop session's Bash tool. The lab's own headless probes therefore look exactly like Desktop sdk prompts (1880 of the 1882 sdk-origin records without an origin object say `claude-desktop`). The PI's decision (keep sdk-cli because a person may run a lab headless) can only hold for runs started from a terminal; the rule cannot see a person's `-p` run started under the Desktop. `scratchpad_dir` was in the payload of the 13 Desktop-environment sessions and absent in the one terminal-like session: n = 1, unexplained, not tested further.
refs: __reports__/wave-07/author-w07-2/fields_by_origin.txt, q2_probe.jsonl (rows f00 and t00), q1_classification.txt

## S-w07-author-w07-2-3
q1 and q3a pass and q2 fails, so the same file is both right and useless in headless sessions. q1 replays the lookup on the file prefix up to each prompt's first record, which assumes the record is on disk when the hook runs; q2 shows it is not. The replay could never have caught that; only a live run with the real hook could. The registered q1 did not claim otherwise, but it is the check one would read first.
refs: __reports__/wave-07/author-w07-2/q1_classification.txt, q2_live.txt

## S-w07-author-w07-2-4
The q1 population is every project folder with "urmuration" in its name, read live, so it contains my own scratch sessions, the other agents' sessions and the PI's, and grows during the wave (1802 files at my first run, 1830 at my last, in about 25 minutes of work). The explorer's numbers (20 human, 476 sdk) came from fixed folder sets; mine (96 human, about 1880 sdk-origin) come from a larger, moving set. A verifier will get different totals; the category rule and the zero-error count are what should reproduce.
refs: __reports__/wave-07/author-w07-2/q1_classification_first_run.txt, q1_classification.txt

## S-w07-author-w07-2-5
In q3b the miss case costs +318 ms at the median, and that is the live headless case, so the registered q3 pass (record present: +0.0 ms to +0.5 ms) describes a situation that live sessions did not produce in 14 of 14 prompts. I report the table both ways; I did not test whether a hook that returns at once and leaves a detached child to wait for the record works end to end (the probe's child found the record in 2 sessions) because the brief caps live sessions at 14, all used.
refs: __reports__/wave-07/author-w07-2/q3_q4.txt, q2_probe.jsonl (rows p00, r-p00)

## S-w07-author-w07-2-6
A resumed session (r-f00, 0.339 s with both hooks) behaved like a first prompt in how long the record took: the transcript file already existed (446 KB) but the new prompt's record was not readable until the hooks exited. So "file exists" is not "record exists", which the explorer's n = 2 could not separate.
refs: __reports__/wave-07/author-w07-2/q2_live.txt (rows r-f00, r-p00)

## S-w07-author-w07-2-7
Two hook rows with the identical command in one event ran once: my "sync crash" and "async crash" rows were merged, and the survivor was the async one. The v1 crash comparison with a sync control therefore did not happen, and all 12 sessions were gone. Nothing in the debug log says a row was merged; I found it from the single "moved to the background" line and the single traceback. Is deduplication by command string documented, and does it keep the first or the last row?
refs: __reports__/wave-07/author-w07-2/v1/dbg-mixed.hooklines.txt, __instrumenta__/w07c5_run.py (the mixed plugin)

## S-w07-author-w07-2-8
The async crash left an [ERROR] line in the debug log and nothing in the transcript, while explorer-w07-c found an `async_hook_response` record with `exitCode: 1` for an async hook that exited 1. I searched my transcript for `exitCode`, `async_hook_response`, `hook_non_blocking` and the module name and found none. Different hook event (UserPromptSubmit here, PostToolUse there), or a different build of the record writer, or my search missed it; not resolved.
refs: __reports__/wave-07/author-w07-2/v1/dbg-mixed.hooklines.txt; __reports__/wave-07/explorer-w07-c/00-findings_v0.md (async failure row)

## S-w07-author-w07-2-9
In every session the time from the user record to the first API request (0.2 to 0.5 s) is about the length of the user-level sync hook `inject_plan_directive.py` (177 to 206 ms), not of anything of ours. So the cost of any plugin hook on UserPromptSubmit is hidden behind the user's own hook in parallel, in this environment. A machine without that hook would show our hook's own cost; not measured. Also: the r2/r4 split into inherited and terminal-like sessions was my design to tell "found and dropped" from "cancelled"; the registered text says "10 headless first prompts" without it.
refs: __reports__/wave-07/author-w07-2/v1/r2_r3_r4_r5_live.txt, dbg-f00.hooklines.txt
