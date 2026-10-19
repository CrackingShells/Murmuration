---
type: findings
wave: wave-02
author: explorer-w02-c
date: 2026-10-19
version: v0
decision-required: confirm
---

# Wave 2, arm B2: M1-M7, the time budget and the ceiling setting (v0)

## Result
B2 ended with a correct `synthesis.md`, an empty `stderr.txt`, no lost worker and no note, notice, stop or deny. By the addendum's rules as written: the **time/USD budget rule stays undecided** (nothing fired; the largest worker used 0.376 of its T and 0.175 of its B); the **ceiling advice is met on the letter, but the run did not need it** (the longest stretch in which the PI was idle was 404 s, under the 600 s ceiling; no worker run was active 10 minutes after any turn end); **no regression** (0 mismatches against brute force for n ≤ 16). All numbers MEASURED with `python3 -I measure_m1_m7.py > output_table.md` (study branch HEAD b396fd1, script uncommitted); n = 1 per arm. A correction to `00-findings_v0.md` is in the last table row.

## Table

### B2, M1 to M7 beside A and B (MEASURED; `output_table.md` has all three arms in every section)
| Item | A | B | B2 | Source (section of `output_table.md`) |
|:--|--:|--:|--:|:--|
| M1 cost-state USD (= result event) | 4.8769 | 6.4737 | 4.6492 | M1 |
| Opus / Sonnet / Haiku USD | 2.21 / 2.62 / 0.05 | 3.11 / 3.31 / 0.05 | 2.61 / 1.98 / 0.06 | M1 |
| `lab_status.py --spend` TOTAL; subagent rows; gap to cost-state Sonnet+Haiku | 4.88; 1.52; 1.15 | 6.47; 2.09; 1.27 | 4.65 exact; 0.91; 1.13 | M1 (same truncation cause: recorded output is 5.6% of exact in B2, 6,182 of 110,265 tokens) |
| M2 worker runs without a deliverable | 1 of 14 (killed at the ceiling) | 0 of 18 | **0 of 9** | M2 |
| M2 turn-limit / budget / refused-Write stops | 0 / n.a. / 0 | 0 / 0 / 0 | 0 / 0 / 0 | M2 |
| other blocked tool calls | 2 | 1 | 1 (author-w01-5, handed back) | M2 |
| hand-back calls; sections saved by the hook | n.a. | 19 of 19 (`delivered`) | 10 of 10 (`delivered`; 9 workers + web-fetch) | M2, Arm B2 |
| M3 explorer reports at `__reports__/wave-NN/<name>/00-findings_v0.md` | none (no convention) | 2 of 2 | 1 of 1; keys exact, exactly the six headings in order; written 18.1 s before the hand-back | M3, Arm B2 |
| M5 user_words entries; with platform text | 2; 0 | 2; 0 | 2; 0 (question stored twice, as in A and B) | M5 |
| M6 synthesis exists; maximum, criterion, N(n) correct for n ≤ 16 | no; (A's files correct) | yes; correct | **yes; correct** | M6 |
| M6 claims (lab_status header) / with verdict / labels | 5 / 5 / 3 THEOREM, 1 CHECKED, 1 THEOREM (gap) | 8 / 6 / 4 THEOREM, 2 CHECKED, 1 cited, 1 superseded | 8 listed = 6 claims + 2 `-proof.md` files read as claims (2 warnings) / 5 / 3 THEOREM, 2 CHECKED, 1 cited | M6 |
| M7 wall time (s) | 1269 | 4540 | **1348** | M7 |
| PI's last record to process exit (s) | 603 | 3 | 3 | M7 |
| M7 worker agent files / runs | 12 / 14 | 14 / 18 | 9 / 9 | M7 |
| runs by role (explorer / author / reproducer / proof-adversary) | 2 / 7 / 1 / 4 | 2 / 9 / 2 / 5 | 1 / 3 / 2 / 3 | M7 |
| first-request prompt tokens, mean, explorer | 23,551 | 13,523 | 13,372 | M7 |
| same, author / reproducer / proof-adversary | 23,896 / 23,687 / 23,717 | 13,779 / 13,299 / 13,382 | 13,876 / 13,365 / 13,512 | M7 |
| B2 minus A at equal role | | | −43%, −42%, −44%, −43% (B2 minus B: −151, +97, +66, +130 tokens) | M7 "B2 by role" |

M6 detail for B2: its synthesis states K = largest k with 2^k ≤ n−k+1 (the same threshold as B's m), M(n) = Σ min(2^k, n−k+1) = 2^{K+1}−2+(n−K)(n−K+1)/2, and the same two-condition criterion. Brute force over all 2^n strings: maximum equal for n ≤ 16, criterion 0 mismatches for n ≤ 14 and n ≤ 16 (CHECKED); its M list (n ≤ 28) and N list (n ≤ 28) agree with brute force for n ≤ 16; top-of-range counts 8 and 40 (n = 4, 9) and 2^{2^{K−1}} at n = 2, 5, 10 agree. Its list for n = 29..48 and A(68) were not rechecked.

### B2, M4 with the time budget (MEASURED; `output_table.md`, "M4 for B2")
| Item | Observed | Source |
|:--|:--|:--|
| harness events | `start` 9, `end` 9; **0 note, 0 stop, 0 halt, 0 deny** | `B2/lab/__statera__/harness.jsonl` |
| T in the log / `Time: min` line in the brief | 20 for the three authors, 15 for the explorer and the verifiers; each equals the PI's `Time: min` line in all 9 runs; USD lines 1.5 to 3 | M4 for B2 |
| `t_frac` at hand-back (log), highest first | 0.376 (author-w01-5, 451 s), 0.277 (explorer-w01-a, 249 s), 0.242, 0.218, 0.161, 0.092, 0.083, 0.069, 0.069 | M4 for B2 |
| USD `frac` at hand-back (log), max | 0.175 (explorer-w01-a); my estimate-output recomputation equals the log to four decimals | M4 for B2 |
| which budget decided (`which`) | time in 5 runs, USD in 4 | M4 for B2 |
| `t_frac` log against my own (first record to hand-back) | within 0.002 (the log counts from SubagentStart) | M4 for B2 |
| start note names both budgets | 9 of 9 murmuration workers | M4 for B2 |
| overshoot past 1.0; handed back after a note | none; not applicable (nothing fired) | M4 for B2 |
| counterfactual: runs in A and B above half of the default T | A: explorer-w02-a 10.1 min (0.50 T, killed). B: explorer-w02-a 49.3 min = **2.46 T** (at the default 20; 3.3 T at the 15 the PI wrote for B2's explorer), author-w02-1 run 2 14.7 min (0.74 T), reproducer-w02-2 9.8 min (0.65 T). B2: none above 0.5 T | M4 for B2 |

### Ceiling: was a background worker still running 10 minutes after a PI turn ended? (MEASURED; "Ceiling" table)
| Arm | PI turn ends | PI background shell tasks | longest idle gaps (turn end to the next PI message or exit) | gaps ≥ 600 s | of those, with a worker run active 600 s later | "stopping them" in stderr |
|:--|--:|--:|:--|--:|--:|:--|
| A | 13 | 0 | 603 s (turn end at 666 s, 1 worker active); 77 s; 46 s | 1 | 1 | yes |
| B | 9 | 4 | 2,952 s (turn end at 595 s, 1 worker active); 527 s (2 workers); 80 s | 1 | 1 | no |
| B2 | 9 | 0 | **404 s** (turn end at 721 s, 1 worker active); 239 s; 64 s | **0** | **0** | no |

How a turn end and a running worker are defined: a PI turn end is a main-thread assistant message with no tool call; a worker run runs from its first record (or the first text message after a hand-back) to its hand-back. For B2 the answer to the question is therefore **no**: in none of its 9 turn ends was a worker run still active 600 s later, because the PI was woken by a worker's hand-back within 404 s each time. The run would have completed under the default ceiling (CONJECTURE: I read "10m after the last turn" as idle time since the PI's last message; the platform's exact rule is not in any file I read). The assumption that the variable was set for B2 comes from the addendum; no file records it.

### The rules of the B2 addendum, applied as written
| Rule | What the data say | Decision |
|:--|:--|:--|
| Time/USD budget: if any note or notice fires, the main rule applies (every worker that gets one hands back; overshoot ≤ 20%). If none fires, the budget stays as inert insurance and the rule stays undecided | None fired: 0 note/stop/halt/deny lines in 9 runs; max t_frac 0.376, max USD frac 0.175. The start note reached 9 of 9 | **UNDECIDED**, as the addendum prescribes. I did not measure the "about 40 ms per tool call" cost |
| Ceiling advice (w02-c7): B2 ends with a `synthesis.md` and no "stopping them" line in stderr | `synthesis.md` exists (evidence table w01-c1 to w01-c6); `stderr.txt` is empty; exit 0 | **MET on the letter**. **Not demonstrated**: the run never had a 10-minute idle gap, so it cannot show that the setting was what saved it |
| No regression: B2's synthesis correct against brute force | formula, closed form, criterion, N(n) for n ≤ 16 all correct (see M6 detail) | **MET** |

### Correction to `00-findings_v0.md` (MEASURED)
| Item | 00 said | Data |
|:--|:--|:--|
| why B's explorer-w02-a could run 49 minutes | B's PI "kept polling" | B's PI ended its turn at 595 s and stayed silent for 2,949 s with one background shell task (`run_in_background`, 3,000 s timeout, "Wait for wave-02 explorer report") running; a task notification woke it at 3,544 s. The process was not stopped. A had no PI background shell task |

## Worst-fitting case
Against "B2 confirms the budget and ceiling changes": the two items B2 was run to see did not show up. The time budget never reached 0.4 of any T (typical run 0.07-0.28 of T; worst, author-w01-5 at 0.376), and the PI never sat idle 10 minutes, so neither the note nor the ceiling setting did any work. The case where a time budget would have bitten is B's explorer-w02-a (49.3 minutes against T = 20), which is arm B, a run without the time budget, so what the mechanism would have done there is a counterfactual.

Against "B2 is the better arm": it is not comparable on time or cost (B2 stopped after wave 1; B ran a second wave; A dispatched one and was cut off), and one defect shows only in B2: its authors saved proof files as `__pondus__/w01-c1-proof.md` and `w01-c5-proof.md`, which `lab_status.py` reads as two claims with no label (header "8 claims, 2 warnings" for 6 real ones).

No prior work is cited.

## Not covered
- Whether the time budget's note and notice work in a real run (nothing fired); the "about 40 ms per tool call" cost.
- Why B's process survived 49 idle minutes. B had a PI background shell task, A had none; I did not establish that this is what the ceiling looks at (CONJECTURE).
- Per-agent exact USD (output is 5.6% recorded in B2); brute force beyond n = 16; B2's proofs; B2's numbers for n = 29..48.
- Whether `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` was set in B2: [assumption: addendum].

## Steering questions
- [now] Accept "undecided, inert insurance" for the budget (USD and time) after two real runs without a firing, or run a B2-type arm with `Budget: USD 0.20` and `Time: min 2` lines so that the note and notice fire on purpose?
- [now] Should the README advice for the ceiling say that a headless run needs it only when the PI can end a turn while a worker has more than 10 minutes to go (A: 603 s idle with the explorer 10.1 minutes in), and that B2 did not need it?
- [later] Should `lab_status.py` skip `__pondus__/*-proof.md`, or the author file say proofs go elsewhere?

## Pointers
- `__reports__/reflective_run/w02/explorer-w02-c/measure_m1_m7.py`: `python3 -I measure_m1_m7.py > output_table.md` (about 4 s). New in this version: arm B2 in every loop, the "Arm B2" section (M3, hand-backs, M4 with `T` and `t_frac`, runs above half of T), the "Ceiling" table (`pi_gaps`, `run_intervals`).
- `__reports__/reflective_run/w02/explorer-w02-c/output_table.md`: all three arms.
- Raw data (read only): `.../scratchpad/w02/expC/B2/{stdout.jsonl,stderr.txt,start.txt,end.txt,exit.txt,lab/__statera__/harness.jsonl,lab/__statera__/synthesis.md}`; transcripts in `~/.claude/projects/*expC-B2-lab`. Command for the claims and spend lines: `python3 scripts/lab_status.py [--spend] --project <B2 lab>`.
- `__scrupuli__/wave-02-explorer-w02-c.md`: puzzles 4 and 5 are new.
