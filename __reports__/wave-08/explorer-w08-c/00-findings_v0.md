---
type: findings
wave: wave-08
author: explorer-w08-c
date: 2026-10-24
version: v0
decision-required: confirm
---

# Cache lifetime and read-or-delegate as decisions under uncertainty: findings (v0)

In the brief's scope; no departure. Scripts at commit 38d58ff: `__instrumenta__/w08c_pause_model.py@38d58ff`, `__instrumenta__/w08c_tables.py@38d58ff`. Notation: g = start-to-start pause before a request, C = tokens the cache covers, N = new tokens written, r / w5 / w1 = read, 5-minute write, 1-hour write price per Mtok. No new symbol enters `__design__/framing.md`.

## Result

**Prices (CITED).** Anthropic's prompt-caching page gives, against base input: 5-minute write 1.25x, 1-hour write 2x, read 0.1x, with Opus 5.5 and Sonnet 5.5 hits and refreshes at 0.05x; Sonnet 5.5 is 2.00 base, 2.50 / 4.00 writes, 0.10 read; Opus 5.5 is 4.00, 5.00 / 8.00, 0.20 [source: https://platform.claude.com/docs/en/build-with-claude/prompt-caching, fetched 2026-10-24, characters 0-100000 of 162264 read]. The lab's `scripts/lab_status.py` PRICES agree. The page also says the lifetime is measured from the start of the request that wrote or read the entry, and that a longer-TTL entry must come before shorter ones in a prompt. Under these prices a re-write saves (w5 - r) = 2.4 USD/Mtok (Sonnet) and the 1-hour premium costs (w1 - w5) = 1.5 USD/Mtok, so 1 hour pays iff re-written tokens exceed 0.385 of all tokens written (the same for Opus, both being multiples of base).

**Model on the lab's data (ESTIMATE, waves 5-7, authors 14, reproducers 14, explorers 9, PI sessions 3).** Pauses are short and heavy-tailed: median 8-15 s, 0.5-0.7% of worker pauses and 7.5% of PI pauses exceed 300 s, under 0.5% exceed 3,600 s. A 5-minute miss in the data happens exactly when the timed pause exceeds 300 s (calibration, MEASURED, 2,536 timed pauses: 13 of 15 pauses over the TTL missed, none of the 2,521 inside it did). The sign of "1 hour saves money" per type: **PI strongly positive, reproducers and explorers negative, authors a coin flip** (mean net -0.02 USD per life, sd 0.39, P(net > 0) = 5 of 14). Every long pause that matters for workers (7 of 7 author misses, 3 of 3 reproducer misses) follows a `SubagentHandback` call, so the cost lies in one phase, waiting to be resumed.

**Rules choose differently for authors.** Expected value says 5 minutes by 0.02 USD, the token-share rule says 5 minutes (0.372 against a 0.385 threshold), a worst-ratio rule says 5 minutes, and the tail rules (CVaR of regret, minimax regret) say 1 hour. The choice for authors depends on the risk attitude, not on more data of the same kind.

**Per-phase switching is not shown possible.** The API accepts a TTL per breakpoint (CITED, same page), but in Claude Code the only evidence is the agent file's `experimental: cacheTtl: "1h"` (author-level, MEASURED in w07-c7: 17 of 17 requests of B wrote 1-hour only, a resumed B author kept 1-hour at n = 1). It is fixed per dispatch. Even with a switch, the entry that must survive a hand-back pause is written one request before the author calls `SubagentHandback`, when it has not yet decided to hand back (CONJECTURE from the request order; the phase oracle in the table below is therefore an upper bound).

## Table

### 1. Literature, fetched (the arXiv tool returned the abstract; I did not read full texts)

| Topic | Identifier | What it gives for this problem | Label |
|:--|:--|:--|:--|
| Ski rental, competitive ratios 2 (deterministic) and e/(e-1) (randomized); tail risk of the randomized rule | arXiv 2308.05067 (Dinitz, Im, Lavastida, Moseley, Vassilvitskii, "Controlling Tail Risk in Online Ski-Rental") | The randomized rule is optimal in expectation but has more than 37% chance of ratio above 2; bounding the tail changes the optimal rule | CITED |
| Tail risk, two-slope ski rental (after buying one still pays a lower rate) | arXiv 2508.06809 (Cui, Dinitz) | The two-slope form fits a 1-hour cache (a premium on every write after "buying") | CITED |
| Multislope ski rental, randomized, e-competitive | arXiv 0802.2832 (Lotker, Patt-Shamir, Rawitz) | Options with set-up cost and rate; best randomized strategy for additive instances | CITED |
| Risk measure inside the competitive ratio: CVaR-competitive ratio | arXiv 2405.09859 (Christianson, Sun, Low, Wierman) | Optimal CVaR ratio of continuous ski rental 2 - 2^(-Theta(1/(1-delta))); for discrete ski rental with buying cost B a phase transition at delta = 1 - Theta(1/log B), after which the classic deterministic rule is optimal | CITED |
| Distribution-aware ski rental | arXiv 2603.29233 (Kim, Fan); arXiv 2602.21104 (Cui, Dinitz); arXiv 2512.07313 (Kang, Park, Fan, Bayesian discrete) | A predicted distribution of the season length gives a threshold with consistency and robustness bounds; loss O(sqrt(b)) when the prediction is right, O(b log b) when wrong | CITED |
| Learning-augmented, decision-theoretic metrics for ski rental | arXiv 2501.17701 (Angelopoulos, Duerr, Melidi); arXiv 2502.02861 (Shen, Vitercik, Wikum, calibration) | Choose among rules by expected loss across the whole range of prediction error, with a risk term | CITED |
| TTL cache analysis | arXiv 2201.11577 (Elsayed, Rizk); arXiv 2405.04402 (Elsayed, Geyer, Rizk); arXiv 1807.03537 (Goseling, Simeone, soft-TTL, hazard function) | TTL caches with renewal-on-hit; hit probability as a function of TTL and the request-gap law; the hazard function of the gap is the quantity a TTL choice depends on | CITED |
| TTL for agent KV caches (serving side) | arXiv 2511.02230 (Continuum, Li et al.) | Pins the KV cache across tool pauses with a TTL set from the reload cost and the queueing delay; the same pause-then-reuse structure, from the provider side | CITED |
| Prompt caching for agents, empirical | arXiv 2601.06007 (Lumer et al.): 41-80% cost cut, strategy matters more than full-context caching; arXiv 2602.22402 (CMV, trimming break-even within 10 turns); arXiv 2603.04814 (memory against long context, break-even about 10 turns at 100k) | Cost per turn and break-even in turns; none treats the 5-minute against 1-hour TTL as a decision under a pause distribution | CITED |
| Risk-aware LLM routing | arXiv 2606.06924 (DARS); arXiv 2610.22695 (chance-constrained routing) | Same frame for the tier choice: expected cost, variability, a reliability constraint | CITED |
| Karlin, Manasse, McGeoch, Owicki 1994 (the e/(e-1) randomized ski rental); Rockafellar and Uryasev 2000 (CVaR); Savage 1951 (minimax regret); Che et al. 2002 (TTL approximation) | not fetched | Original sources of the rules named above | UNVERIFIED |
| Claude Code settings `ENABLE_PROMPT_CACHING_1H`, `FORCE_PROMPT_CACHING_5M` (session-wide, not per phase) | search-result snippets only (web search 2026-10-24; pages not fetched; one source says a GitHub issue ties it to v2.1.108) | A session-wide switch exists besides the agent frontmatter | UNVERIFIED |

### 2. The pauses, per type (waves 5-7; wave 4 has no model time or gap in `requests.tsv` and is left out)

| Type | Lives | Requests | Pauses | Median g, s | p90 g, s | Over 300 s | Over 3,600 s | Phase holding the long pauses |
|:--|--:|--:|--:|--:|--:|--:|--:|:--|
| author | 14 | 1,138 | 1,124 | 10.3 | 58.3 | 7 (0.6%, 90% CI 0.3-1.1%) | 1 | handback: 22 pauses, median 161 s, 7 over 300 s; all 7 |
| reproducer | 14 | 571 | 557 | 8.0 | 37.5 | 3 (0.5%) | 0 | handback: 8 pauses, 3 over 300 s |
| explorer | 9 | 424 | 415 | 10.0 | 36.9 | 3 (0.7%) | 0 | job (a Bash wait over 60 s): 18 pauses, 3 over 300 s |
| PI | 3 | 443 | 440 | 15.0 | 154.1 | 33 (7.5%) | 2 | resume (turn without tool call, resumed later): 90 pauses, 32 over 300 s |

MEASURED, `__reports__/wave-08/explorer-w08-c/pause_model.json`, `pause_model_pauses.json`. Figure: `fig1_pauses_and_life_net.png` (survival of g per type; one dot per life).

### 3. Net USD per agent life of 1 hour over 5 minutes (positive: 1 hour saves)

| Type | Mean net | sd | 10th / median / 90th | P(net > 0), lives (Wilson 90%) | P(net > 0), gamma-Poisson event model | P(mean net > 0), bootstrap over lives | Mean cache cost per life, 5m / 1h |
|:--|--:|--:|:--|:--|--:|--:|:--|
| author | -0.02 | 0.39 | -0.26 / -0.10 / +0.25 | 5/14 = 0.36 (0.19-0.58) | 0.30 | 0.43 | 2.29 / 2.30 |
| reproducer | -0.09 | 0.10 | -0.16 / -0.13 / +0.08 | 3/14 = 0.21 (0.09-0.43) | 0.19 | 0.00 | 0.65 / 0.74 |
| explorer | -0.13 | 0.19 | -0.27 / -0.21 / +0.11 | 2/9 = 0.22 (0.08-0.50) | 0.22 | 0.03 | 0.87 / 1.01 |
| PI (Opus, 3 sessions) | +14.55 | 15.47 | +2.50 / +13.13 / +27.17 | 2/3 (0.25-0.92) | 0.99 | 0.96 | 27.4 / 12.9 |

ESTIMATE. Formula (stated in the head of `w08c_pause_model.py`): request i costs `r*C_(i-1) + w*N` if g <= T and `w*C_i` if g > T, T = 300 (w5) or 3,600 (w1) s; request 0 costs `w*cache_write`. Check of the model against the recorded cost, observed arm, waves 5-6 (CHECKED): model / recorded USD = 1.002 (authors), 1.003 (reproducers), 1.041 (explorers), 1.039 (PI). Gamma-Poisson model: events (300-3,600 s pauses) per 100 requests 0.53 (author, 90% 0.26-1.00), 0.53, 0.71, 7.0; mean premium per life 0.32 / 0.16 / 0.22 / 1.84 USD against mean saving per event 0.70 / 0.31 / 0.26 / 1.59 USD (`tables.md`, part a). The two P(net > 0) columns for the PI rest on 3 lives (one of them a short wave-7 session with net -0.16) and are not a statement about future PI sessions.

### 4. What each rule chooses (observed lives of each type; `pause_model.json`, key `rules`)

| Rule | author | reproducer | explorer | PI |
|:--|:--|:--|:--|:--|
| Expected value (mean net > 0) | 5m (-0.02) | 5m | 5m | 1h |
| Token-share rule (1h iff re-written / written > 0.385) | 5m (0.372) | 5m (0.21) | 5m (0.20) | 1h (0.85) |
| P(net > 0) > 0.5 | 5m (0.36) | 5m | 5m | 1h (0.67, n = 3) |
| Worst-case cost ratio against the cheaper arm (competitive, per life) | 5m (1.13 against 1.56) | 5m (1.09 against 1.37) | 1h (1.31 against 1.43) | 1h (1.04 against 2.60) |
| Expected ratio (ECR) | 5m (1.03 against 1.21) | 5m | 5m | 1h (1.01 against 1.83) |
| CVaR 0.8 and 0.9 of regret | 1h (0.49 against 0.65 at 0.9) | 5m (0.10 against 0.20) | 5m | 1h |
| Minimax regret in USD | 1h (max 0.72 against 1.04) | 5m (0.11 against 0.25) | 5m (0.29 against 0.30) | 1h (0.16 against 30.7) |
| Ski rental with an in-life switch (simulated, not available) | ratio to the better static arm 1.03 mean, 1.11 max; the randomized e/(e-1) threshold gives the same | 1.03 / 1.16 | 1.03 / 1.15 | 1.06 / 1.11 |

ESTIMATE, n as in table 3. The ratio is on cache cost (reads and writes). For authors the arms differ by 0.4% in mean cost (2.29 against 2.30 USD per life), so the "regret" rules are choosing between a small certain premium (1 hour) and a rare 0.7-1.0 USD loss (5 minutes): this is the whole disagreement. In the switch simulation every threshold x <= 1 times the premium on the current prefix gives the same result, because one miss (2.4 C) already exceeds that premium (1.5 C): the break-even rule reduces to "switch after the first miss", at a cost of that first miss.

### 5. Phase table (summed net USD of 1 hour over 5 minutes by the phase of the pause, all lives of the type)

| Type | loop (about 95% of pauses) | job | handback | resume | oracle that picks 1 hour only in positive phases | best static choice |
|:--|--:|--:|--:|--:|--:|--:|
| author | -3.63 | -0.15 | +3.78 (22 pauses) | -0.01 | +3.78 | 0 (5m) |
| reproducer | -1.92 | -0.06 | +0.91 (8 pauses) | n/a | +0.91 | 0 (5m) |
| explorer | -1.77 | +0.73 (18 pauses) | n/a | n/a | +0.73 | 0 (5m) |
| PI | -2.63 | -0.01 | n/a | +45.80 (90 pauses) | +46.75 | +44.11 (1h) |

ESTIMATE. A switch per phase would be worth 3.78 USD over the 14 authors' lives (0.27 USD per life, 12% of their cache cost), 0.91 over 14 reproducers, 0.73 over 9 explorers; it needs a platform control that was not found and a prediction of the pause one request ahead. Without a switch the only per-phase change is a different agent definition per dispatch.

### 6. The PI reads a large document, or delegates the read (Opus carries it for M more requests; a Sonnet worker reads it and returns a summary)

Frame (ESTIMATE; assumptions marked): read cost `D*(8.00 + 0.20*M)/1e6` USD; delegate cost `D*(2.50 + 0.10*n_w)/1e6 + overhead + S*(8.00 + 0.20*M)/1e6 + brief output`, n_w the worker's requests (median 39), overhead a worker life's whole cache cost resampled from 23 reproducer and explorer lives (median 0.62, p10 0.35, p90 1.23 USD; an upper bound, since it includes work other than the read) [assumption: a delegated read costs about as much as a verifier or explorer life], S = 2,000 summary tokens and 800 brief tokens [assumption: no measure of summary size was taken]; with probability q the summary fails and the PI reads half of the document too [assumption: q is not measured; the table shows 0, 0.2, 0.4].

| D (tokens) | q | P(delegate cheaper) | mean saving read minus delegate, USD (5-95%) | mean read cost, USD |
|--:|--:|--:|:--|--:|
| 10,000 | 0 | 0.01 | -0.62 (-1.31 to -0.12) | 0.25 |
| 25,000 | 0 | 0.27 | -0.34 (-1.29 to +0.41) | 0.64 |
| 25,000 | 0.2 | 0.22 | -0.40 | 0.64 |
| 50,000 | 0 | 0.57 | +0.12 (-1.13 to +1.37) | 1.27 |
| 50,000 | 0.2 | 0.49 | -0.02 | 1.26 |
| 100,000 | 0 | 0.79 | +1.06 (-0.86 to +3.35) | 2.55 |
| 100,000 | 0.4 | 0.63 | +0.53 | 2.52 |
| 200,000 | 0 | 0.91 | +2.97 (-0.42 to +7.39) | 5.15 |
| 200,000 | 0.4 | 0.79 | +1.92 | 5.14 |

M is drawn from the PI's remaining requests at a random point of a session (487 positions, waves 4-6, no compaction seen). Break-even document size at q = 0, median overhead: D* = 181k tokens at M = 10, 87k at M = 30, 32k at M = 100, 17.5k at M = 200, 9.9k at M = 400 (`tables.md`). Large reads the PI actually carried (context jumps over 8k tokens after request 1): 10 in three sessions, 8.3k-14.6k tokens, with 32-146 requests still to come [source: `tables.md` part b]. Figure: `fig2_read_or_delegate.png` (read minus delegate over D and M).

CONJECTURE: the structure is the same as the cache choice (a premium paid now against a carrying cost that grows with the unknown remaining life), but there is no pause distribution to fit; the unknowns are M, the summary failure probability q, and the value of the information a summary loses (not in USD here).

## Worst-fitting case

- Authors, the type the question is about, fit no rule cleanly: the expected value (-0.02 USD per life) is inside noise, the break-even share is 0.372 against 0.385, and the six rules split 4 to 2. Typical (reproducers, explorers) are clear: 5 minutes. The best single life for 1 hour is author-w06-5 (net +1.04, 241 requests, 130 min, two hand-backs of 668 s and 594 s at about 350k tokens); the worst is author-w06-3 (net -0.72; its one pause of 4,187 s is beyond both TTLs, so 1 hour paid the premium on 87 requests for nothing).
- The calibration has two exceptions: PI w6 request 58 (pause 5,203 s, a 1-hour entry should have expired; the cache was read) and explorer-w06-b request 36 (pause 304 s, read). See puzzle 2.
- Against the earlier estimate (w07-c7 c4: +0.87 USD of 47.80 for 19 authors, "sign not determined" after the verifier): 8 of its 14 re-writes are wave-4 authors, whose gaps are not recorded; on waves 5-7 alone the data here give 6 events (300-3,600 s) in 14 lives and a mean of -0.02 per life.

## Not covered

- No wave-4 pauses (not recorded in `requests.tsv`); re-parsing the wave-4 transcripts was not tried. Only 6 of the 15 wave-7 subagents are typed (the authors, matched by request count to `c4_break_even.md`); the other nine are left out.
- n is 3 for the PI (and its three sessions differ by 40x in net), 9 for explorers, 14 for authors and reproducers; the intervals above are Wilson and bootstrap, not guarantees. Pauses are treated as independent across lives and, in the iid pause bootstrap (`pause_model.json`, `iid_pause_life_net`), across requests; the data show them clustered after hand-backs, so the iid P(net > 0) (0.28 for authors) understates the spread.
- Concurrent agents that share a prefix can refresh one another's entries; not modeled (puzzle 2).
- The delegation frame has no measured summary size, summary failure rate or worker overhead for a pure read; only the cost side is data. Value of information, latency and the cost of the PI waiting are not in USD.
- The platform control for a per-phase TTL was not searched beyond `w07-c7` and the docs page (the second half of the prompt-caching page, characters 100,000-162,264, was not read). No runs were made.
- Sonnet 5.5 and Opus 5.5 prices only; no Haiku, fast mode or context above 200k tokens (the PI reaches 516k; no long-context surcharge was checked).

## Steering questions

- [now] Authors sit at the knife-edge. Which attitude should set their TTL, expected cost (5 minutes) or tail loss (1 hour)? The data cannot separate them; the choice is a priority, not a measurement.
- [now] The PI already runs 1-hour, and the data say it should (13-31 USD saved in two of three sessions). Is a wave-8 trial of `cacheTtl: "1h"` on authors worth a probe (the w07-c7 setting is in place), or is the saving (at most about 0.3 USD per life) below the attention it costs?
- [later] Should handback pauses be shortened (the resumer replies earlier) rather than priced? They hold 10 of the 13 worker misses; 22 author hand-backs had a median wait of 161 s.

## Pointers

- `__reports__/wave-08/explorer-w08-c/pause_model.json`, `pause_model_pauses.json`, `pause_model_stdout.txt`: `cd __reports__/wave-08/explorer-w08-c && python3 -I ../../../__instrumenta__/w08c_pause_model.py ../../wave-07/explorer-w07-b/requests.tsv ../../wave-07/author-w07-6/requests_w7.tsv --out pause_model.json > pause_model_stdout.txt` (seed 8, under 5 s).
- `__reports__/wave-08/explorer-w08-c/tables.md`, `fig1_pauses_and_life_net.png`, `fig2_read_or_delegate.png`: `python3 -I ../../../__instrumenta__/w08c_tables.py . ../../wave-07/explorer-w07-b/requests.tsv > tables.md` (same folder; seed 8).
- Inputs: `__reports__/wave-07/explorer-w07-b/requests.tsv`, `__reports__/wave-07/author-w07-6/requests_w7.tsv`; the pause rule follows `w07c7_c4.py` (previous request's model time + tool time + gap), not `w07_ttl_by_type.py` (see puzzle 1).
- Puzzles: `__scrupuli__/wave-08-explorer-w08-c.md`.
