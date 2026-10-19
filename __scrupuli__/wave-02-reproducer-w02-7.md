## S-w02-reproducer-w02-7-1
Why did arm B survive a 2,952 s idle gap with a worker active, with no variable set, when arm A was stopped at 603 s? The findings guess a PI background shell task (B had 4, A had 0), but nobody tested it. The platform's message says "after the last turn", so one possibility is that B's PI turn did not count as the last turn. A cheap test would be a small headless run with a deliberately long worker, with and without a PI background shell task.
refs: __reports__/reflective_run/w02/explorer-w02-c/01-findings_v0.md (Ceiling table, open questions); scratchpad w02/expC/B/stderr.txt

## S-w02-reproducer-w02-7-2
The "14 worker runs" in A's M2 cannot be matched to the 13 subagent files I listed (the findings give 12 files and 14 runs, since SendMessage resumes count as extra runs). I did not re-derive it, and the claim does not depend on it.
refs: scratchpad w02/expC/A transcripts; 01-findings_v0.md M7

## S-w02-reproducer-w02-7-3
Explorer-w02-a's tool result reads "The user doesn't want to proceed with this tool use", the permission-rejection text, when the platform kills a background task. The cause is the ceiling, not a user. A reader of the transcript alone would think a human interrupted it.
refs: agent-a209ed43358aee992.jsonl last two records
