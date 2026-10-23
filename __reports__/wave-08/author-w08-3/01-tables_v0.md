# w08-c3 tables: a PI-like session through a compaction, the PreCompact hook, the setting's location, workers

Protocol: `__reports__/wave-08/02-protocol_p3_compaction_v0.md` (b89e6c5). Branch `w08-c3-compaction` of the plugin: hook `scripts/precompact_state.py` + its row in `hooks/hooks.json` at 9ac1855 (row at d1af3a4). Claude Code 2.1.304, models `opus` (the research-pi agent's own) and `haiku`, window 150,000 (compaction fires near 117,000 tokens), default permission mode, no budget flag. All runs are under `/private/tmp/murmuration-w08/author-w08-3/` (transcripts stay there; nothing from them is committed, only counts and booleans).

## 1 deviations from the protocol (all after the pilot `pilot_h`, which is not counted)

1. The pilot asked for "my latest words to you, quoted exactly" and the model quoted my previous driver turn. Q2 became "the instruction I gave you at the start of this session, quoted exactly", and the planted sentence is now in the first message as well as in the last entry of `user_words.md`. Rule 1 below is therefore scored on the question as asked in the counted runs.
2. The first subagent cell ended after one file (haiku took "say only ok" as the whole task, explorer-w08-e's flake); its instruction became "one short sentence after each", and the cells below are the second attempt.
3. Haiku arm H has 4 runs: seeds 1-3 with the window in the environment and one (seed 1) with `autoCompactWindow` in a `--settings` file (run `hk_Hset_1`). Opus B1 (one run) is the extra the protocol allowed.
4. The scorer's Q1 strict rule is as registered (no ended worker named in the answer to Q1); the lenient version (names with their claim ids, ended workers allowed) is reported next to it.

## 2 arms (m1, m2, m3, m5), `runs_scored.tsv`, `arms_table.md`

| model | arm | runs | Q1 strict | Q1 lenient | Q2 | Q3 | Q4 | Q5 | re-read calls (mean) | re-read tokens per run | summary holds sentence / names / next / labels / q5 | compaction request USD | context before -> after | next request writes | total USD at Opus list (mean) | context at the end |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|:--|:--|--:|:--|--:|--:|--:|
| opus | C | 1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0.0 | 0 | - | - | - | - | 1.76 | 156,880 |
| opus | B1 | 1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 4.0 | 2,934 | 1/1/1/0/1 | 0.100 | 120,519 -> 25,333 | 41,153 | 1.83 | 77,846 |
| opus | H | 2 | 2/2 | 2/2 | **1/2** | 2/2 | 2/2 | 2/2 | 5.5 | 2,490; 1,590 | 1/1/1/1/1; 1/1/1/0/1 | 0.104 | 119,086 -> 25,553 | 41,794 | 1.89 | 77,381 |
| haiku | C | 3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0.0 | 0; 0; 0 | - | - | - | - | 1.56 | 152,335 |
| haiku | B0 | 3 | 2/3 | 3/3 | 2/3 | 3/3 | 3/3 | 3/3 | 6.3 | 18,879; 13,645; 2,461 | 1/0/0/0/0; 1/1/1/0/1; 1/1/1/0/1 | 0.132 | 120,707 -> 25,208 | 40,864 | 1.93 | 86,731 |
| haiku | B1 | 3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 5.7 | 3,423; 2,992; 13,998 | 1/1/1/0/1; 1/1/1/0/1; 1/1/1/0/0 | 0.133 | 120,974 -> 25,643 | 41,721 | 1.87 | 80,852 |
| haiku | H | 4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4.5 | 14,144; 2,992; 4,229; 2,201 | 1/1/1/0/1; 1/1/1/1/1; 1/1/1/1/1; 1/1/1/0/1 | 0.162 | 120,741 -> 26,114 | 42,393 | 1.91 | 81,130 |

Arms: C no compaction (9 reports read, default window); B0 window only (no brief, no hook); B1 window + the lab's `resume_brief.py` row; H window + brief + `precompact_state.py`. Seeds 1-3 are lab variants (names, numbers, sentence). Per-run rows: `runs_scored.tsv`. "Total USD at Opus list" re-prices every request of the run (haiku tokens at Opus prices) and adds the compaction request.

Reading of the table, by script and by eye on the booleans:

- Opus H run 1 (`op_H1`) failed Q2: it answered that it could not quote the instruction exactly, "the only copy I can reach is my summary", although its summary did hold the sentence (`s_sentence` = 1) and `user_words.md` held it; it made 10 re-read calls (2,490 tokens) and did not read `user_words.md`. Opus H run 2 read `user_words.md` (1 call, 1,590 tokens) and answered exactly. Opus B1 and C answered all five.
- Haiku B0 run 1 (`hk_B0_1`): summary without the in-flight names and next step (0/0), Q1 strict and Q2 failed, 13 re-read calls (18,879 tokens, one of them the session's own transcript file).
- The hook changes what the summary holds, not the outcome: labels of the wave's claims were in 3 of 6 H summaries and in 0 of 4 B1 and 0 of 3 B0 summaries; Q4 was answered correctly in every run, because the claim files are small and the PI re-reads them.
- Paired by seed, haiku H against B1: items correct equal (5 of 5 in all three seeds); re-read tokens seed 1 14,144 against 3,423, seed 2 2,992 against 2,992, seed 3 4,229 against 13,998.
- The compaction request (m3), Opus: 0.100-0.106 USD (2,564 uncached input, 108-115k cache read, 3.4-3.5k output, 30-35 s); context 115.8-122.4k -> 25.2-25.9k; the next request writes 41.0-42.5k tokens; the whole event costs about 0.44 USD (request 0.10 + post-compaction write 41.8k x 8 per million = 0.33).
- Spend (m5), measured on the 20-request session: compacted runs cost more than the control (Opus H 1.89 and B1 1.83 against C 1.76; haiku-priced-as-Opus arms +0.3 to +0.4 against C 1.56), because the sessions end 8-12 requests after the compaction: each later request is cheaper by (156,880 - 77,381) x 0.20 per million = USD 0.016, so the compaction pays back after about 28 requests at this size.

## 3 the registered rules, applied

| rule | result | outcome |
|:--|:--|:--|
| 1 state survives (Opus H x2 and C all four of Q1..Q4; haiku H at least 2 of 3 seeds all four and never more than one item under C) | Opus H run 1 failed Q2 (strict), run 2 and C all correct; haiku H 4 of 4 runs all correct | **not met on Opus** (one of two runs), met on haiku |
| 2 the hook adds something (H above B1 in an item in at least one seed and below in none; or equal with fewer re-read tokens in 2 of 3 seeds) | items equal in all seeds; fewer re-read tokens in 1 of 3 seeds | **not met** |
| 3 re-reads bounded (Opus H at most 30,000 tokens) | 2,490 and 1,590 tokens (scratch files are small: see Not covered) | met |
| 4 cheap (hook median under 500 ms, exit 0) | hook time in the six H compactions: 62.1, 70.1, 84.4, 92.5, 142.9, 157.7 ms (median 88 ms, from the debug log); ten cold runs on the real lab: median 142 ms (87-667 ms); exit status 0 in every one | met |
| 5 net (ESTIMATE at measured R at least USD 25) | USD 43.8-44.7 at R = 2,500 tokens (Opus summary 3,400 tokens: 44.65), 43.0 at R = 10,000, 39.5 at R = 20,000, 32.3 at R = 45,000, of 144.47 (22-31%) | met |
| 6 setting | `autoCompactWindow` in a `--settings` file compacted a session end to end at 119,395 tokens (`thresholdSource=settings`, run `hk_Hset_1`); project `.claude/settings.local.json` not run (section 4) | partly |

By the protocol's own wording: rules 1 and 2 fail for the hook, so the hook is not landed on this evidence, and the setting is judged on rule 1 with B1: Opus B1 4 of 4 correct and haiku B1 3 of 3 all correct, so the setting with the existing brief passes rules 1, 3, 4, 5. n is 1 for Opus B1 and C; a sign, not a test.

## 4 where the setting must live, and whether a running session sees it (m6), `m6_settings_location.txt`

- MEASURED (debug log, 2.1.304): with `--project-config-root <main checkout>` and the shell in the lab's worktree, the files loaded are `~/.claude/settings.json` and the main checkout's `.claude/settings.json` and `.claude/settings.local.json`; the worktree's own `.claude/` files are not. Without the flag, a session in the worktree loads the worktree's two files and the main checkout's `settings.local.json`. The Desktop passes the flag (`__statera__/synthesis.md` row 1(d), explorer-w05-e), so for the Desktop PI the key must be in the main checkout's `.claude/settings.local.json` (or the user's `~/.claude/settings.json`); a copy in the worktree does nothing there.
- NOT TESTED: that `autoCompactWindow` written in a project `.claude/settings.local.json` is honoured. The lab's permission guard (G3) refused my writes of such a file even inside a scratch folder, and I did not work around it (the brief allowed the scratch settings file; the guard is the user's layer). What I ran instead: the same key in a `--settings` file, end to end (compaction at 119,395 tokens, `thresholdSource=settings`). The Desktop entrypoint was not run.
- MEASURED: a `--settings` file changed between two turns of one process was not re-read (`effectiveWindow` 980,000 at both turns, the second after the file said 150,000). The project and user settings files are on the watch list in the debug log ("Watching for changes in setting files ..."); whether a change of those reaches a running session was not tested (it needs a write to a settings file). Idle compaction and Desktop behaviour: not run.

## 5 workers (m7), `worker_ceilings.txt`, `subagent_cell_*.json`

- MEASURED over the lab's own subagent transcripts (waves 1-8 so far, 331 workers, 7,023 requests; 132 sonnet, 199 haiku): median worker context 33,760 tokens, p90 206,088, max 438,307. Above 150k: 20.2% of workers, 32.4% of requests; above 250k: 6.6% of workers (22), 12.7% of requests; above 400k: 3 workers, 0.95% of requests. All of the 22 are sonnet workers (16.7% of the 132); one haiku worker passes 150k.
- ESTIMATE (explorer-w08-e's cost model per worker at its own price, one compaction per worker, post-compaction context 77,000): net USD -0.64 at 150k, +9.31 at 250k, +1.21 at 400k, on worker context reads of about USD 91. Workers at 250k are worth compacting; at 150k they are not.
- MEASURED (subagent cell, haiku, window 120,000, `subagent_cell_compacted.json`): a subagent read eight reports and was compacted twice (two PreCompact events, two forked compactions) and still answered its name, claim id, verifier name and the first report's largest gap correctly (4 of 4), as did the uncompacted control. The PreCompact payload of the subagent has no `agent_id` or `agent_type` and its `transcript_path` is the main session's, so the hook cannot tell it runs for a subagent; the platform ignores a PreCompact hook's stdout in a subagent (CITED explorer-w08-e). The hook ran in 56-66 ms there. `resume_brief.py` also fires in a compacted subagent (explorer-w08-e, MEASURED): in the real lab it hands each compacted worker the whole wave note (about 16,000 characters).
- Rule applied (registered): above the threshold in more than 10% of worker requests (12.7% at 250k) -> the PI's threshold applies to workers; the setting is global, so no extra setting. No block: the one compacted-subagent cell lost nothing, and blocking a proactive compaction would only send the worker back to the 967k default.

## 6 net over the six PI sessions (m5), ESTIMATE

`python3 -I` with `__instrumenta__/w08e_compaction_net.py` run through `run(T, "new", OUT, R)`, threshold 250k, 13-17 compactions, summary output 3,000 tokens (the Opus summaries were 3,371-3,500 output tokens; 3,000 is the value the run used) or 6,000 (haiku's, explorer-w08-e's): R = 0: 45.56 / 44.78; 2,500: 44.65 / 43.81; 10,000: 42.99 / 42.15; 20,000: 39.52 / 38.62; 45,000: 32.29 / 31.27 (USD, OUT 3,000 / 6,000), of 144.47. The scratch lab's floor after compaction (25.3k) is not the real PI's (91.5k): the model uses 91.5k.

## Not covered

Real PI sessions at 250k with the Desktop (the window here is 150k and the lab small: wave note 3,000 characters, claim files of 600-700, six-line harness log; in the real lab the brief alone is 16,000 characters and the harness log is longer, so R there is more than the 1,600-2,900 tokens measured here); Opus n = 2, 1, 1; the summarizer at 250k; a PI that works for hours after the compaction; the project-settings route and the Desktop route; the hook against a real parallel dispatch (the real `harness.jsonl` names a worker wrongly at `start` when three agents start in the same instant: the hook takes the name of the latest event of an agent_id, which fixes it only when a later event exists); prose detail: Q5 (the first report's largest gap) was answered correctly in all 17 runs, from the summary in 11 of the 13 compacted runs (in `hk_B0_1` and `hk_B1_3` it was re-read), so this scenario does not show the loss of prose detail that explorer-w08-e measured (0 of 10); the gap line was the number the PI had been asked to look at in turn 2.
