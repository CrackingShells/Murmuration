---
type: findings
wave: wave-02
author: explorer-w02-c
date: 2026-10-19
version: v0
decision-required: confirm
---

# Wave 2 phase C, arms A and B: M1-M7 and the pre-registered rules (v0)

## Result
All numbers come from one script, `python3 -I measure_m1_m7.py` (study branch at bb7f2ce, script uncommitted), and are labelled MEASURED unless marked otherwise. Full output: `output_table.md` beside this file. n = 1 per arm.

Against the protocol's rules as written: the **hand-back saver** (18 of 18 worker hand-backs saved, 2 of 2 explorer reports at the convention path) and the **lean-worker context** (B's first request is 42-44% smaller than A's at every role) pass. The **budget hook (w02-c3) cannot be decided**, because no note, stop, halt or deny fired in B: the largest worker used 0.28 of its B. The **outcome rule** is not triggered: B's synthesis is right, A has no synthesis. Both arms' stated maximum formula and extremal-string criterion are correct on every string for n ≤ 16.

## Table

### M1: USD (MEASURED, `output_table.md` section M1)
| Item | A | B | Label | Source |
|:--|--:|--:|:--|:--|
| cost-state totalCostUSD (main transcript, 1 record) | 4.8769 | 6.4737 | MEASURED | `output_table.md` M1 |
| result event `total_cost_usd` (last) | 4.8769 | 6.4737 | MEASURED | same; equal to cost-state in both |
| of which Opus (PI) / Sonnet (workers) / Haiku (web helper), cost-state | 2.2109 / 2.6197 / 0.0464 | 3.1118 / 3.3113 / 0.0506 | MEASURED | same |
| `lab_status.py --spend` TOTAL | 4.88 "exact, all sessions ended" | 6.47 same | MEASURED | `python3 scripts/lab_status.py --spend --project <lab>` |
| `lab_status.py` per-agent rows (sum of subagent rows; main-thread row) | 1.52 (2.21) | 2.09 (3.11) | MEASURED | same |
| sonnet+haiku cost-state minus subagent rows | 1.146 | 1.272 | MEASURED | same |
| of that gap: unrecorded output tokens at $10/M (110,064 / 122,795 tokens) | 1.101 | 1.228 | MEASURED | `output_table.md` M1 |

Do the two agree? The total does, by construction (lab_status takes cost-state). The main-thread row agrees with cost-state Opus (2.21 vs 2.2109; 3.11 vs 3.1118). The per-agent rows agree with my own pricing of the transcripts (1.519 vs 1.52; 2.085 vs 2.09) but sum to 76% (A) and 80% (B) of the total: the transcripts hold 5.3% of the exact Sonnet output tokens (6,896 of 129,721 in B), which explains 1.10 and 1.23 of the gap; Haiku helper calls (0.046, 0.051) are not in the agent rows, and the residual is under 0.01. lab_status marks the rows `+` and says so in its footer. The per-agent figure is therefore a lower bound by about a fifth of the total.

Per-agent USD is the top-11 table in lab_status; I computed all rows (`output_table.md`, last table): A's largest worker is explorer-w01-a at 0.21 recorded / 0.37 with output estimated (chars/1.3); B's is explorer-w02-a at 0.66 / 0.85.

### M2: worker runs without a deliverable (MEASURED)
| Item | A | B | Label | Source |
|:--|:--|:--|:--|:--|
| worker agent files / runs (one run per hand-back, 1 if none) | 12 / 14 | 14 / 18 (+1 built-in `web-fetch`, not counted) | MEASURED | M2, M7 |
| runs without a deliverable | **1**: explorer-w02-a | **0** | MEASURED | M2 table |
| reason | killed at the 10-minute background ceiling (`stderr.txt`: "Background tasks still running 10m after the last turn (subagent "Probe maximiser counts n=2^m+m"); stopping them"); task notification status `stopped` | - | MEASURED | `A/stderr.txt`, `output_table.md` M2 |
| turn-limit stops | 0 (most requests in one file: 15 of 60) | 0 (27 of 150) | MEASURED | M2 table |
| budget stops | n/a (no hook) | 0 | MEASURED | `harness.jsonl`: events are only `start` 18, `end` 18 |
| refused Write/Edit (tool_result error on Write or Edit) | 0 | 0 | MEASURED | M2 table |
| other blocked tool calls | A explorer-w02-a: 2 (a `sleep 420` blocked by the tool guard; one "user doesn't want to proceed" rejection of a Bash call) | reproducer-w02-2: 1 (`sleep 200` blocked); it handed back | MEASURED | M2 table |
| B hand-back calls vs sections saved by the hook | 19 calls (18 murmuration + web-fetch) | 19 sections, all `status=delivered` | MEASURED | M2 second table |
| agent task notifications at the PI | 13 completed, 1 stopped | 19 completed | MEASURED | M2 |

A's lost run: the PI's last record is 3 s after it dispatched explorer-w02-a (666 s of 1269), and the process stayed 603 s more before the ceiling killed the explorer (`output_table.md` M7 timeline and "Last main-thread record" line). Its working files were `code/explore_w02a.c` and `code/explore_w02a_start.c`; no report, no hand-back, no puzzle file.

### M3: explorer deliverables (MEASURED)
| Explorer | Path | Template shape | Label | Source |
|:--|:--|:--|:--|:--|
| B explorer-w01-a | `__reports__/wave-01/explorer-w01-a/00-findings_v0.md`: convention path | six headings present in order, plus one extra h2 ("Sketch of the existence construction ...") between Table and Worst-fitting case; front-matter keys exactly the six of the template, values valid | MEASURED | M3 table |
| B explorer-w02-a | `__reports__/wave-02/explorer-w02-a/00-findings_v0.md`: convention path | exactly the six headings in order (one extra h3); keys and values as the template | MEASURED | M3 table |
| A explorer-w01-a | no report; `data/lit-w01.md` (literature survey), `__scrupuli__/wave-01-explorer-w01-a.md`, and the hand-back text | A's explorer file has no path or template (`__reports__/` does not exist in A's lab) | MEASURED | M3, A second table |
| A explorer-w02-a | nothing (killed) | - | MEASURED | M3 |

### M4: budget notes and stops, arm B only (MEASURED; mostly vacuous)
| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| B per run | from the first user message's `Budget: USD n` line: 3 (explorers, author-w01-2, -3), 2 (other authors, 4 verifiers), 1.5 (3 verifiers); the harness log's `B` matches the line in all 18 runs | MEASURED | M4 table |
| notes / stops / halts / denies fired | **0 / 0 / 0 / 0**; `harness.jsonl` holds only `start` and `end` lines | MEASURED | `B/lab/__statera__/harness.jsonl` |
| fraction of B at hand-back, own pricing from the transcripts, recorded output (lower bound) | max 0.219 (explorer-w02-a, 0.657 USD of 3.0); next 0.114 (reproducer-w02-2); median 0.04 | MEASURED | M4 table |
| the same with output estimated (chars/1.3, the hook's own estimate) | max 0.282 (0.846 USD); next 0.171; matches the harness's `used` to 4 decimals in all 18 runs | MEASURED | M4 table |
| is output truncated? | yes: the worker transcripts hold 6,896 output tokens, 5.3% of the exact 129,721 (cost-state, session level; per-agent exact output exists nowhere); the estimate sums to 144,362, 111% of exact, so it errs towards firing early | MEASURED | M4 truncation line |
| handed back after the note? | not applicable: no note or stop fired. The start note (`Budget: your budget for this run is ...`) reached 14 of 14 murmuration workers | MEASURED | M4 |
| deny: reports and hand-back | both explorers' first tool call naming `findings_v0.md` (a Bash write) precedes their only hand-back by 11.1 s and 10.9 s, so the pre-hand-back check had nothing to deny; 0 deny lines; 0 hook-decision attachments (`hook_blocking_error` etc.) in B's transcripts | MEASURED | M4 |
| counterfactual: A workers against the same B | largest whole-agent-file fraction 0.123 (explorer-w01-a, estimated output); no A worker would have been noted | MEASURED | M4 counterfactual table |

### M5: the user's words (MEASURED)
| Item | A | B | Label | Source |
|:--|:--|:--|:--|:--|
| entries in `__statera__/user_words.md` | 2 | 2 | MEASURED | M5 |
| entries with platform text (tags, `system-reminder`, skill preamble) | 0 | 0 | MEASURED | M5 |
| note | entry 2 starts with entry 1: the question is stored twice (186 and 334 characters), the second with the "you will not hear from me" suffix | | MEASURED | M5 |

### M6: outcome against brute force (MEASURED / CHECKED)
| Item | A | B | Label | Source |
|:--|:--|:--|:--|:--|
| brute-force maximum, all 2^n strings, n = 1..16 | 1, 3, 5, 8, 12, 16, 21, 27, 34, 42, 50, 59, 69, 80, 92, 105 = Σ_{k=1..n} min(2^k, n−k+1) for every n ≤ 16 | same | CHECKED n ≤ 16 | M6 table |
| arm's stated formula | Σ min(2^k, n−k+1) (`__statera__/wave-01.md`, `__pondus__/w01-c1.md`); correct | Σ and the closed form 2^{m+1}−2+(n−m)(n−m+1)/2 with m = largest k with 2^k+k−1 ≤ n (`synthesis.md`); correct for n ≤ 16, and the closed form equals the sum for every n ≤ 3000 | CHECKED | M6 |
| arm's extremal-string criterion on all strings | K = min{k: 2^k ≥ n−k+1}; all (K−1)-words occur and the n−K+1 K-windows are distinct: 0 mismatches for n ≤ 14 and for n ≤ 16 | m as above; all m-words occur and the n−m (m+1)-windows are distinct: 0 mismatches for n ≤ 14 and for n ≤ 16 | CHECKED | M6 table |
| maximiser counts N(n) each states | A's csv n ≤ 31: equal to brute force for n ≤ 16 | `synthesis.md` lists N and M for n = 1..24: equal to brute force for n ≤ 16; N(n) at n = 2, 5, 10 and 1, 4, 9 equal 2, 4, 16 and 2, 8, 40 | CHECKED | M6 |
| `synthesis.md` exists | **no** | yes | MEASURED | `ls __statera__` |
| claims filed (`lab_status.py --project`) | 5, all with a verdict: 3 THEOREM, 1 CHECKED, 1 THEOREM (gap) | 8: 4 THEOREM, 2 CHECKED, 1 `cited (not verified)`, 1 `superseded by w01-c6`; 6 carry a verifier verdict; 0 disputed | MEASURED | M6 claims table |
| open puzzles | 0 | 0 | MEASURED | lab_status |

### M7: time, runs, context (MEASURED)
| Item | A | B | Label | Source |
|:--|--:|--:|:--|:--|
| wall time, `end.txt − start.txt` (cost-state totalDuration) | 1269 s (1267.6) | 4540 s (4540.0) | MEASURED | M7 |
| time from the PI's last record to process exit | 603 s | 3 s | MEASURED | M7 |
| API / tool duration (cost-state) | 1369.6 / 1069.8 s | 1716.2 / 3892.2 s | MEASURED | M7 |
| first wave-2 dispatch to its end | 663 s start; explorer killed at 1268 s | 589 s start; explorer ran 2956 s (49 min), 65% of B's wall time | MEASURED | M7 timeline |
| worker runs by role (explorer / author / reproducer / proof-adversary) | 2 / 7 / 1 / 4 | 2 / 9 / 2 / 5 | MEASURED | M7 |
| agent files by role (same order) | 2 / 5 / 1 / 4 | 2 / 5 / 2 / 5 | MEASURED | M7 |
| first-request prompt tokens (input+cache read+cache write), mean (min-max) | explorer 23,551 (23,406-23,697); author 23,896 (23,733-23,985); reproducer 23,687; proof-adversary 23,717 (23,498-23,834) | explorer 13,523 (13,402-13,644); author 13,779 (13,471-14,177); reproducer 13,299 (13,235-13,364); proof-adversary 13,382 (13,121-13,483) | MEASURED | M7 |
| B minus A at equal role | | explorer −10,028 (−43%); author −10,118 (−42%); reproducer −10,388 (−44%); proof-adversary −10,335 (−44%) | MEASURED | M7 |
| mean brief length (chars), A / B | 1517, 1621, 1300, 1328 | 2462, 2306, 1458, 1502 | MEASURED | M7 |
| `skill_listing` attachment in a worker's transcript | 12 of 12 (32,959 characters in the first) | 0 of 14 (agent files no longer list `Skill`) | MEASURED | M7 |

CONJECTURE (not isolated): the 10,000-token drop is the skill listing (32,959 characters at about 3.3 characters per token is about 10,000 tokens); the briefs are 150-950 characters longer in B, which counts against B. For this user, with 90 skills, the drop is large; for a user with few skills it would be small.

### Decision rules, applied as written in `00-experiment_protocol_v0.md`
| Rule | What the data say | Decision |
|:--|:--|:--|
| w02-c3 budget hook: lands if every worker that gets a note or a stop hands back a deliverable (M2 lost to the budget mechanism = 0) and overshoot past 1.0 B ≤ 20%; does not land if any worker loses its deliverable to the deny or stop path | No worker received a note or a stop; no deny; no worker lost a deliverable to the mechanism (M2 = 0 in B); no overshoot (max 0.28 B). The conditions hold only vacuously, because the mechanism was never exercised at real B. | **CANNOT BE DECIDED** by this experiment. On the letter, no failure was observed; on substance the evidence is the phase-A probe cells, not this run. The only live observations: the start note was delivered to 14 of 14 workers, and no B transcript holds a hook error or block attachment. |
| w02-c3 hand-back saver: lands if every explorer in B has a report at the convention path (M3) and every hand-back is saved | 2 of 2 explorers at the convention path; 19 of 19 hand-back calls saved (18 of 18 murmuration), all `delivered` | **LANDS** on this data |
| w02-c3 deny-once: no deny loops | 0 denies; both explorers had written the report before handing back | **NOT EXERCISED**: "no deny loops" holds vacuously; the deny path itself did not run |
| w02-c4: lands if B's explorer reports are at the convention path in the template's shape (M3) and B's worker start context is smaller than A's at equal role | Path: 2 of 2. Shape: keys exact in 2 of 2; headings exact in 1 of 2, in order with one extra h2 in the other. Start context smaller at every role (−42% to −44%, n = 2, 5, 2, 5 against 2, 5, 1, 4) | **LANDS** if "shape" means the six headings in order; one report has an extra h2 and would fail an exact-heading check |
| No regression on the outcome: if B's synthesis is wrong where A's is right, nothing lands | B's synthesis is correct (n ≤ 16 checked, closed form to 3000); A wrote no synthesis | **NOT TRIGGERED** |
| M1 difference | B costs 6.47 against 4.88 (+33%) and did a second wave (explorer 0.85, author 0.48, reproducer 0.26 estimated) plus 3 more claims | reported; per the protocol it does not decide at n = 1 |
| w02-c1 observed | M1 comes out of the new reader as exact cost-state in both arms (4.88, 6.47 "exact, all sessions ended") | observed, works |
| w02-c2 observed | M5 clean in both arms (0 of 2 entries with platform text each) | observed, works; the question is stored twice |

## Worst-fitting case
Against the story "B's mechanism works": the budget hook is the item the experiment was meant to test and the one it did not test. Typical case: runs end at 0.01-0.17 of B; worst case: explorer-w02-a, 0.22-0.28 of B, still 3.5 times short of the 0.8 note. B values of 1.5-3 USD sit 3.5 to 150 times above what these workers spend per run (median 0.04 of B, recorded output).

Against the story "the candidate is better": B costs a third more and took 3.6 times as long (4540 against 1269 s), and its explorer-w01-a report has a seventh h2 against the template's six. The wall-time gap is the second wave: A's PI ended its turn 3 s after dispatching its wave-2 explorer and the process waited out the 10-minute ceiling; B's PI kept polling with background shell commands for the 49-minute explorer. No text in the diffs of `research-pi.md` (empty), `SKILL.md`, `briefs.md` or `waves.md` concerns waiting for workers, so I attribute it to PI behaviour at n = 1: CONJECTURE.

For prior work: none cited.

## Not covered
- Whether the budget note, stop and halt work in a real run: they did not fire (see steering question).
- Per-agent exact USD: not available from any file; lab_status per-agent rows are lower bounds (output tokens truncated to 5.3% of exact in B). Only the session total and per-model totals are exact.
- A's extremal-string and formula statements come from its wave note, claim files and proof file, not from a synthesis (there is none); I did not read the proofs.
- n = 17 and above: brute force stopped at 16; the table values to 24 (B) or 31 (A) beyond that are the arms' own exhaustive searches, not rechecked here. B's maximiser counts at n = 18, 35 (704, 188416) and the top-of-range formula were checked only at n = 1, 4, 9.
- Why B's explorer-w02-a ran 49 minutes (it ran its own long enumerations with `sleep` waits); not a plugin matter, not analysed.

## Steering questions
- [now] Accept the phase-A probe cells as the w02-c3 evidence for the note and stop, or run one more B-arm run in which the PI writes `Budget: USD 0.10` to 0.30 in the briefs so that the note and stop fire on real workers (the hook already reads that line)?
- [now] Is "template shape" for w02-c4 the six headings in order (B passes 2 of 2) or exactly six h2 (B passes 1 of 2)?
- [later] The lean-worker saving of about 10,000 tokens per worker is the skill listing of a 90-skill user; do you want it reported as user-specific rather than as a property of the plugin?

## Pointers
- `__reports__/reflective_run/w02/explorer-w02-c/measure_m1_m7.py`: the script; `python3 -I measure_m1_m7.py > output_table.md` (about 3 s; the brute force for n ≤ 16 and all transcripts). Reads the arms in `.../scratchpad/w02/expC/{A,B}` and the transcripts in `~/.claude/projects/*expC-{A,B}-lab`; imports `PRICES` and `message_usd` from `scripts/lab_status.py` of this worktree (identical to B's plugin copy).
- `__reports__/reflective_run/w02/explorer-w02-c/output_table.md`: every table above.
- Also run: `python3 scripts/lab_status.py --spend --project <A or B lab>` and `python3 scripts/lab_status.py --project <lab>` (quoted in M1 and M6).
- Raw data (read only, not copied): `.../w02/expC/A/{stdout.jsonl,stderr.txt,lab}`, `.../w02/expC/B/{stdout.jsonl,lab/__statera__/harness.jsonl,lab/__statera__/handbacks}`, the two transcript folders named in the brief.
- `__scrupuli__/wave-02-explorer-w02-c.md`: my puzzles.
