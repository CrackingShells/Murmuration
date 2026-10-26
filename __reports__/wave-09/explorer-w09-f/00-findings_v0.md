---
type: findings
wave: wave-09
author: explorer-w09-f
date: 2026-10-25
version: v0
decision-required: none
---

# What landed on `main`, what was measured about it, and what its saving can be measured from (findings v0)

Stayed inside the brief. Labels as in the skill; claim labels are those of `python3 -I scripts/lab_status.py` at 2026-10-25 14:30 JST; the saving figures are quoted from `__statera__/synthesis.md` ("What landed", waves 5-8) and the claim heads in `__pondus__/`. Times in the before/after tables are UTC as the transcripts write them.

## Result

The user's reading is half right. Every one of the 33 landed changes below has a recorded **mechanism** result (a guard denies N of M forms, a hook returns the same output on N replays, a start costs X ms); by current label 29 rows read MEASURED (three of them with a restated or "below MEASURED: restate" claim among them: rows 4, 9, 26), 2 read CHECKED and 2 read CONJECTURE. **No landed change has a saving in USD, minutes or risk that was MEASURED as an achieved saving**: every USD or minute figure is an ESTIMATE (formula on recorded inputs) or a counterfactual. What the records allow, by my tally of the table: 9 changes got a measurement here on records that exist (tokens, ms, counts: rows 4, 7, 13, 16, 20, 23, 25, 28, 31; row 27 only thinly), 7 more could be measured on records and I did not (8, 10, 11, 14, 19, 21, 22), 3 only by a new paired run (3, 15, 26), and 13 are counterfactual by nature or name no saving (1, 2, 5, 6, 9, 12, 17, 18, 24, 29, 30, 32, 33). On USD the records give a ceiling only (tokens saved x later requests x list price). Worst fit of claimed saving to the records: **w07-c7 (authors' 1-hour cache)**, whose net moves from +USD 0.87 (ESTIMATE) to -0.02 +- 0.39 (ESTIMATE) to +0.54 over 7 authors here (ESTIMATE), each resting on a handful of pauses, while a before/after is impossible because the pause rate itself changed (1.6 to 0.8 per author). [source: tables below; `__reports__/wave-09/explorer-w09-f/`]

## Table

### A. Every change that landed on the local `main`, waves 1-8 (first-parent merges of `Murmuration` main)

Merges read: 84ff038 (waves 1-3), 4c675ec (wave 4), fed7a08 (wave 5), 33582f1 (wave 6), 3b0448b (wave 7), 1e0a81d, 16b05a8, dc74371, 3d5147a, 1511545, 92a853f (wave 8); merge-by-merge file lists from `git diff --stat <merge>^1 <merge>` on agents, skills, scripts, hooks, rust, bin. Wave-1 claims that landed inside w02-c1 and w02-c2 (w01-c2, c3, c8, c9) are not listed apart; w01-c14 is a framing rule, not plugin code.

Measurability codes: **R** = can be measured now from records that exist (transcripts, `harness.jsonl`, cost-state) on the same kind of work; **R-tokens** = the token or ms quantity can, the USD only as a ceiling; **P** = only by a new paired run; **N** = counterfactual by nature (a loss avoided, a risk) or no saving claimed.

| # | Change (landed at) | Claim · current label | Mechanism measured, at which label | Saving claimed, label | Measurable from records? |
|:--|:--|:--|:--|:--|:--|
| 1 | `/lab-status` spend in USD, each message once (84ff038) | w02-c1 · MEASURED | matches `cost-state` within 0.05% on 213 cells (MEASURED) | none in money; accuracy of every later cost figure | N (a correctness change); re-checkable any day against cost-state |
| 2 | prompt hook keeps typed text, v0 (84ff038) | w02-c2 · MEASURED (v0; replaced by #19) | 72 typed prompts kept, 0 dropped, 5 transcripts (MEASURED) | none (record quality) | N |
| 3 | hand-back saver, deny-once report request (84ff038) | w02-c5 · MEASURED | notes obeyed 7/7, 15/15 hand-backs saved byte for byte, report followed deny 13/13 (MEASURED, headless cells) | "workers spent 3.1 B without notices" (MEASURED in one cell set); no USD saving figure for the lab | P (paired run) for the spend effect; the loss it prevents is N |
| 4 | findings template, workers without `Skill`, `maxTurns` 150 (84ff038) | w02-c4 · below MEASURED: restate | worker start context 42-45% smaller at every role (MEASURED in the experiment) | tokens only (+444 words cost); no USD figure | **R-tokens: done here, M2** |
| 5 | `/lab-status` reads a verifier's latest verdict (84ff038) | w02-c9 · MEASURED | only w02-c4 changes state (MEASURED) | none | N |
| 6 | spend figures from harness log or `/lab-status`, never a worker (84ff038) | w02-c10 · MEASURED by PI decision | one worker read the session counter as its own (MEASURED, n = 1) | risk of a wrong figure quoted; "effect untested" | N |
| 7 | budget v2: graded notes on `PostToolBatch`, 1.5x block on `PostToolUse`, floor, raise (84ff038; hardened 33582f1) | w03-c1 · MEASURED | `PostToolBatch` fired 109/109; `PostToolUse` missed 13/172; a block on `PostToolBatch` ends the worker 4/4 (MEASURED) | stops overspend; in w04-c11 3 of 3 workers without notes ran on to 1.49-1.98 B, 2 of 3 with notes stopped (MEASURED, n = 3 per arm) | mechanism R (done here, M5: 0 of 171 workers ended over 1.0 B, 0 blocked); the saving is P (the no-notes arm) |
| 8 | helper scripts as files in `__instrumenta__/`, one scoped search, `.ignore` (84ff038) | w03-c2 · MEASURED (PI decided: restated) | saved under `__instrumenta__/` 3 of 3 vs 0 of 4 (MEASURED, n = 1 per arm) | none in money; reuse "not exercised" | R for where scripts land (count files by worker in transcripts); reuse is P |
| 9 | README: headless setting (84ff038) | w02-c7 · below MEASURED: restate (PI restated) | one of five runs lost its synthesis (MEASURED, n = 1) | avoids a lost synthesis | N |
| 10 | lab root from first cwd for words and resume brief (4c675ec) | w04-c1 · MEASURED | 3 of 3 prompts in the worktree vs 3 of 3 in main (MEASURED, headless); +1.5 / +5 ms | none (record placement) | R (`user_words.md` of main vs worktree) |
| 11 | explorer report line (4c675ec) | w04-c12 · MEASURED (w04-c8 · MEASURED, proposes B' not B'') | denies 1 of 3, template shape 2 of 3, n = 3 (MEASURED) | avoids a deny and a re-write; no USD | R (report shape and path of every explorer report on disk) |
| 12 | `/lab` index status, `briefs.md` script-file rule (4c675ec) | w04-c6 · MEASURED | two real bugs found and fixed (MEASURED) | none | N |
| 13 | waiting paragraph in the four worker files (fed7a08) | w05-c1 · MEASURED (PI decided: restated) | 0 cold mid-run requests vs 1, cost 0.57 of A at 227k tokens, n = 3 per arm + pair (MEASURED) | 0.43-0.47 of one author run's cost on one task | **R: done here, M4** (pauses and cold re-writes per author, three eras) |
| 14 | absolute colgrep path in worker files (fed7a08) | w05-c2 · CHECKED | searched the lab's folder in every case tried (CHECKED) | none claimed; a stale search of main avoided | R (the `paths` argument of every colgrep call in worker transcripts) |
| 15 | `/lab-status` one git call plus parse cache (fed7a08) | w05-c5 · MEASURED | 1082 to 344 ms on a frozen tree, output byte-identical (MEASURED) | about 0.7 s a call; no lab total | P (time one call before/after is only a new run; calls are not timed in transcripts) |
| 16 | `disallowedTools:` on the PI (fed7a08) | w05-c7 · MEASURED (headless), w06-c1 · MEASURED (Desktop) | request 0 minus 15,690 tokens 4/4 pairs; Desktop 74,966 to 46,738 (MEASURED) | 7.5-12% of a wave-4 PI (ESTIMATE) | **R-tokens: done here, M1** |
| 17 | commits by named paths (fed7a08) | w05-c8 · CHECKED | plain `git commit` took another agent's staged revert, named paths did not (CHECKED, one case) | risk of a wrong commit | N |
| 18 | reassessment entries in the wave procedure (fed7a08) | w05-c10 · CONJECTURE | six entries in wave 5, causation not shown | none shown | N |
| 19 | prompt hook: `async`, `prompt_id`, `origin.kind: human` (3b0448b) | w07-c5 · MEASURED | 0 errors over 3,027 prompts; live 10 of 10 (MEASURED) | none (record quality) | R (the three wrong entries it would drop are listed) |
| 20 | lean hook starts, `python3 -S -I`, run_hook.py (33582f1) | w06-c9 · MEASURED (landed against its threshold by PI decision) | same outputs 197 of 197; 20-22 ms less a start, 9 pairs (MEASURED) | about 32 s of 161 s a wave (ESTIMATE) | **R-ms: done here, M3** |
| 21 | fail-closed permission guard, Python (33582f1) | w06-c13 · MEASURED, w06-c14 · MEASURED | denies 63 of 4,637 real Bash calls, 26 strict false denials (MEASURED, replay); 65.2 vs 71.9 ms | risk (32 bypass-mode runs found by replay); the live record is 17 of 19 denials false in waves 6-8 (MEASURED, explorer-w08-j) | the live false-denial count R; the risk avoided is N |
| 22 | "Permissions" paragraph in four worker files, briefs, working defaults (33582f1) | no claim id (the user's decision of 19:27) | none run | risk (loosened permission layer) | N, but R for later violations: `claude` runs with bypass flags in Bash history |
| 23 | hooks in exec form (3b0448b) | w07-c3 · MEASURED | 215 of 215 starts, 10 of 10 live pairs; guard 123 to 42 ms, budget 104.5 to 41 ms (MEASURED) | CPU and energy per call; "60-70 ms should reach wall, could not be resolved" (CONJECTURE) | **R-ms: done here, M3** |
| 24 | `lab_status` prices fast mode and web searches (3b0448b) | w07-c4 · MEASURED | cache file carries a version, 0.955 vs 0.25 s (MEASURED) | none; "no figure changes today" | N |
| 25 | authors keep a 1-hour cache (3b0448b) | w07-c7 · MEASURED (PI decided) | 17 of 17 writes 1-hour; a 333 s gap read 100% vs 42% (MEASURED, n = 1) | net +USD 0.87 of 47.80 (ESTIMATE); later -0.02 +- 0.39 per life (ESTIMATE, explorer-w08-c) | **R-counterfactual: done here, M4** (an ESTIMATE, not a before/after) |
| 26 | Rust permission guard, Python fall-back (3b0448b) | w07-c6 · MEASURED, w07-c8 · below MEASURED: restate (PI landed on verifier wording) | 0 differences in 20,847 events; CPU 17.6 to 1.6 ms (MEASURED) | CPU and energy, wall only in default mode (MEASURED mechanism); no USD | P (a PreToolUse guard that hides behind the classifier leaves no duration in transcripts) |
| 27 | `budget` and `handback` as Rust subcommands (1e0a81d) | w08-c4 · MEASURED | byte-identical on 3,821 events; 9 of 12 start-time pairs met the registered 10 (MEASURED) | "seconds a wave" (ESTIMATE); price: USD 1.50 and 23 min vs 0.36 and 1.4 for the next change (MEASURED, author-w08-5) | R-ms for the one hook that writes output (M3: 24 ms, n = 1, too thin) |
| 28 | hand-back of at most about 1,500 characters, sections not whole files (16b05a8) | w08-c6 · MEASURED | first hand-backs 1,809-2,449 vs 3,328-5,873, n = 6 each, one session (MEASURED, an association) | PI context (hand-backs are 12% of PI context, MEASURED split); no USD figure in the claim | **R-tokens: done here, M6** |
| 29 | landing steps, times from `date` (16b05a8) | w08-c8 · CONJECTURE | would have caught two observed failures | none | N |
| 30 | PI decision sections in `/lab-status` (dc74371) | w08-c11 · MEASURED | 9 decided escalations read right; 68 other files unchanged (MEASURED) | none | N |
| 31 | start-note path, names bound only when unambiguous (3d5147a) | w08-c12 · MEASURED | 0 violations over every arrival order of 1-3, samples of 4 and 6; the old code fails 483 of 2,240 orders (MEASURED) | none in money; wrong budget on a wrong name | **R: done here, M7** |
| 32 | guard holes closed, Python and Rust (1511545) | w08-c13 · MEASURED | 0 of 2,259 hole forms and 0 of 639 write forms allowed, 1,515 and 359 before (MEASURED) | risk | N (the live record cannot show a hole closed, only a use) |
| 33 | `-c` option clusters for five shells (92a853f) | w08-c15 · MEASURED | 0 of 20,282 variants allowed vs 8,098 (MEASURED) | risk | N |

Tally by the last column (33 rows): measured here 9 (4, 7, 13, 16, 20, 23, 25, 28, 31), thin 1 (27), measurable on records but not computed 7 (8, 10, 11, 14, 19, 21, 22), new paired run only 3 (3, 15, 26), counterfactual or no saving named 13 (1, 2, 5, 6, 9, 12, 17, 18, 24, 29, 30, 32, 33). [my own tally of the table above, not a pipeline output]

### B. The before/after measurements I ran on existing records

All from `__reports__/wave-09/explorer-w09-f/threads.tsv` (564 transcripts: every main thread and subagent of the lab's seven worktrees plus the main checkout, made by `python3 -I __instrumenta__/w09f_threads.py`) and the harness files; the full printed output is `__reports__/wave-09/explorer-w09-f/before_after.md`.

**M1. PI request 0 before and after `disallowedTools` (w05-c7, merged fed7a08 2026-10-21T08:08Z). MEASURED (tokens); ESTIMATE (USD).**

| session (PI main thread) | start (UTC) | version | requests | request-0 tokens | PI USD at list | |
|:--|:--|:--|--:|--:|--:|:--|
| ab96c5ed (study) | 10-19 01:56 | 2.1.299 | 394 | 74,457 | 63.23 | before |
| c533f1c6 (wave 4) | 10-20 00:27 | 2.1.299 | 114 | 74,632 | 10.50 | before |
| 6b0e1f2a (wave 5) | 10-21 05:29 | 2.1.304 | 153 | 74,966 | 18.08 | before |
| 74fa512e (wave 6) | 10-21 08:18 | 2.1.304 | 233 | 46,738 | 23.08 | after |
| f023f552 (wave 7) | 10-21 15:22 | 2.1.304 | 201 | 47,867 | 27.14 | after |
| ad75be4f (wave 8) | 10-23 15:11 | 2.1.308 | 229 | 50,223 | 26.02 | after |
| 70daedf1 (wave 8, after close) | 10-24 05:18 | 2.1.308 | 255 | 50,223 | 29.82 | after |
| a75de3b4 (this wave, so far) | 10-25 14:23 | 2.1.308 | 41 | 51,100 | 3.01 | after |

Mean request 0: 74,685 before (n = 3), 49,230 after (n = 5), -25,455 tokens (-34.1%). The same version (2.1.304) sits on both sides (6b0e1f2a before, 74fa512e after), so the platform version is not the cause. Ceiling of the saving per after-session, tokens saved x requests x USD 0.20/M cache read: USD 1.30, 1.08, 1.12, 1.25, 0.19, i.e. 4.0-6.4% of that session's PI USD; plus one 1-hour write of the difference, about USD 0.20 a session. The ESTIMATE in the synthesis ("7.5-12% of a wave-4 PI", item w05-c7) is above what the records give for the wave-4 PI itself (114 requests x 28.3k x USD 0.20/M = USD 0.64 of 10.50, 6.1%). Confounders: the "after" request 0 drifts up 46.7k to 51.1k over four days (other changes to the PI's own context: skills, agent file, MCP servers connected at launch move request 0 by about 2.4k, CITED to the synthesis wave-7 platform facts); the two "before" sessions of 10-19 and 10-20 are a study session and a headless-style wave-4 PI, not the same kind of day; the ceiling counts no re-write after a cold gap (none seen for the PI).

**M2. Workers' request 0 before and after (w02-c4, merged 84ff038 2026-10-19T14:53Z). MEASURED (tokens); ESTIMATE (USD).**

Median request 0, workers of the lab's worktrees: 24,303 tokens before the merge (n = 44: authors 12, explorers 9, reproducers 23, all on 10-19), 14,480 after (n = 97), -9,823 (-40.4%), matching the claim's 42-45%. By type: authors 24,431 to 14,170-15,153, explorers 23,596 to 14,537-16,181, reproducers 24,309 to 13,619-14,540. Ceiling of the saving over the 97 later workers: sum of (24,303 - own request 0) x own requests x Sonnet cache read USD 0.10/M = USD 5.24 (ESTIMATE), against workers' list-price spend of the order of USD 110 for waves 4-8 (`__reports__/wave-08/explorer-w08-h/00-findings_v0.md`), about 5%. Confounders: workers before the merge ran on the study branch's agent files, which differed in more than the `Skill` tool; request 0 of explorers rose from 14.5k to 16.2k by 10-25 (briefs and notes grew), eating a tenth of the gain.

**M3. Hook durations the platform recorded, the budget hook (w06-c9 lean start, w07-c3 exec form, w08-c4 binary). MEASURED, selected records.**

| event | command form | n | median ms | p90 ms | first to last record (UTC) |
|:--|:--|--:|--:|--:|:--|
| PostToolBatch | `budget.py` in a string | 44 | 105 | 316 | 10-20 01:04 to 10-21 13:04 |
| PostToolBatch | `run_hook.py` in a string (after w06-c9) | 30 | 103 | 163 | 10-21 15:34 to 17:27 |
| PostToolBatch | `run_hook.py` exec form (after w07-c3) | 35 | 51 | 70 | 10-23 15:28 to 20:03 |
| PostToolBatch | Rust binary (after w08-c4) | 1 | 24 | 24 | 10-24 05:45 |
| SubagentStart | `budget.py` in a string | 47 | 467 | 1010 | 10-20 00:34 to 10-21 13:13 |
| SubagentStart | `run_hook.py` in a string | 20 | 247 | 847 | 10-21 15:27 to 17:18 |
| SubagentStart | `run_hook.py` exec form | 25 | 166 | 306 | 10-23 15:16 to 19:32 |
| SubagentStart | Rust binary | 6 | 282 | 361 | 10-24 05:22 to 10-25 14:29 |

Exec form (w07-c3): PostToolBatch median 103 to 51 ms, i.e. -52 ms, against the claim's median pair saving of 71 ms (guard) and 77 ms (budget, `__pondus__/w07-c3.md`): the right direction, 0.7 of the size. Lean start (w06-c9): the median does not move (105 to 103 ms) although the claim is 20-22 ms; the p90 halves (316 to 163) and the SubagentStart median drops 467 to 247 ms. Binary: 1 and 6 records, nothing to conclude (the SubagentStart median is above the exec-form one, 282 vs 166 ms, with n = 6 of which the first runs include the binary's first exec, 150-480 ms, CITED in the synthesis wave 7). Confounders: only runs that wrote stdout leave a record (`__instrumenta__/hook_platform_durations.py`'s own caveat), so these are the slow notes path; machine load differs by day (the M3 Pro with the Falcon extension); the eras are also the different waves with different task mixes.

**M4. Authors' cache pauses, three eras (w05-c1 waiting paragraph; w07-c7 1-hour cache). MEASURED counts, ESTIMATE USD.** Source: `python3 -I __instrumenta__/w09f_author_cache.py`, output `__reports__/wave-09/explorer-w09-f/author_cache.md`.

| era | authors | requests | requests after a pause over 300 s | cold (at least half the earlier context re-written) | extra USD of those re-writes | 1-hour share of writes | authors' USD |
|:--|--:|--:|--:|--:|--:|--:|--:|
| a: before w05-c1 | 20 | 1,621 | 32 | 29 | 16.38 | 0 | 62.14 |
| b: w05-c1 to w07-c7 | 11 | 1,018 | 9 | 9 | 5.48 | 0 | 32.54 |
| c: after w07-c7 | 7 | 666 | 6 | 0 | 0.00 | 1.00 | 27.22 |

Pauses per author 1.6 (a), 0.82 (b), 0.86 (c); cold re-write USD per author 0.82, 0.50, 0.00. For w05-c1 (the waiting paragraph): pauses per author halved and the cold re-write cost per author fell by 0.32 USD, about USD 3.5 over the 11 authors of era b (ESTIMATE; the claim's own cell was 0.57 of A at one task). Confounders: era a holds the wave-4 author whose 88-minute pipeline is the cause of most pauses (synthesis, wave 5), and the three eras are different tasks. For w07-c7: the 1-hour write premium paid is 1,692,557 tokens x (4.0 - 2.5)/M = USD 2.54; the 6 pauses, had the cache lived 5 minutes, would have re-written their earlier context, the sum of the earlier contexts of those 6 pauses x (2.5 - 0.1)/M = USD 3.08 (ESTIMATE, a counterfactual from the same records, assuming a 5-minute lifetime and that no pause was refreshed by a read); net +USD 0.54 over 7 authors. All 6 pauses are under 3,600 s. A before/after on USD is not meaningful here: 0.86 pauses per author in c against 1.6 in a means the work, not the setting, changed the pause rate.

**M5. Budget hook, real use (w03-c1). MEASURED over the lab's `harness.jsonl` files.** Source: `python3 -I __instrumenta__/w09f_harness_ends.py`, `__reports__/wave-09/explorer-w09-f/harness_ends.md`. 171 `end` records: median cost 0.38 of B, none over 1.0 B (authors 0.49, explorers 0.37, reproducers 0.28; max 0.92), 0 workers with a block, time over 1.0 T in 2% (4 of 171). So the 1.5x block, whose design cost three waves, has never fired on the lab's real work, and no worker finished over its budget. Whether the notes caused this (against the PI's generous budgets, median use 0.38) is not in these records: it is the no-notes arm that exists only as w04-c11, n = 3.

**M6. Hand-back length before and after w08-c6 (merged 16b05a8 2026-10-23T16:30Z). MEASURED (characters of the `SubagentHandback` message); ESTIMATE (PI cost).**

| period | n | median chars | p25 | p75 | max |
|:--|--:|--:|--:|--:|--:|
| all workers before | 125 | 3,562 | 1,877 | 4,413 | 19,661 |
| all workers after | 12 | 986 | 763 | 1,988 | 2,454 |
| explorers before / after | 33 / 5 | 4,265 / 1,988 | | | |
| authors before / after | 35 / 3 | 1,645 / 861 | | | |
| reproducers before / after | 57 / 4 | 3,670 / 704 | | | |

By day before the merge the medians are 3,899 (10-19, n = 44), 2,905 (10-20, n = 15), 3,866 (10-21, n = 51), 1,859 (10-23, n = 15): wave 8's own workers were already shorter before the merge, because the claim's six treated briefs ran in that wave. At about 3.5 characters a token [assumption: English prose], 2,576 fewer characters (3,562 to 986) is about 740 tokens a hand-back; at the PI's remaining 100 requests when a hand-back arrives [assumption: wave 8 had 229 PI requests and hand-backs arrive across them] x USD 0.20/M that is USD 0.015 a hand-back, about USD 0.35 over a wave of 23 workers, against a PI session of about USD 26 (1.3%). Confounders: the PI's brief text is the cause, not any hook; reproducers write their verdict in the claim file, so their hand-back is short by role; the "after" has 12 workers, 4 of them the same PI session's last wave-8 dispatches.

**M7. Name binding before and after w08-c12 (merged 3d5147a 2026-10-23T18:18Z). MEASURED on the lab's harness files.** Source: `python3 -I __instrumenta__/w09f_name_audit.py`, `__reports__/wave-09/explorer-w09-f/name_audit.md`. Of the `start` records whose agent has a name in its `.meta.json`, 14 of 130 carried another dispatch's name (waves 4 to 8; always same-type dispatches started together, in swapped pairs, for example explorer-w06-a recorded as w06-b); 0 of 15 after the merge, where only one start came up ambiguous: this run's own start, which was marked `name_unconfirmed` with candidates `explorer-w09-e,explorer-w09-f` and the default budget B = 3.0 / T = 20, then a `named` line followed one second later. The others of the batch (c, d, my own second record) were bound from their briefs with B = 8/80, 5/50, 4/35. So the fix works live in the one ambiguous case I could see; its saving (a wrong budget on a swapped name) is in the records only as the 14 swaps, the cost of which nobody measured. Confounder: the after-sample has 1 ambiguous batch.

## Worst-fitting case

The story is "landed changes were measured, the money figures are estimates, but records can now close several". The case that fits worst is **w07-c7, the authors' 1-hour cache**. Claimed saving: net +USD 0.87 of 47.80 (ESTIMATE, at a 300 s bound; -0.60 at 360 s, P(net <= 0) = 0.34) in the claim and the wave-7 synthesis; wave 8 re-fits it to -0.02 +- 0.39 per life with expected value pointing at 5 minutes (ESTIMATE, explorer-w08-c; `__statera__/synthesis.md` Wave 8, "Cost choices as decisions"); these records give +0.54 over 7 authors, from six pauses (M4). Three ESTIMATEs, three sizes, the sign unsettled; the only direct record is that the 17 of 17 writes were 1-hour and 0 cold re-writes followed, and a before/after cannot isolate the setting from the pause rate, which halved with the waiting paragraph (w05-c1). It landed by the PI's decision rule, and nothing available can say whether it saves money. Runner-up: w06-c9 (lean start), whose recorded median PostToolBatch duration does not move (105 to 103 ms) although the claim is 20-22 ms, saved only by a p90 change and by the SubagentStart median (467 to 247 ms) in selected records.

The case that fits best: **w02-c4 (workers without Skill)**: the claimed 42-45% smaller start reappears as -40.4% over 44 versus 97 workers (M2), and the effect follows into every later wave. Next best: w05-c7 (request 0 -34.1%, same version on both sides), with the USD ceiling 4.0-6.4% of a PI session, below its ESTIMATE of 7.5-12% (a 0.5-0.8 ratio).

## Not covered

- Rows 8, 10, 11, 14, 19, 21 (live false denials), 22: marked R in the table, not computed (each is a count over transcripts or files; I did none, for the budget).
- A before/after on **minutes**: workers' wall times per task do not exist for the same task before and after (no change landed together with a repeated task). I did not compare wave wall times; they are dominated by one author's pipeline (synthesis, wave 5).
- The Rust guard's wall effect (rows 21, 26, 32, 33): silent PreToolUse runs leave no duration record, so only a new run can time it.
- Rows 28 and 31 need more workers after the merge; the PI will have them at the end of wave 9.
- The 41 of 306 subagent transcripts whose last tool call is not `SubagentHandback` (Bash 30, Write 4, none 3, SendMessage 2, Read 1, Skill 1): w02-c5's "15 of 15 hand-backs saved" says nothing about them; I did not classify them (lost deliverable, resumed, or killed).
- USD by wave from cost-state per session for the PI before/after: I used list price from the transcripts (`PRICES` copied from `scripts/lab_status.py`), not cost-state, so the PI USD column is a lower bound in sessions with an unflushed stream tail.
- Waves 1-3 claims that did not survive (w01-c1 to w01-c13 other than the above) are not rows: they were superseded or restated, and landed inside the rows above.

## Steering questions

- [now] Do you want the table read as the answer: mechanism MEASURED for each landed change, saving ESTIMATE or counterfactual for each, five token/ms before/after pairs now on records (M1-M3, M6, M7)? Or should the next wave file a claim for each M-row so that a verifier can say whether it holds?
- [later] w07-c7 stays on the authors' agent file with no saving shown. Should the lab revisit it with a paired run on one author task (cost of the order of USD 2), or leave it as the user's call on risk attitude as the wave-8 map says?
- [later] Should `harness.jsonl` also record the first request's token total and the hook's own duration for every hook run, so that M1-M3 become one query rather than a transcript scan?

## Pointers

- Table and tables M1-M3, M6: `python3 -I __instrumenta__/w09f_threads.py > __reports__/wave-09/explorer-w09-f/threads.tsv` then `python3 -I __instrumenta__/w09f_before_after.py > __reports__/wave-09/explorer-w09-f/before_after.md` (reads `~/.claude/projects`, read only; about 20 s).
- M3: `python3 -I __instrumenta__/w09f_hook_dur.py > __reports__/wave-09/explorer-w09-f/hook_dur.md`.
- M4: `python3 -I __instrumenta__/w09f_author_cache.py > __reports__/wave-09/explorer-w09-f/author_cache.md`.
- M5: `python3 -I __instrumenta__/w09f_harness_ends.py > __reports__/wave-09/explorer-w09-f/harness_ends.md` (reads the sibling worktrees' `__statera__/harness.jsonl` under `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/`).
- M7: `python3 -I __instrumenta__/w09f_name_audit.py > __reports__/wave-09/explorer-w09-f/name_audit.md`.
- Scripts cited as `__instrumenta__/w09f_threads.py@<commit>`, `w09f_before_after.py`, `w09f_hook_dur.py`, `w09f_author_cache.py`, `w09f_harness_ends.py`, `w09f_name_audit.py` (commit of this report).
- Landed set: `git -C /Users/hacker/Documents/src/CrackingShells/Murmuration log --first-parent main` and `git diff --stat <merge>^1 <merge>` per merge; claim labels from `python3 -I scripts/lab_status.py`; savings from `__statera__/synthesis.md` ("What landed", Waves 5-8) and `__pondus__/<claim>.md` heads.
