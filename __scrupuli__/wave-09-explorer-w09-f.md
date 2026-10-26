## S-w09-explorer-w09-f-1
The PI's `disallowedTools` line (w05-c7) cut request 0 by 34.1% (74,685 to 49,230 tokens, n = 3 against 5, the same platform version on both sides), but its USD ceiling on the records is 4.0-6.4% of a PI session, and the synthesis states 7.5-12% of a wave-4 PI (ESTIMATE). The wave-4 PI itself gives 6.1%. Either the estimate used a different base (cache-read share of PI spend, 56%, times the token share) or it is high by 0.5-0.8. I did not find which; the two numbers carry the same label and sit in the same synthesis.
refs: __reports__/wave-09/explorer-w09-f/before_after.md (M1); __statera__/synthesis.md (wave 5, "The PI's tool schemas")

## S-w09-explorer-w09-f-2
The 1-hour cache for authors (w07-c7) has three money figures (+0.87, -0.02 +- 0.39, and +0.54 on 7 authors here) and none can be tested by a before/after, because the pause rate per author itself fell from 1.6 to 0.82 after the waiting paragraph (w05-c1). The setting and the behaviour it is meant to protect against are changed by two different landed changes in the same week. I would look at whether any author after the merge was resumed more than 5 minutes after a hand-back (the case the claim rests on): the 6 pauses I count are all inside a run, none is a resume wait.
refs: __reports__/wave-09/explorer-w09-f/author_cache.md (M4); __instrumenta__/w09f_author_cache.py

## S-w09-explorer-w09-f-3
41 of 306 subagent transcripts of the lab end on a tool call that is not `SubagentHandback` (30 Bash, 4 Write, 2 SendMessage, 1 Read, 1 Skill, 3 with no tool call). w02-c5 says 15 of 15 hand-backs were saved, and the budget design says "a lost deliverable is the failure to avoid"; nobody classified these 41 as killed, resumed or lost. The harness `end` records (171) show no worker over 1.0 B and none blocked, so they were not stopped by the budget hook.
refs: __reports__/wave-09/explorer-w09-f/threads.tsv (columns handback_chars = 0 on sub rows); the last-tool-call count came from an inline Python pass over `~/.claude/projects/*Murmuration-murmuration-*/*/subagents/agent-*.jsonl` (not saved as a script)

## S-w09-explorer-w09-f-4
The platform's recorded duration of the budget hook, lean start (w06-c9) against the string form: PostToolBatch median 105 to 103 ms (n = 44, 30), SubagentStart 467 to 247 ms (n = 47, 20). The claim is 20-22 ms a start. A hook that writes stdout is the slow path, and a silent run leaves no record, so the table cannot say which of the two numbers is the saving a worker sees. The exec form's step (103 to 51 ms) is cleaner than the claim it was registered against, and the lean start's step is not visible at all at the median.
refs: __reports__/wave-09/explorer-w09-f/hook_dur.md (M3); __instrumenta__/w09f_hook_dur.py
