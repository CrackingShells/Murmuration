## S-w08-research-pi-1
I wrote two clock times into the wave note ("00:45", "01:05") that were estimates; the commits say 00:29 and 00:32, and `date` said 00:53 when I wrote "01:05". Open item 5 already records this habit (w05-c9). Knowing it did not stop it. The PI has no clock in its context except what a tool prints; a time in a note should come from `date` or a commit, and nothing in the wave template or the skill says so.
refs: __statera__/wave-08.md (Reassessments headings, corrected in the two commits after 1730b71); `git log --format='%h %ad' --date=format:%H:%M`

## S-w08-research-pi-2
w08-c1/w08-c4 passed 3,821 replayed events, 19 fall-back cases and a verifier's own 651-event replay, and `python3 scripts/budget.py --selftest` failed at the first merge: the selftest asserts that every budget row runs `run_hook.py budget`, and the branch points the rows at the binary. Neither the author's e1–e4 nor the verifier ran the scripts' own selftests, and no protocol in the lab lists "every `--selftest` passes on the merged tree" as a landing step. Fixing the selftest edits `budget.py`, which moves the scripts hash the manifest pins: the coupling of a second implementation showed up on the first day.
refs: merge 15d4c94 on claude/murmuration-wave-8-928ebd; `scripts/budget.py` selftest (the `argv(h)[-2].endswith("run_hook.py")` assertion); `bin/manifest.json` (`scripts_sha256`)
