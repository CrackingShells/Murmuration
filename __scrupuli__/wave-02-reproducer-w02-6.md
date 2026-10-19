## S-w02-reproducer-w02-6-1
Every one of the five time cells had its first SubagentHandback refused by the report check (a `deny` line), so "handed back in 5 of 5" really means "handed back on the second try". In m1 to m3 the worker handed back at the note, before the notice; the notice then fell on the report write, so it tested nothing. Nothing here shows what the hand-back notice does to a worker that is not already handing back, apart from m4 and m5 (n = 2, and each of those was also refused once). Is the notice or the report check what costs the worker its first hand-back?
refs: runs/m1..m5/lab/__statera__/harness.jsonl (events start/note/deny/stop/end); my chk.py output

## S-w02-reproducer-w02-6-2
The repeated notices after a refused hand-back: m4 got 2 and m5 got 3 `decision: block` notices because each deny made the worker call a tool again. The halt backstop needs 3 earlier notices and 1.5 T, so a worker that is refused by the report check and then writes its report can accumulate notices toward a halt that loses the hand-back. In m5 the third notice came at 1.24 T. Is the report check plus the time budget a path to the `continue: false` the design says loses the hand-back?
refs: runs/m5/lab/__statera__/harness.jsonl (three `stop` lines, 62.4, 68.9, 74.4 s)

## S-w02-reproducer-w02-6-3
Arm B's long calls (236 to 596 s) were 25 Bash calls in a background worker with no `timeout` in the command, and three ended within 3.2 percent of 600 s. A hook cannot interrupt them; the head says "give long computations their own limit in the command". Who tells an explorer that, and was the 600 s ceiling the reason or a coincidence? Not checked (the author marks it CONJECTURE).
refs: expC/B explorer-w02-a transcript aa1c72b39e7eedcd2, calls at 676, 1260, 1855 s

## S-w02-reproducer-w02-6-4
The T default at SubagentStart is always logged as the default (`from_brief` false, because the brief is not readable yet); only later lines carry the brief's T. The start note told every worker "20 minutes ... unless your brief has a line" even where the brief had `Time: min 1`, so each m-cell worker was told 20 minutes at start and 1 minute at the note. The run still behaved; but the two texts conflict for the worker and no cell measures whether the start text hurts obedience.
refs: runs/m4/lab/__statera__/harness.jsonl line 1 (T 20.0, t_from_brief false); transcript record 15

## S-w02-reproducer-w02-6-5
Part 1's explorer span (2956 s) has the model at about 240 s and tools at 2719 s; the hook counts wall time, so a long model turn counts too. On the m cells the model took about 3 to 4 s a call. For a worker doing real reasoning the same budget ticks differently; the wall-clock defaults (20/15 min) are one run's worth of evidence from a different mix.
refs: expC/B explorer-w02-a transcript; chk.py output
