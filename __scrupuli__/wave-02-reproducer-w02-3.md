## S-w02-reproducer-w02-3-1
In the quick run's h1 the stop notice (1.32 B) arrived after the worker had already called SubagentHandback for the second time; in the 5 cells with the note on, the stop is always the last-but-one request. The "0 reads after the stop" figure is therefore only informative in the 4 stop-alone cells. Is the stop notice worth anything when the note is on, or does the deny-and-write-report round trip alone push the spend past 1.0 B every time?
refs: __reports__/reflective_run/w02/author-w02-3/summary.tsv (requests minus stop_at_request); runs/h1 transcript, records 100 to 109 of the worker agent file

## S-w02-reproducer-w02-3-2
Every worker sees the platform `budget_usd` attachment (used from the whole process, total 0.7) next to a start note saying B = 0.06. The tracker's `used` at the first read was 0.0288, including the haiku parent, so a worker comparing it to B would stop at once; it did not. Why do sonnet workers ignore the tracker against a 0.06 line but obey a 0.8 B hook note? A cell with start note and tracker and no later notices would answer it.
refs: runs/h1 worker transcript records 21 to 103 (budget_usd attachments); w02-c3 Limits, first-set controls that stopped at 13 and 9 files

## S-w02-reproducer-w02-3-3
The recorded output count in an auto-mode worker transcript is 63 to 83 percent of exact spend, and the hook estimates the rest with content length / 1.3 calibrated on 7 pilot runs. The estimate also stands in for hidden thinking tokens, which the transcripts of these runs hold in small amounts (143 thinking tokens in h1). A thinking-heavy explorer at B = 3.0 would be under-counted; which test would show it?
refs: runs/h1/stdout.jsonl modelUsage (thinkingTokens 143); scripts/budget.py lines 73 to 78

## S-w02-reproducer-w02-3-4
Running `run_all.sh ... quick` overwrote the tracked `summary.tsv` with a 2-cell table. A verifier who does not look at git status would leave the evidence file of the claim replaced. The same pattern may hold for other authors' quick commands.
refs: __reports__/reflective_run/w02/author-w02-3/run_all.sh (last line)

## S-w02-reproducer-w02-3-5
The head says the three shipped files are "uncommitted over HEAD fb80f93", but they are committed in fbbbcc3 with the same hashes. Which commit do the cells of the claim belong to, and does the claim's "evidence: ...@" form need the final hash?
refs: git log -1; sha256 of scripts/budget.py (c552e8dcaaac)

## S-w02-reproducer-w02-3-6
The `start` log line names the agent `murmuration-explorer-a308bb41` (the fallback name) because the transcript does not yet hold the brief; later lines carry the real name. A reader sorting the log by name sees two agents per run. Harmless to the claim, odd for the human reviewing harness.jsonl.
refs: runs/h1/lab/__statera__/harness.jsonl line 1
