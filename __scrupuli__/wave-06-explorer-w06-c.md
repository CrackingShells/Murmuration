## S-w06-explorer-w06-c-1
The "PI idle 75%" figure has no price on it: idle costs no tokens, only wake-ups do, and the wake-ups that changed nothing are 4.8% (wave 4) and 7.8% (wave 5) of PI spend. So the figure the user found interesting measures wall-clock, not waste. What would make idle time costly is a critical path that runs through the PI, and wave 4's does not (78.8 min of one author's headless cells). Is there any wave where the PI's idle time sat on the critical path, i.e. a worker waited for a PI decision beyond the 4-59 s measured in wave 4? Wave 5's PI-to-worker lags were not measured by me.
refs: __reports__/wave-06/explorer-w06-c/summary_tables.txt ("time split", "wake-ups"), __reports__/wave-05/explorer-w05-a/00-findings_v0.md (PI response lag)

## S-w06-explorer-w06-c-2
Wave 4's PI wrote all 101 puzzle dispositions, the dispatch and claims tables and the synthesis in the last 5 minutes, while workers had been handing back since the first 4 minutes. I priced it (about 1.5-3 min of the 1.8-min close are movable) but did not test that earlier dispositions survive later puzzles and verdicts, which is probably why a PI waits. How many dispositions in wave 4 or 5 changed between a first reading and the close? That decides whether "dispose as they land" is safe.
refs: __reports__/wave-06/explorer-w06-c/w4_turns.tsv (rows 23-24), PI transcript T4 01:50:07-01:54:30 UTC, __statera__/wave-04.md (Puzzle dispositions)

## S-w06-explorer-w06-c-3
The PI main thread writes every cache entry with the 1-hour lifetime (0 of 256 requests used 5 minutes); every Sonnet subagent writes the 5-minute lifetime (6.4M tokens, 0 at 1 hour). I found no setting that explains the split, and nothing in the plugin chooses it. In wave 4 the subagents' 11 misses after gaps over 300 s cost an estimated USD 4.37 (24% of their spend) and a blanket 1-hour write for them would cost 5.52, so it is a wash by measurement, but a per-call choice (1 hour only when a long wait is coming) might win. Who sets the lifetime, and is it per agent type, per interactivity, or per model?
refs: __reports__/wave-06/explorer-w06-c/w4_worker_cache.tsv, w5_worker_cache.tsv, w4_req.tsv (cache_write_5m column all 0)

## S-w06-explorer-w06-c-4
Wave-5 turn 24 (the wave-6 opening) cost USD 1.82 at 389k-417k context, and a fresh session would have cost the same within 0.3 USD at a 10k-token handoff, but only 3.25 at an 85k handoff, which is what wave 5's own preface actually read. So the real lever is not the session boundary but the size of what a PI reads to orient (turn 0 is 21-32% of PI spend). Which of the 85k tokens did wave 5's PI use later? I did not tag the preface reads against later use.
refs: __reports__/wave-06/explorer-w06-c/w5_turns.tsv (turn 0, 24), w4_turns.tsv (turn 0), __reports__/wave-05/explorer-w05-b/00-findings_v0.md (re-reads)
