## S-w02-reproducer-w02-1-1
The head's first sentence puts "equal to the sum of Claude Code's cost-state totals (224.85)" next to measured things, but for an ended session the script prints totalCostUSD itself, so the equality cannot fail. Only the author's selftest and R3 cells test the price table. A reader skimming the title may take 224.85 as a check of the price table. Should a title carry a by-construction equality at all?
refs: scripts/lab_status.py:645-647, __pondus__/w02-c1.md (head), __reports__/reflective_run/w02/reproducer-w02-1/cost_check.txt

## S-w02-reproducer-w02-1-2
The `+` is per (agent label, model) row, and two runs of one name merge into one row; the OR across copies (`have["final"] or msg["final"]`) can clear a mark when a final copy of a message sits in another file. No case in 1456 subagent files, or in the author's 23 rows, exercises either. Is the OR the right rule, or would a copy that is final in one file and unfinished in another be better marked? Untested branch.
refs: scripts/lab_status.py:590-591, __reports__/reflective_run/w02/reproducer-w02-1/key_check.txt, __reports__/reflective_run/w02/author-w02-1/rowcheck.txt

## S-w02-reproducer-w02-1-3
Without git, `/lab-status` prints a spend figure (1.11 against 65.3) with no notice, and `git_worktrees` returns [] both for "git absent" and "not a repository", so the two cases cannot be told apart in the output. SKILL.md says it; the section does not. Which is more costly: a one-line notice, or the silent figure? The PI has to decide.
refs: __reports__/reflective_run/w02/reproducer-w02-1/spend_main_nogit.txt, scripts/lab_status.py:436-443

## S-w02-reproducer-w02-1-4
Spend 60.93 for the open PI session grew about 0.55 USD in the few minutes of my run; the claim's 64.77 and my 65.32 differ only by that. The claim states the figure at run time, but the head's table prints a number a verifier can never reproduce. Is a reproducible check for an open session possible (a frozen copy of the transcript), or is this class of figure always unverifiable?
refs: __reports__/reflective_run/w02/reproducer-w02-1/spend_wt.txt, __pondus__/w02-c1.md lines 20-27

## S-w02-reproducer-w02-1-5
The author's added section landed after my verdict section and so sits under my `## verdict: reproducer-w02-1` heading; the research-loop format has no place for a post-exchange author addendum. Where should an author put an addendum so it is not read as part of a verifier's section?
refs: __pondus__/w02-c1.md lines 78-82
