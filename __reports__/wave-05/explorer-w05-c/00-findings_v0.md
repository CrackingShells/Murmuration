---
type: findings
wave: wave-05
author: explorer-w05-c
date: 2026-10-21
version: v0
decision-required: confirm
---

# Where the workers' requests, tokens and time go: findings (v0)

I did not leave the brief. Two additions: the same measurement on the 44 wave-1-to-3 workers as a comparison, and one direct test of the colgrep path instruction.

## Result

Orientation is small and it is not where wave 4's workers lost money: reading the lab's documents at the start of a run is about 3% of list-price spend (strict bound; 6% to 8% on wider definitions). What is large and shared is (a) the 5-minute prompt cache lapsing, which costs about 17% of the 15 workers' spend in wave 4 and 14% in waves 1 to 3 (ESTIMATE), (b) one request per tool call with a context that reaches 300k tokens in authors, and (c) wall time spent waiting on experiments (tool time is 62% of active seconds, and 25 waits over 120 s are 38% of all active seconds). Three one-sentence changes to agent files or the skill would remove the repeatable parts of (a) and a papercut seen in half of all workers; trimming the skill, `framing.md` or the tool outputs would save about 1% to 3% each (ESTIMATE).

## Table

All figures are for the 15 wave-4 workers unless a row says waves 1-3 (44 workers). "List-price USD" is the harness's own quantity re-derived from the transcripts; it is a measurement artefact for shares, not budget use.

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Re-derivation check | Per-worker list-price USD equals the harness `used` for 15 of 15 workers (to 0.001) and active seconds equal the harness `active_s` to within 1.5 s for 15 of 15 | CHECKED (15 workers) | `w4/worker_phase_table.csv` columns `usd_list`/`usd_harness`, `active_s_transcript`/`active_s_harness` |
| Size of what was measured | 15 workers, 716 requests, 770 tool calls, USD 25.66 list price, 16,913 s active (282 min). Wave wall time 88 min, so parallelism about 3.2 (formula: 16,913 s / (88 x 60 s)) | CHECKED / ESTIMATE (ratio) | `w4/summary.md`; wave 4 wall time from `__statera__/wave-04.md` |
| Token-type split of USD | cache write 36%, cache read 31%, output 33%, uncached input about 0%. Authors 405 requests USD 18.79; reproducers 311 requests USD 6.87 | CHECKED | `w4/summary.md` section 1 |
| Output share is soft | The transcript stores output tokens at start-of-stream for 683 of 716 requests; the harness estimates `max(recorded, content chars / 1.3)`. In the 33 requests with a final count, chars per output token is 1.73, not 1.3, which would put output near 25% instead of 33% | CHECKED (n=33 final records) | raw transcripts; `usage.iterations` records; command in Pointers |
| Phase shares (mutually exclusive) | start (first request) 2% of requests / 1.6% of USD / 0.4% of seconds; orientation 1.7% / 1.8% / 0.5%; work 78% / 69% / 87%; writing the claim, verdict or report ("deliver") 11% / 19% / 9%; exchange messages 2.8% / 3.2% / 1.4%; hand-back 4.1% / 5.0% / 1.9%. Waves 1-3: orientation 1.0% of USD, deliver 13.9%, work 74.0% | CHECKED (counts); the phase boundaries are my rules, stated in `w05c_phase_table_md.py` | `w4/phase_table.md`; `w123/phase_table.md` |
| Orientation, three bounds (share of USD) | strict (requests among the first 3 whose strongest call reads docs, searches or reads outside the lab) 3%; prefix (every request before the first run or write, evidence reading included) 6%; wide (every doc/search/outside request of any run) 8%. Waves 1-3: 3%, 5%, 16% | ESTIMATE: sum of USD of the selected requests / total | `w4/summary.md` "Orientation, three bounds" |
| Same reading by 13 of 15 workers | `__design__/framing.md` (8,109 bytes, about 2k tokens). Carried for a 30-request reproducer it costs about USD 0.011, 2% of that worker's spend; for a 100-request author 0.4% | ESTIMATE: tokens x (cache write + later requests x cache read), 4 chars/token | `w4/worker_phase_detail.json`; sizes from `ls -la` |
| Fixed start cost | First request (writes about 13.3k to 14.4k tokens) plus carrying that context at cache-read price for the later requests: authors 4% of spend, reproducers 10% (waves 1-3: 6%, 14%, explorers 7%). Of those 13.5k tokens about 4.6k are system prompt plus tool names (it is the only part read from cache on every cold resume: `first_cr` 4,575 to 4,673) and the skill is 9,809 characters, about 2.5k tokens | ESTIMATE; CHECKED for the token sizes | `w4/summary.md` "Fixed start cost"; `pre_chars` in the detail json |
| Cold cache events | 11 events (4 resumes after idle 312 to 997 s, 7 tool waits of 313 to 602 s) rewrote 86k to 338k tokens each; extra cost versus a warm cache USD 4.41 of 25.66 (17%). Waves 1-3: 26 events, USD 14.10 of 99.98 (14%) | ESTIMATE: cache-write tokens x (2.5 - 0.1) USD per million | `w4/summary.md` "Cold resumes and in-run cache expiries" |
| Which workers | All 7 mid-run lapses are authors, and each followed a Bash call that waited 313 to 602 s (`timeout 590 sh -c "until ..."`, `until ... sleep 10`). Author-w04-4: 3 events, USD 2.31 of 7.15 (32%) | CHECKED | same table |
| Remedy for mid-run lapses | Split every wait over 240 s into polls of at most 240 s; a poll costs a cache read of the context. Net saving USD 2.20 of 25.66 (9%) in wave 4; USD 4.95 of 99.98 (5%) in waves 1-3 | ESTIMATE: formula in `w05c_summarize.py` last-but-one block (premium minus polls x (ctx x 0.1/1e6 + 200 output tokens x 10/1e6)) | `w4/summary.md` last "ESTIMATE" section |
| A resume that did nothing | Author-w04-4 was resumed a third time by a task notification of a background `until` loop it had started and left running ("failed" at its 600 s limit). It rewrote 337,631 tokens (USD 0.85) for one text-only turn that said "Nothing further is needed from me" (1.4 s of work) | CHECKED | `agent-ab28dda4375d2902b.jsonl` rows 589 to 594; `w4/summary.md` cold table row 1 |
| Warm resumes are cheap | 12 resumes with idle under about 3 min (cache read of 56k to 300k tokens): first request USD 0.013 to 0.051 | CHECKED | `w4/summary.md` "Warm resumes" |
| What the exchange costs the author side | 7 runs opened by a peer message cost USD 2.26, of which the first requests are USD 1.23, and 2 of those 7 first requests were cold (USD 0.23 and 0.84). Waves 1-3: 22 runs, USD 11.70, first requests 5.21. Reproducer's wait for the answer: median 83 s (n=11, 17 to 447 s); 447, 419 and 311 s answers were to authors inside a 313 to 541 s tool wait, since a message is delivered "at its next tool round" | CHECKED (counts); the link to the tool waits is CONJECTURE (timing only) | `w4/summary.md` "Exchange latency" |
| Resume runs in general | Runs after the first (raises by the PI, peer messages, one notification) hold 31% of USD (8.00 of 25.66): 8 coordinator-opened runs cost USD 4.90 and 3,058 s | CHECKED | `w4/summary.md` end |
| Failed calls | 31 of 770 calls (4%). Classes: nonzero exit of a probe 14; `sleep N` blocked by the harness 10 (8 workers); zsh `=`-expansion 3; colgrep relative path 2; tool not available 1; permission denied 1. Their requests cost USD 0.69 in total (2.7%). Waves 1-3: 132 of 2,441 calls, `sleep` blocked 25 (23 of 44 workers), zsh 11 | CHECKED | `w4/summary.md` "Failed calls by class" |
| The blocked-sleep hint points at a tool workers lack | The harness answers `sleep 45` with "To wait for a condition, use Monitor with an until-loop"; none of the four `tools:` lines in `agents/*.md` lists Monitor, and reproducer-w04-2's one Monitor call failed with "No such tool available: Monitor" | CHECKED (grep of the four agent files; one transcript) | `agents/{author,reproducer,explorer,proof-adversary}.md` line 5; `w4/summary.md` failed-call list |
| colgrep path in the agent files is unreliable | The four agent files say `paths: ["__instrumenta__"]`. In wave 4, 2 of the 5 colgrep searches failed with `PATH_NOT_FOUND ... (relative paths ...)`. In this session the same relative path did not fail but searched `/Users/hacker/Documents/src/CrackingShells/Murmuration/__instrumenta__` (the plugin source), not this lab's folder; the absolute path found this lab's new file | CHECKED (2 calls here, 2 failures there) | `agents/*.md` line 25-26; the two search calls in this session |
| Re-reads | 30 repeat reads over 128 distinct files read by Read or a bare cat/sed/head (23 files read more than once), mostly slices of one file or the claim file after the verdict was appended; waves 1-3: 80 over 295 | CHECKED (counts; slices count as repeats) | command in Pointers |
| Tool outputs | All tool outputs carried: USD 3.16 of 25.66 (12%). Outputs over 8,000 chars: 60 of 770 calls, USD 1.62 (6% of spend). The largest, `budget.py` read whole (61,427 chars, USD 0.22 carry), was the file that author was rewriting | ESTIMATE: chars/4 tokens x (write + later requests x read) | `w4/summary.md` "Largest tool outputs" |
| Where context comes from | Growth first to last request (e.g. author-w04-4 14k to 342k tokens) is 20% to 25% tool results and the rest is the worker's own output and thinking (author-w04-4: results 66k tokens, own output about 155k, growth 328k) | ESTIMATE (chars/4; thinking is invisible) | table in this report's Pointers |
| Chains of read-only requests | 43 chains of 2 or more consecutive look/doc/search requests; making each one request would save between USD 0.56 and 1.94 (2% to 8% of spend) | ESTIMATE: lower bound is the cache read of the context of each removed request, upper bound the whole request | `w4/summary.md` "Chains" |
| Calls per request | 670 of 716 requests make one call, 34 make two, 10 make three or more, 2 make none | CHECKED | `w4/summary.md` |
| Where the wall time goes | Tool side 62% of active seconds (10,557 of 16,913 s); 25 waits over 120 s are 6,447 s, 38% of all active seconds. Orientation is 0.5% of seconds. The wave's critical path is the three long authors (first hand-back at +33, +49, +54 min of 88; exchange and last hand-backs to +67, +77, +80) | CHECKED | `w4/summary.md` "Seconds by category" and "Tool waits"; hand-back times from the transcripts |
| Harness `start` lines | 4 of 31 `start` lines carry another worker's name (two pairs of workers dispatched in the same second), and the 4 simultaneous authors' start lines log B=3, T=20 with `source: unknown` though their briefs said 4/30, 8/60, 12/60, 8/60; `end` lines carry the right names | CHECKED | `harness.jsonl` vs the `.meta.json` names; command in Pointers |

## Worst-fitting case

The account is: orientation is small, cache lapses and long contexts dominate. Two workers fit it worst.

- author-w04-6 (24 requests, USD 0.50): strict orientation 17% of its spend (3 of its first 3 requests are doc/search; its first request reads `lab_init.py` whole, 30,889 chars, and `briefs.md`), wide 24%, no cold event, no failed-call class that a sentence would remove. For short workers the fixed start cost is large: reproducers sit at 10% to 14% (reproducer-w04-2, -6 at 14%). So "orientation is negligible" holds for pooled spend (3%) and for authors (0% to 2% for authors 2, 3 and 4; 7% for author-w04-1; 17% for author-w04-6) and fails for the cheap ones; as a share of the whole wave they are small because they are cheap.
- author-w04-3 (USD 4.81): one lapse (6% of its spend). Its cost is carrying a 301k-token context for 116 requests (cache read 42% of its spend), which no sentence about waiting removes.

The cheapest sentence-level fixes also fit worst in one place: the 5-minute lapse after an idle gap (4 cold resumes) cannot be removed by the worker, because the idle time is the verifier's work time (author hand-back to first question: 134 to 997 s).

## Not covered

- The PI main thread, and the PI's own dispatch lag between a hand-back and the next dispatch: the brief was the workers. Claim c3's reproducer started 1,012 s after the author's first hand-back (the claims c2 and c3 share author-w04-2); I did not read the PI transcript to say why.
- Whether lowering the workers' effort or thinking would cut the output third of the spend: all 716 requests ran at `effort: high` (`effort` field of the transcript rows); I did not find or test an agent-file setting for it, UNVERIFIED that one exists.
- Quality: nothing here says whether a faster or leaner worker gives the same verdicts. Every saving above is an ESTIMATE on spend or time, not a result of running a changed plugin.
- What the workers' experiments waited on (headless `claude -p` cells, serial or parallel): the long waits are work, and I did not ask whether the cells could run more in parallel.
- The 1-hour cache write option (`is1hCacheTTL: false` in the prefix state, price 4.0 vs 2.5 USD per million): not tested and not controllable from the plugin as far as I read.
- Verification of my phase rules by a second reader: category assignment is by command pattern; a hand check of the 46 "doc" requests shows later `git status`/`ls __scrupuli__` checks counted as doc (they are closing checks, not orientation), which is why I report the strict bound.

## Steering questions

- [now] Do you want one sentence in `author.md` and `explorer.md` (and the skill's brief rules): "no single tool call waits longer than 4 minutes; to wait for a background job, poll with `timeout 240`, and stop any background loop before you hand back"? ESTIMATE: 9% of the wave-4 workers' spend; a probe is cheap (one author brief with and without it).
- [now] Add `Monitor` to the four `tools:` lines, or write in the agent files that a bare `sleep N` is blocked and the allowed form is `until ...; do sleep 5; done` under `timeout`? Which of the two is a plugin decision, not mine.
- [now] Replace `paths: ["__instrumenta__"]` in the four agent files by "the absolute path of this lab's `__instrumenta__`"? Without it a worker may reuse scripts from the plugin source's folder instead of the lab's.
- [later] Is a cold resume of a 300k-token author (USD 0.80) the price of the author-verifier exchange you want, or should the exchange be answered from a fresh worker that reads the claim file (about USD 0.03)? This changes what "independent" and "question the author directly" mean, so it is yours.
- [later] Should the harness `start` line be written from the agent's own name (it is wrong for 4 of 31 starts)?

## Pointers

Scripts (committed at 2761dd4):

- `__instrumenta__/w05c_worker_phases.py@2761dd4`: transcripts to per-worker CSV and detail JSON. Full command, about 10 s each:
  `python3 -I __instrumenta__/w05c_worker_phases.py ~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-4-3417be/c533f1c6-c56e-4c8d-b6ff-e90c3ddea2f4/subagents __reports__/wave-05/explorer-w05-c/w4 /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417be/__statera__/harness.jsonl`
  and for waves 1-3 the same with `.../murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/subagents`, output folder `w123`, no harness argument. No seeds; deterministic.
- `__instrumenta__/w05c_summarize.py@2761dd4`: `python3 -I __instrumenta__/w05c_summarize.py __reports__/wave-05/explorer-w05-c/w4/worker_phase_detail.json > .../w4/summary.md` (pooled shares, cold events, failed calls, outputs, exchange, estimates).
- `__instrumenta__/w05c_phase_table_md.py@2761dd4`: `python3 -I __instrumenta__/w05c_phase_table_md.py .../w4/worker_phase_detail.json > .../w4/phase_table.md`.
- It imports `PRICES` and `message_usd` from `scripts/lab_status.py` (list price, same table as `/lab-status`).

Raw artifacts in `__reports__/wave-05/explorer-w05-c/`:

- `w4/phase_table.md`: the per-worker phase table asked for (15 rows, mutually exclusive phases, USD and seconds, resume-run USD, cold premium, failed calls).
- `w4/worker_phase_table.csv`: one row per worker, requests, USD and seconds by call category (`req_*`, `usd_*`, `s_*`), prefix, fixed start, resume, failed, re-read, carry and lapse columns.
- `w4/summary.md`: every table cited above, as printed. `w4/worker_phase_detail.json`: per request category, USD, tokens, seconds and calls.
- `w123/`: the same four files for the 44 workers of waves 1 to 3 (different plugin versions; wave 1 had no hooks).

One-off commands (not saved as files):

- Re-read counts: a loop over `worker_phase_detail.json` taking file names from Read calls and from Bash commands starting with cat, head, tail, sed -n, grep, nl; slices counted as repeats.
- Start-line name check: compare `name` in `harness.jsonl` `start` events with `name` in `agent-*.meta.json` by agent id (4 of 31 differ: ab1d2a, a03dce, af2465, af9694).
- Final output-token check: over `usage.iterations` records (33 messages): output 52,992, thinking 12,279, content chars 91,676.
- Wall-clock table: first and last SubagentHandback times from the 15 transcripts.
- colgrep path test: two `search` calls in this session, `paths` relative then absolute.
