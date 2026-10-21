## symbols
No new symbol.

## S-w07-author-w07-6-1
A3 (agent file A, 5-minute cache) read 5,202 tokens from cache at request 2 after a 422 s gap, although a 5-minute entry written 422 s earlier should have expired. The likely source is B3's 1-hour write of the same system and tools prefix, which ran at the same time; so the two arms were not independent of each other, and a cache entry written at one TTL is read by a request that asks for the other (B1 of the quick run read 5,202 tokens that A1 wrote at 5 minutes). I did not test this: a clean test runs A3 alone, then B3 alone, in a cold hour. The verdict on c2 does not depend on it (A3 still re-wrote 7,719 tokens, read fraction 0.408), but the size of A's re-write does.
refs: `__reports__/wave-07/author-w07-6/tables_c1_c3.md` rows A3 req 0 and 2, B3 req 0; `/private/tmp/murmuration-w07/author-w07-6/quick/runs` B1 req 0

## S-w07-author-w07-6-2
The CLI's `total_cost_usd` is 3-7% above the cost I recompute from every deduplicated request in the main and author transcripts at list price (ratio 0.928-0.973 in all six sessions; 0.939-0.959 in the quick pair). Candidates: requests that are billed but not in a transcript (title, summary, classifier calls on a smaller model), or the thinking tokens. The ratio is stable enough to support the 1-hour rate (it falls to 0.68-0.75 if 1-hour tokens were billed at the 5-minute rate), but I cannot say what the remainder is.
refs: `__reports__/wave-07/author-w07-6/prices_check.md`

## S-w07-author-w07-6-3
The break-even depends on one ratio, tokens re-written after 300-3600 s over all write tokens, and the wave records sit at 0.414 against a threshold of 0.385. The six wave-7 authors have none of these re-writes, and eight authors of waves 4-6 have 14 (author-w06-5 has two, 0.70M tokens); I cannot say from the transcripts which author behaviours (verifier exchanges, long Bash waits, resumes) produce them, nor whether the wave-7 authors' zero is a change of behaviour (the 4.5-minute waiting rule in the agent file; I did not check when it was added) or chance. If the rule works, the gap bin that 1h saves is shrinking, which makes the net smaller than the replay says.
refs: `__reports__/wave-07/author-w07-6/c4_break_even.md`

## S-w07-author-w07-6-4
Two re-writes in the author records have a gap of 300 s or less (author-w04-1, author-w04-4; 0.43M tokens) and one above 3600 s (author-w06-3, 0.23M tokens), by the w07g rule; w07g counted them as TTL drops. A cache write after under five minutes is not a TTL miss: something else changed the prefix (a tool loaded by ToolSearch, a compaction, a resume that rebuilt the context). The rule `cache_read < 0.5 x previous context` cannot tell these apart, and the c4 gap bins depend on my definition of elapsed time (previous model time + tool time + gap).
refs: `__reports__/wave-07/author-w07-6/c4_break_even.md` rows w4 author-w04-1, author-w04-4, w6 author-w06-3

## S-w07-author-w07-6-5
The headless author sessions list the tools `Read, Bash, Write, Edit, ToolSearch, SubagentHandback` (the prefix record), although `agents/author.md` lists Glob, Grep and SendMessage too. The same in A and B, so c3 is unaffected. Grep is denied for the session by a hook and SendMessage is deferred, but Glob is missing and I did not find why; real authors in the waves do call SendMessage after ToolSearch.
refs: `/private/tmp/murmuration-w07/author-w07-6/work/A1/` transcript `subagents/agent-*.prefix.json` (field `state.toolNames`); `__reports__/wave-07/author-w07-6/tables_c1_c3.md` second table

## S-w07-author-w07-6-6
The first request of a B author at a cold start reads nothing (0 read, 11,948 written at 1 hour in B1) where A authors read 3,636 to 10,539 tokens that other sessions left. In the lab the system and tools prefix (about 5k tokens) is shared by every dispatched author, so a 1-hour author pays 4.0 on it for each cold start instead of 0.1 when an A entry is alive, and its 1-hour entry is then readable by A-type requests too. The size is small per start (about USD 0.02 at Sonnet prices for 5k tokens) but I did not put it into c4.
refs: `__reports__/wave-07/author-w07-6/tables_c1_c3.md` rows A1/B1/A2/B2 req 0
