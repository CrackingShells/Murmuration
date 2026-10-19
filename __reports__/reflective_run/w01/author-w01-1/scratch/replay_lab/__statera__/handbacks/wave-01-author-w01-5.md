# Hand-backs of wave-01-author-w01-5

Final messages, verbatim, appended by the lab's hook. Read it; never edit it.

## hand-back 1 | 2026-10-19T11:29:03+09:00 | agent_id=a9745700ad92f7cee type=murmuration:author event=PostToolUse bytes=7134 sha256=d4ad55f57ebf

author-w01-5 for w01-c5: the claim head is filed at `__pondus__/w01-c5.md`, label MEASURED. The settings per role are inside it as a labelled CONJECTURE. Nothing in `agents/`, `skills/`, `scripts/` or `hooks/` was touched, and nothing is committed. The Write tool did not refuse any of my files, so no heredoc fallback was needed.

**The hunch, against the data (snapshot 2026-10-19T02:24:30Z, about 11:24 JST):**
- **Three explorers hit the limit, not two.** b, c and d each stopped after exactly 60 turns, so the turn definition matches the limit 3 of 3. d stopped at 02:17:05 and was resumed at 02:17:37. No wave note or report names d as a limit stop.
- **Finished runs against stopped runs.** The three that finished used 46, 49 and 52 turns. The three that stopped needed 62, 62 and 63 in all. No run lands between 52 and 62.
- **Bash.** It was 39 to 61 of each explorer's 55 to 68 tool calls.

**(1) What a stop plus resume cost.** Re-caching and "minutes stranded" are both false for these three.

| | b | c | d |
|:--|--:|--:|--:|
| notice to resume (s) | 7.7 | 10.9 | 31.9 |
| context at the first turn after resume | 301,857 | 281,185 | 296,922 |
| cache write on that turn | 1,798 (0.6%) | 1,256 (0.4%) | 1,853 (0.6%) |
| extra cache write caused by the resume | 0 | 0 | 0 |
| wrap-up turns after resume | 2 | 3 | 2 |
| PI turns spent noticing | 1 | 2 | 1 |
| PI cost, Opus list | 0.06 USD | 0.20 USD | 0.14 USD |
| run total, Sonnet list | 3.06 USD | 2.92 USD | 3.07 USD |

- **Where the cost is.** The wrap-up turns are not extra, since the agent had to write the report anyway. The stop added about 1 to 3% to each run's 12 to 17 minutes of wall time. The PI's cost was 1.8 to 7% of the run, and the instrument can see a cold resume when it happens.
- **When a resume does re-write the context.** Across 12 resumes in all three sessions, those with gaps of 3.2 to 238.9 s are warm (cache write at most 1.5% of context). The five with gaps of 425 to 1,951 s re-write 81 to 87% of it, at 0.33 to 0.51 USD each. That fits the 5-minute TTL of subagent cache writes, which is inferred from the field name and this split, not probed. The PI's main thread uses 1-hour writes.
- **Exposure if the PI had been busy more than 5 minutes.** An ESTIMATE of context x (2.50 - 0.20) / 1e6 gives 0.65 to 0.69 USD per stop. That was never paid in this run.
- **How often the PI is that slow.** In this run, 0 of 9 notices waited over 300 s (max 29 s). In the interactive genesis and design sessions, 15 to 18% did. That includes time the PI spent waiting for the human, so it is an upper bound. At that rate the expected extra is about 0.10 USD per stop.
- **Price basis.** Prices come from the `claude-api` skill's cached table (2026-10-06): Sonnet 5.5 at 2 USD in, 10 out and 0.20 cache read; Opus 5.5 at 4, 20 and 0.20. The cache-write multipliers (1.25 for 5 minutes, 2.0 for 1 hour) are an assumption.
- **Lower bound.** Subagent output tokens are understated, so every USD per run is a lower bound.

**(2) Turn distribution (no-limit analogues, role labels are my reading of descriptions):**

| group | n | turns | median | max |
|:--|--:|:--|--:|--:|
| genesis/design explorer-like | 3 | 31, 35, 103 | 35 | 103 |
| genesis/design author-like | 7 | 46, 60, 65, 78, 85, 87, 89 | 78 | 89 |
| genesis/design verifier-like | 6 | 6, 10, 14, 18, 40, 42 | 16 | 42 |
| pooled Sonnet workers above 6 turns | 18 | | 41 | 103 |
| this run, explorers (final) | 6 | 46, 49, 52, 62, 62, 63 | 57 | 63 |
| this run, authors (6, in flight) | 6 | 19, 23, 24, 30, 31, 35 | | |
| this run, verifiers | 0 | none exist yet | | |

- **Cost per turn grows with context.** The mean turn costs 0.043 USD at turns 1 to 20, 0.070 at 41 to 60, and 0.105 at 61 to 80.
- **Past 60 turns.** Six unlimited runs went past 60. They spent 12 to 57% of their cost after turn 60, and all six ended with a hand-back.

**(3) Proposal, a CONJECTURE (n is small, nothing applied):**

| role | now | proposed | why |
|:--|:--|:--|:--|
| explorer | 60 | 75 | it holds all six explorers of this run with 12 turns to spare; it is not a cost saving, only fewer PI interruptions |
| author | none | 120 | a backstop above the highest worker seen (103); a limit of 60 would have cut 5 of 7 author-like runs |
| reproducer | none | 80 | about twice the highest verifier-like run (42) |
| proof-adversary | none | 80 | same reason as the reproducer |

- **Weakest numbers.** The reproducer and proof-adversary values rest on single-shot reviews, not author exchanges. Re-run the script once this run's verifiers exist.
- **Three one-line habits:**
  1. Append findings to the puzzle file with `cat >>` as you go. All six explorers first wrote a puzzle file or report in their last 1 to 7 turns.
  2. Briefs should say "return the report as your hand-back message". Five of six explorers had a Write to a report file refused, 6 refusals at a turn each.
  3. State the limit and a turn to start handing back in the brief. The agent sees a token counter but no turn counter.

**What would differ if the claim were false:** the first turn after resume would show a cache write near the whole context. The same tables show that shape in the 5 cold resumes (81 to 87%), so the 0.4 to 0.6% for b, c and d is not an artefact of the instrument.

**Open items:**
- Whether `maxTurns` restarts on a resume cannot be tested here. Every resumed segment is 2 or 3 turns long.
- The expensive case is the author being resumed by a verifier question. The verifier works for minutes first, so the author wakes with a cold cache. That costs about 0.69 USD for a 300k-token author. Nothing in the data measures an exchange yet; reproducer-w01-5's first question to me will be the first.
- Separately, 43 to 64% of each explorer's cache writes arrive in about 7 to 13 spikes of more than 8k tokens each. In c they line up one for one with `skill_listing` attachments. In c that is about 0.35 USD of its 2.92 USD, a larger line than any resume.

**Reproduce:**
- **Full** (0.7 s, stdlib, no seeds, read-only): `cd __reports__/reflective_run/w01/author-w01-5 && python3 -I turns_profile.py`. The default `--until` is frozen at the snapshot, so a later re-run gives the same numbers.
- **Quick** (this run only, 0.2 s): the same command with `--quick --out <scratch dir>`.
- **Stops and costs:** `turns_profile.py` loads `scan`, `usage_vec` and `ts` unmodified from explorer-w01-a's `profile_runs.py`.

**Files, all under `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/`:**
- `__pondus__/w01-c5.md`
- `__scrupuli__/wave-01-author-w01-5.md` has 9 puzzles. It starts with a symbols section, and I introduced no new framing symbol.
- In `__reports__/reflective_run/w01/author-w01-5/`:
  - `turns_profile.py`
  - `cw_spikes.py`, `cw_spikes.txt`, `run_log.txt`
  - `stops.csv`, `stop_cost.csv`
  - `resume_vs_gap.csv`
  - `segments.csv`, `pi_notice.csv`, `pi_reaction_latency.csv`
  - `turn_dist.csv`, `runs_turns.csv`
  - `cost_by_turn.csv`, `cost_by_turn_band.csv`, `cost_after_60.csv`
  - `first_write.csv`, `summary.txt`

reproducer-w01-5 will message me.
