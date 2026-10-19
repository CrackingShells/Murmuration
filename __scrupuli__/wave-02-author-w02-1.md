## S-w02-author-w02-1-1
Running the patched script with no `git` on PATH from the main checkout prints a clean section with USD 1.11 and 30 sessions, and says nothing about the 274 sessions of the worktree it did not look for. A spend figure that is wrong without a warning is the failure the plugin is meant to avoid. Should the section print a `!` line when `git worktree list` fails or the lab is in a repository with no worktree data? I did not add it (nothing asked for it).
refs: __reports__/reflective_run/w02/author-w02-1/after_main_nogit.txt, scripts/lab_status.py (git_worktrees)

## S-w02-author-w02-1-2
In `auto` mode every subagent request of this team is truncated (w01-c2), so every subagent row prints `+`. The detector is correct and the mark is uniform, hence it tells a reader nothing about which agents are worse. Only 197 of 314 subagent files (all headless runs in other modes) are unmarked. Is the mark worth its line in the shipped table, or should the table print only a single note when all rows are marked? An exact per-run figure needs OpenTelemetry set outside the plugin.
refs: __reports__/reflective_run/w02/author-w02-1/check.txt (item 4), __pondus__/w01-c2.md

## S-w02-author-w02-1-3
`lab_status.py` grew from 880 to 1068 lines (spend section 174 to 287, its selftest 65 to 130), which is against the leanness aim of the framing. The prototype's discovery was 56 lines, the reader and prices another 120. Where could it be cut: drop fast mode, web search and the long-prompt Haiku row (each is a price rule seen in no lab transcript I checked), or the 12-row agent table? I kept them because the table was cited and checked in w01-c3, not because this lab needs them.
refs: __reports__/reflective_run/w02/author-w02-1/lines_before.txt, lines_after.txt

## S-w02-author-w02-1-4
I left out the n=2 "ESTIMATE about" uplift and the wake-ups column of the w01-c3 prototype. The first printed a second, higher figure for open sessions; without it the TOTAL of a running lab is only a lower bound (64.77 at least, with this run's open session at 60.38). The wake-ups column was in the verified claim's human view but the reproducer did not check it. Does the PI want either back? The decision belongs to a claim, not to me.
refs: __pondus__/w01-c3.md (R9, human view), scripts/lab_status.py (report_spend)

## S-w02-author-w02-1-5
The scan is by the first `cwd` of a session, so sessions of the plugin's own design (here, the design session under the combinatorics project) and the 12 scratchpad sessions of this run (about 0.111 USD) are not counted. The user's question is the cost of a lab; the sessions of a lab that sits in two project folders have no reader. A `--also <session id>` option was in the prototype and I dropped it; is a lab ever in two places?
refs: __pondus__/w01-c3.md (scope, verdict "left standing" (b))

## S-w02-author-w02-1-6
When `/lab-status` is run from the main checkout (`--project` the main path), the worktree session is labelled "worktree murmuration-system-optimization-8cff9e" and the main checkout's own sessions "this checkout, sessions started below it": a person who reads it from the main checkout sees the PI's session as another worktree. The same section from the worktree says the reverse. Both are right by the path asked, but is "this checkout" the right word when the command may be run by an agent from any path?
refs: __reports__/reflective_run/w02/author-w02-1/after_main.txt, after_worktree.txt

## S-w02-author-w02-1-7
`scripts/user_words.py` shows as modified in the worktree while I worked (89 changed lines) and I did not touch it. The PI commits my files; the commit hygiene puzzle of wave 1 applies: whoever commits must stage `scripts/lab_status.py`, `skills/lab-status/SKILL.md`, `__pondus__/w02-c1.md`, `__reports__/reflective_run/w02/author-w02-1/` and `__scrupuli__/wave-02-author-w02-1.md` by name, not `-a`.
refs: git status of the worktree at the end of this claim

## symbols
none new.
