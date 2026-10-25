## S-w09-explorer-w09-e-1
Every arm answered every question, B1 included. A ceiling this clean means the questions measure the summarizer's recall of lab state, which Opus does well at 220k, not what a digest adds. I wrote the questions and the digest together, so I cannot say the 8 of 8 would survive a question I did not anticipate; the two detail questions (numbers in hand-backs) are the only ones the summaries lost, and every arm fetched them. What question would make B1 fail at this size?
refs: `__reports__/wave-09/explorer-w09-e/runs_scored.tsv`, `__reports__/wave-09/explorer-w09-e/summary_flags.tsv`, `/private/tmp/murmuration-w09/explorer-w09-e/main/questions3.txt`

## S-w09-explorer-w09-e-2
On resume the platform injects a `task_notification` for each unfinished background agent ("didn't finish before the previous session ended", with the agent's description). In a replay it hands the PI the in-flight workers by name in every arm, which makes my Q1 useless as a test of the digest, and it makes each PI say "nothing is running now". In a live compaction no such notice exists. I do not know whether the notice comes before or after the compaction in the context order; the answers do not say.
refs: `/private/tmp/murmuration-w09/explorer-w09-e/main/runs/OP_B1_2/stream.jsonl` (records with `subtype: task_notification`)

## S-w09-explorer-w09-e-3
The compaction request of a resumed session paid input price for 168,357 tokens and read only 20,706 from cache (the system prompt and tools): USD 0.76-0.81 against explorer-w08-e's 0.126-0.157 for a live compaction. So any cost from a resume-based replay overstates a live compaction by about five times, and wave 8's "USD 0.44 per compaction" in w08-c3 came from live-like cells. Is there a way to warm the cache of a resumed session before the compaction without paying a full request, or is the cold-cache cost simply part of what a `--resume` costs?
refs: `/private/tmp/murmuration-w09/explorer-w09-e/main/runs/*/debug.log` (line "Forked agent [reactive-compact] finished ... totalUsage: input=168357 ... cacheRead=20706")

## S-w09-explorer-w09-e-4
HP_3's cell cost USD 1.703 as the run reports it, but my sum of its requests is 1.283; the other five cells differ by 0.03-0.05. Its second request wrote 94.9k tokens to the cache (the others about 47k) and the result's input tokens are 201k against 168k. I assumed a cache miss from launching two runs at once, but I did not see which request missed. If it is the platform's, a replicate protocol should not launch cells in parallel on one prefix.
refs: `__reports__/wave-09/explorer-w09-e/runs_scored.tsv` rows OP_HP_3 and OP_HP_2; `/private/tmp/murmuration-w09/explorer-w09-e/main/runs/OP_HP_3/stream.jsonl` (result line `modelUsage`)

## S-w09-explorer-w09-e-5
The haiku pilot with the PreCompact digest copied "the user's words, verbatim" into the summary with the last clause of one sentence missing ("by using it yourself."), while asked to keep them word for word; the Opus summaries kept the quote exactly (H cell). The digest asks the summarizer to copy, and a copy is not a guarantee. The post-compaction channel (HP) delivers the text byte for byte and in this pilot left no trace of the failure. Which of the two should carry the sentence a PI must quote?
refs: `/private/tmp/murmuration-w09/explorer-w09-e/pilot/runs/P1/` (session file of the run: `~/.claude/projects/-private-tmp-murmuration-w09-explorer-w09-e-lab/b5f55d4f-0002-4bb5-8f05-8be1cd79d204.jsonl`, the `isCompactSummary` record); `__reports__/wave-09/explorer-w09-e/summary_flags.tsv` for Opus
