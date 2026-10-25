## S-w09-author-w09-1-1
A resumed PI session is a second transcript with the old history inside it: 70daedf1 holds 226 of ad75be4f's 229 request ids and a copy of its records (shared uuids). Every per-file count in the explorer's scripts (PI request 0, PI USD, hook records) can count that history twice; I checked it for M1 and found no duplicate hook uuids, but the harness-ends and start counts have the same shape at another level (records per resume, not per worker: 171 end records are 91 workers, 130 start records with names are 66 dispatches). Should every lab script state its unit (file, record, request, worker) in its first line?
refs: `__reports__/wave-09/author-w09-1/tokens.md` (M1 block), `harness.md` (M5, M7), `__instrumenta__/w09f_harness_ends.py`, `w09f_name_audit.py`

## S-w09-author-w09-1-2
The explorer's hand-back lengths read the last `SubagentHandback` call of a worker; 57 of 137 workers called it two or more times (each answered "Report delivered to your caller"), and the PI reads each delivery. The claim w08-c6 speaks of first hand-backs. The first and last differ by 700 characters at the median, and by a factor of three for authors (5,548 vs 1,645). Which unit is the PI's context cost: the first, the last, or the sum of the deliveries? I did not compute the sum.
refs: `__reports__/wave-09/author-w09-1/tokens.md` (M6 block)

## S-w09-author-w09-1-3
The lean start (w06-c9) is claimed at 20-22 ms a start and landed against its threshold by PI decision; the recorded PostToolBatch median does not move (105 to 103 ms, interval [-28, 38]), and the SubagentStart interval [-35, 360] contains 0. The exec form (w07-c3) shows (52-54 ms). Nothing in the records can say whether the lean start ever saved anything, since only stdout-writing runs leave a duration.
refs: `__reports__/wave-09/author-w09-1/hooks_cache.md` (M3 block)

## S-w09-author-w09-1-4
"No worker ended over budget" (budget hook) depends on which budget: 28 of 91 workers were raised at least once, and one (author-w07-5) ended at 1.10 of its pre-raise budget. The block at 1.5x has never fired, and 0.36 median use can mean generous budgets or working notes; the records cannot separate them. The harness records the budget at the end, not the one first set, so a "frac" computed from `end` alone is relative to a moving denominator.
refs: `__reports__/wave-09/author-w09-1/harness.md` (M5 block), `__statera__/harness.jsonl` `raise` and `end` records of any sibling worktree

## S-w09-author-w09-1-5
The name-binding fix has almost no after-sample: 5 dispatches before the freeze, 2 of them in a batch. The explorer's "0 of 15 after" is not reproducible by my reading of the harness files (inline computation, never saved: S-w09-explorer-w09-f-3). The only evidence of the fix at work is this wave's one `name_unconfirmed` start, bound a second later.
refs: `__reports__/wave-09/author-w09-1/harness.md` (M7 block)

## S-w09-author-w09-1-6
The explorer's report states the lab_status labels were read "at 2026-10-25 14:30 JST"; the clock was 14:30 UTC (23:30 JST), and the transcript timestamps it cites are UTC. A one-word slip, but the same sentence says the before/after tables are UTC, so a reader mixing them is off by nine hours.
refs: `__reports__/wave-09/explorer-w09-f/00-findings_v0.md` line 12; `date -u` at 14:40 UTC on 2026-10-25 against the commit time 23:39 +0900

## S-w09-author-w09-1-7
M2's before-group is one session and the after-group starts the next day; the drop of 40.5% matches the claimed 42-45% well, perhaps too well for an observational pair: the merge carried waves 1-3 together, and the agent files on the study branch differed in more than the `Skill` tool. Whether the claim's own experiment or the transcripts is the stronger evidence of the `Skill` effect is not settled by this pair; only that nothing contradicts it.
refs: `__reports__/wave-09/author-w09-1/tokens.md` (M2 block)

## S-w09-author-w09-1-8
Rows 21 and 22 of the explorer's table sit in the "measurable on records" list while their own last-cell text says the risk avoided is N; the 33-row tally adds up, but the R and N sizes (7 and 13) depend on how a mixed cell is read (5-6 and 13-14).
refs: `__reports__/wave-09/author-w09-1/tally.md`

## S-w09-author-w09-1-9
Resumed after w09-c1 was ruled OVERSTATED: the head said "ceiling" for a figure that leaves out the cache write, and "pairs" for a rate and for three eras. I wrote both words without checking them against the unit of the number. The same failure as S-w09-author-w09-1-1, in the wording instead of the count. A one-line check at filing time (name the unit and the direction of each bias next to every USD figure) would have caught it.
refs: `__pondus__/w09-c1.md` head, `__pondus__/w09-c3.md`
