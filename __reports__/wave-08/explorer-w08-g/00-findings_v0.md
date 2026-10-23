---
type: findings
wave: wave-08
author: explorer-w08-g
date: 2026-10-24
version: v0
decision-required: none
---

# Batching independent tool calls: what it would save in USD, and whether a line in an agent file moves it (findings v0)

Stayed inside the brief. One addition: the brief asks for two or three runs per arm on one task; the first task showed the unchanged arm already batching, so I ran four more task variants (five tasks, 46 headless runs of which 41 measured and 5 warm-ups, USD 1.45 by their result records, at least; the cap of USD 5 was not approached) to look for a case where the base arm does not batch.

## Result

1. **Nothing to lever in the lab's transcripts: ESTIMATE, bounded.** Of 4,239 requests of 77 workers (waves 4-8), 3,904 carry exactly one call and 2,542 of those are followed by a request that carries a call and is not interrupted by a message. By a token test and a read-only rule, only **95 requests (2.2%) could have gone out in the message before them (loose) and 44 (1.0%) under the strict rule**. My hand audit of the strict rule (32 worker pairs, one reader) finds 18 independent, 9 doubtful, 5 dependent. Savings had they merged: **USD 0.47 (strict) to 0.94 (loose) of cache reads and uncached input** of the absorbed requests, plus USD 0.41 to 1.31 if the absorbed request's thinking were not produced and not carried; against USD 109.92 recorded for these workers: strict, audit-adjusted **0.2% to 0.7%**, loose, unaudited upper bound **0.9% to 2.1%** (formula below). By role: reproducer 45 loose / 20 strict of 1,162 requests (3.9% / 1.7%), author 31 / 14 of 1,889 (1.6% / 0.7%), explorer 17 / 10 of 1,148 (1.5% / 0.9%).
2. **The lever cannot be shown to work because the unchanged agent already batches: MEASURED (n = 3 to 4 per arm, five tasks, 46 runs, Sonnet 5.5 subagents of a Haiku parent).** With the independent files named, the unchanged agent file sent all reads in one message in 4 of 4 runs (8 files) and 3 of 4 runs (16 files) of the read-only tasks (the fourth run counted lines with Grep in 2 calls instead) and chained the shell in the tasks with Bash; requests per run 4.00 base against 3.75 to 4.00 with the line, USD per run equal within the spread of the base arm. Answers stayed right in 40 of 41 runs that had a unique right answer; the one wrong run is in the arm with the line (task 4, 1 of 4), n too small to say anything.
3. **Where the lab's single-call requests come from: MEASURED.** 65% of the 2,542 candidate pairs (1,643) are a Bash command that runs or writes something followed by another such command (X then X), and the token test cannot say anything about those; 251 are a read then X, 220 X then read. That is the class of "run it, look at the output, run the next thing", which the line does not address. Wave 7's earlier count reproduces exactly on the same rule (loose 19 / 23 / 25 absorbed requests in waves 4 / 5 / 6, USD 0.56; strict 8 / 12 / 12) [source: `pairs_by_wave_role.tsv`; `__reports__/wave-07/explorer-w07-b/00-findings_v0.md`].

## Method

**Data.** The main transcripts of waves 4 to 8 and their `subagents/` folders (83 transcripts, 110.6 MB: 77 workers, 5 PI sessions, and this run, which is dropped); the wave-8 transcripts are live, so the counts of wave 8 grow. Parsed with `__instrumenta__/w07b_loop_parse.py` (turns, calls, classes, tokens first seen in a result) and `__instrumenta__/w08g_sig.py` (thinking signature characters per request, whether every token of a request's calls is in the worker's first prompt).

**Dependence, judged mechanically.** Pair (j-1, j): request j-1 carries exactly one call with a result and no error; request j carries calls and no message arrived in between. Loose: both requests read-only (Read, Glob, Grep, ToolSearch, colgrep, Bash with only read-only words and no redirect) or both file writes to different paths; no specific (path-like or 12+ character) token of a call of j first appeared in a tool result of j-1 (or of the batch before it); no call a near-copy (word overlap 0.6 or more) of the previous one; at most 8 calls per message. Strict: also every call of j names at least one such token and none is unseen anywhere before. Brief: strict, and every token of every call of j occurs in the worker's first prompt. A greedy walk over the worker's requests gives the absorbed requests (a batch may grow) [source: `__instrumenta__/w08g_pairs.py`, rule copied from `w07b_loop_tables.py` `merge_walk`].

**Money (ESTIMATE).** For an absorbed request j with model prices p (input, output, read, write): saving_reads = cache_read_j x p_read + input_j x p_input. The request's cache write is not saved: its tokens (the previous result) would be written one request later in the merged world. saving_think = T_j x (p_output + n_later x p_read + p_write) with T_j = 0.3278 x (signature characters_j - 806.4) thinking tokens (explorer-w08-f's fit, R2 0.962, fit range 856 to 6,560 characters; applied far outside it for a few requests), n_later the requests after j in that worker, p_write the 1-hour or 5-minute rate of the next request. The call text of j is still produced in a merged message, so it is not counted. Sums are for workers only; PI rows are in the tsv.

## Table

### Requests that could have merged, and USD (workers of waves 4-8) [ESTIMATE; counts MEASURED by the rule above]

| Role | Workers | Requests | Single-call requests | Pairs candidate | Loose pairs / absorbed | Strict absorbed | Brief absorbed | USD loose reads / + thinking | USD strict reads / + thinking | USD recorded | Loose, upper, % of recorded | Strict, reads, % of recorded |
|:--|--:|--:|--:|--:|--:|--:|--:|:--|:--|--:|--:|--:|
| author | 22 | 1,889 | 1,731 | 945 | 36 / 31 | 14 | 2 | 0.504 / 1.368 | 0.243 / 0.521 | 64.26 | 2.13 | 0.38 |
| reproducer | 31 | 1,162 | 1,080 | 811 | 44 / 45 | 20 | 5 | 0.214 / 0.435 | 0.100 / 0.176 | 17.57 | 2.48 | 0.57 |
| explorer | 22 | 1,148 | 1,068 | 767 | 13 / 17 | 10 | 1 | 0.210 / 0.298 | 0.128 / 0.185 | 26.83 | 1.11 | 0.48 |
| other (guide, general-purpose) | 2 | 40 | 25 | 19 | 2 / 2 | 0 | 0 | 0.014 / 0.151 | 0 | 1.26 | 11.93 | 0 |
| **all workers** | 77 | 4,239 | 3,904 | 2,542 | 95 / 95 | 44 | 8 | 0.942 / 2.252 | 0.470 / 0.882 | 109.92 | 2.05 | 0.43 |
| PI (5 sessions) | 5 | 752 | 501 | 233 | 25 / 21 | 10 | 3 | 0.556 / 1.226 | 0.303 / 0.750 | 82.91 | 1.48 | 0.37 |

By wave, workers (loose absorbed / strict absorbed / USD loose reads / USD loose + thinking): w4 19 / 8 / 0.159 / 0.242; w5 23 / 12 / 0.125 / 0.271; w6 25 / 12 / 0.276 / 1.014; w7 18 / 5 / 0.224 / 0.480; w8 (partial, 9 workers) 10 / 7 / 0.158 / 0.245. [source: `pairs_by_wave_role.tsv`, `pairs_per_worker.tsv`]

"Recorded" is the sum of per-request list-price USD with output at the stored count (a lower bound of output). The thinking column is dominated by a few requests: five requests carry USD 0.79 of the USD 1.31 thinking carry of the loose set (the largest: 15,109 estimated thinking tokens, author-w06-4, request 5, signature 46,900 characters, USD 0.37); with thinking capped at 2,000 / 1,000 / 500 tokens per request the carry is USD 0.735 / 0.544 / 0.386 [source: `pairs_think_sensitivity.txt`]. The median absorbed request has 256 estimated thinking tokens.

### Why candidate pairs do not merge (all workers, 2,542 single-call requests followed by a call) [MEASURED]

| Reason (first that applies) | Pairs | Share |
|:--|--:|--:|
| Bash exec or script then Bash exec (X then X) | 1,643 | 64.6% |
| read-only then X | 251 | 9.9% |
| X then read-only | 220 | 8.7% |
| error in the previous result | 139 | 5.5% |
| X then file write / write then X / mixed | 163 | 6.4% |
| token of the next call first seen in the previous result | 15 | 0.6% |
| independent, read-only (loose) | 95 | 3.7% |

[source: `pairs_why_not.tsv`; 2,168 of the 2,542 pass the token test whatever the class, which says the token test alone is no evidence of independence for X calls.]

### Hand audit of the strict rule [ESTIMATE; one reader, from the first 120 characters of each call, not committed]

| Judgment | Worker pairs | Share of 32 |
|:--|--:|--:|
| independent (Y) | 18 | 56% |
| doubtful (M) | 9 | 28% |
| dependent (N) | 5 | 16% |

Eight PI pairs in the same random sample of 40 are left out. Audit-adjusted strict savings: 44 x 0.56 to 0.84 = 25 to 37 requests; USD 0.26 to 0.39 (reads), 0.49 to 0.74 (reads + thinking) [source: `audit_judgments.tsv`: sample number, wave, worker, request index, judgment, no text].

### The lever, five tasks [MEASURED; Sonnet 5.5 subagent, Haiku 5.5 parent calls the Agent tool once; auto permission mode; 3 to 4 runs per arm]

Agent files differ by one added line. `lever1`: "When several tool calls do not depend on each other, send them together in one message." `lever2` (task 1 only): "When the files you need are named in your task, read all of them in one message (several tool calls together), not one per message." USD is the Sonnet subagent's `modelUsage.costUSD` from the result record (output included), mean (range).

| Task (tools) | Arm | Runs | Requests | Calls per request (sum/sum) | Mean USD (range) | Thinking tokens | Right |
|:--|:--|--:|--:|--:|:--|--:|--:|
| 1: 6 shards + prices + claim, files named in the agent file (Read, Glob, Grep, Bash) | base | 3 | 3.67 | 1.45 | 0.0191 (0.0167-0.0223) | 19 | 3/3 |
| 1 | lever1 | 3 | 3.33 | 1.50 | 0.0206 (0.0166-0.0229) | 0 | 3/3 |
| 1 | lever2 | 3 | 3.33 | 1.50 | 0.0198 (0.0180-0.0214) | 0 | 3/3 |
| 2: 6 shards, files named in claim.md (same tools) | base | 4 | 4.00 | 1.25 | 0.0190 (0.0183-0.0196) | 0 | 4/4 |
| 2 | lever1 | 4 | 4.00 | 1.19 | 0.0190 (0.0175-0.0217) | 0 | 4/4 |
| 3: 12 shards, files named in claim.md (same tools) | base | 4 | 4.00 | 1.25 | 0.0203 (0.0190-0.0219) | 0 | 4/4 |
| 3 | lever1 | 4 | 4.00 | 1.12 | 0.0209 (0.0187-0.0238) | 0 | 4/4 |
| 4: count rows of 8 shards named in claim.md (Read, Glob, Grep only) | base | 4 | 4.00 | 3.00 | 0.0308 (0.0278-0.0348) | 414 | 4/4 |
| 4 | lever1 | 4 | 3.75 | 3.13 | 0.0296 (0.0246-0.0352) | 319 | 3/4 |
| 5: count rows of 16 shards (Read, Glob, Grep only) | base | 4 | 4.00 | 4.06 | 0.0383 (0.0251-0.0439) | 499 | 4/4 |
| 5 | lever1 | 4 | 4.00 | 4.38 | 0.0373 (0.0267-0.0429) | 373 | 4/4 |

Calls per request by run, for the read-only tasks: base 2,1,8,1 (every task-4 run; the 8 shard reads in one message), 2,1,16,1 or 2,16,0,1 (task 5, three runs), and 2,1,2,1 (one run, 6 calls, a cheaper route that counted lines with Grep, USD 0.0251). With the line, task 4: 2,1,8,1 three times and 2,8,1 once (the run that answered all eight files wrong, UNSUPPORTED, USD 0.0246); task 5: 2,1,16,1 twice, 2,16,1 and 2,1,2,0,1 (the Grep route again, USD 0.0267). "Right" = recomputed total within 0.005 and verdict not SUPPORTED (tasks 1-3), or exactly the two wrong files named and verdict not SUPPORTED (tasks 4-5). Order of runs: one warm-up, then base and lever arms alternating within a task, tasks 2/3 and 4/5 run as two concurrent sequences. [source: `arms_task1_files_in_agent_file.tsv` ... `arms_task5_readonly_16.tsv`; scripts `w08g_make_task.py`, `w08g_make_count_task.py`, `w08g_arms.sh`, `w08g_sub_table.py`]

## Worst-fitting case

The story: "batching saves little because there is little to batch, and workers batch already when there is". The cases that fit it worst:

- **The best-fitting workers for batching in the lab**: reproducer-w05-4 (51 requests, 4 absorbed under every rule, 4 under the brief rule, USD 0.021 of 0.63) and reproducer-w05-3 (32 requests, 5 loose / 3 strict absorbed, 16% / 9% of its requests, USD 0.035 loose upper bound of 0.35). The wave-5 reproducers are where the idea pays at all (role row of wave 5: 8.9% loose, 4.5% strict of 202 requests, USD 0.142 of 2.4), and even there the saving is a few cents per worker. The largest percentage of USD is an "other" worker (general-purpose helper of wave 7, 31 requests, 2 absorbed, USD 0.151 of 1.08), and it rests on one 8,855-token thinking block.
- **The worker where batching would save most in USD**: author-w06-4 (126 requests, 122 single-call): one absorbed request, USD 0.376 loose upper bound, 9% of its USD 4.03, all from one estimated 15,109-token thinking block outside the signature fit's range. Remove that block and the worker's saving is under USD 0.01.
- **Against "the line does not change anything"**: task 4 with the line shows 3.75 requests against 4.00 (one run of four lost a request by answering after the batch of reads, and that run was the wrong one); the unchanged agent was already at 3 to 4 calls per request. The single wrong run is in the line's arm (answer all eight files wrong, 1 of 4); with n = 4 I cannot call it an effect or noise.
- **The lab agent files were not run** (reproducer.md has 150 turns, 40,000-token prompts, a skill, many tools, hooks). Task agents have a 5,000-token base context. The lever may behave differently there; the base arm's 100% batching is a property of fresh short tasks.

## Not covered

- The lab's own agent files as the test arm, a long worker, Opus. A lever test on a worker whose context is 50,000+ tokens, where the saved request is worth USD 0.005 to 0.015 each, would need hundreds of requests per arm.
- Whether the model chose call j because of the content of result j-1 (semantic dependence). The token test cannot see it (the `wc -l` then `sed -n 60,248p` pair, number 248, was in the sample); the audit found 5 of 32 dependent and 9 doubtful, one reader, from 120-character heads. The loose count (95) is not audited.
- Savings in time (wave 7 measured 0.2% to 0.4% of wall for the same rule); only USD here. Output tokens of the absorbed request other than thinking; stream-start counts make them unrecoverable.
- PIs (reported in the table, not analysed); waves 1-3; the PI's use of `Agent` batches (parallel dispatch of workers).
- Cache lifetime effects on the carried thinking (rewrites after pauses), which would raise the thinking estimate slightly; and the effect of hooks that add text per request.
- A positive test of the lever: no arm was found where the unchanged agent fails to batch, so the lever was not shown to cause batching, only not to harm (3 to 4 runs per arm).

## Steering questions

- [now] The ceiling is 0.2% to 0.7% (audited strict) and at most 2% (loose, with thinking carry) of worker USD; wave 7 had measured 0.3% to 0.6% of time and USD for the same rule. Do you want to drop batching as a lever and spend the next probe on the X-then-X chains (65% of single-call requests: run, look, run again), for example a stop rule or fewer runs per claim?
- [now] If you still want the line in the agent files for free: nothing in these runs shows it harms (one wrong run of 22 in the line's arms, 0 of 19 in the base arms); a test on a real worker (reproducer, 30+ requests) is the missing check, and it costs about USD 1 to 2 for 3 runs per arm.
- [later] An effort of `low` and a batching line both act on thinking and request counts of the same turns; a joint test would be cheap on these tasks but does not address the 65%.

## Pointers

All in `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-8-928ebd/__reports__/wave-08/explorer-w08-g/` (tables only; the raw runs, parsed turns and the audit sample with call heads stay in `/private/tmp/murmuration-w08/explorer-w08-g/`, not committed). `claude` 2.1.304, `CLAUDE_CODE_SHELL=/bin/bash`, auto permission mode, no budget flag; seeds of the tasks 9, 21, 31, 5, 6 (generator), model sampling not seeded. Prices: `scripts/lab_status.py` PRICES. Scripts as `__instrumenta__/<file>@<commit>` at the commit of this report:

- Parse: `python3 -I __instrumenta__/w07b_loop_parse.py <S>/parsed w4=<main.jsonl> ... w8=<main.jsonl>` (0.5 s) and `python3 -I __instrumenta__/w08g_sig.py <S>/sig w4=<main.jsonl> ...` (about 5 s); the five main transcripts are in `~/.claude/projects/*wave-4-3417be`, `*lab-system-optimization-1aa673`, `*blissful-villani-34edd8`, `*xenodochial-franklin-bc67fb`, `*murmuration-wave-8-928ebd`.
- Pairs, money, audit sample: `python3 -I __instrumenta__/w08g_pairs.py <S>/parsed <S>/sig <this folder> <S>/audit_sample.txt` gives `pairs_by_wave_role.tsv`, `pairs_per_worker.tsv`, `pairs_why_not.tsv`, `pairs_think_sensitivity.txt` (runs in about 2 s).
- Lever arms: `python3 -I __instrumenta__/w08g_make_task.py <S>/t2 21 6 claim` (and `<S>` 9 6 agent for task 1, `<S>/t3` 31 12 claim), `python3 -I __instrumenta__/w08g_make_count_task.py <S>/t4 5 8` (and `t5` 6 16); `__instrumenta__/w08g_arms.sh <S>[/tN] <reps> "base lever1"` (about 20 s per run, uses `w08f_run.py`); `python3 -I __instrumenta__/w08g_sub_table.py <S>[/tN] <truth.json> V <out.tsv>`.
- A first pass of `w08g_sig.py` was started without the `__main__` guard and spawned itself recursively under macOS `spawn`; it ended by itself (a stray task output file of 512 KB in the scratchpad). It is fixed; no results came from it.
