---
type: findings
wave: wave-02
author: explorer-w02-c
date: 2026-10-19
version: v0
decision-required: confirm
---

# Wave 2, arm B3 (budget stress): the four rules, and B3 against B2 on scope (v0)

## Result
Even at `Budget: USD 0.40` and `Time: min 4` in every brief, no B3 worker reached the 0.8 note: the highest deciding fraction was 0.602 (author-w01-1, time), and the harness log holds 7 start and 7 end lines and no note, notice, stop, halt or deny. So **rules 1 (delivery under pressure) and 2 (overshoot) have no workers to judge and stay undecided**; **rule 3 (no anxiety) is met as a rough signal** (7 of 7 runs within a factor of 2 of B2's role rate, all 1.08 to 1.85 times faster); **rule 4 (outcome) is met**: B3's synthesis is correct against brute force. B3 also did less: 7 workers against 9, USD 2.35 against 4.65, 473 s against 1348 s, and no reproducer. All numbers MEASURED by `python3 -I measure_m1_m7.py > output_table.md` (study branch HEAD as of this run; script uncommitted); n = 1 per arm.

## Table

### The four B3 rules, as written in the last addendum of `00-experiment_protocol_v0.md`
| Rule | What the data say | Decision |
|:--|:--|:--|
| 1. Delivery under pressure: every worker that gets a note or notice hands back a deliverable; if one is lost to the budget path, the budget does not land as shipped | 0 workers got a note or notice (0 of 7 runs at or above 0.8 of B or T). All 7 handed back (7 hand-backs) and all 7 have their deliverable in the lab: 2 explorer reports at `__reports__/wave-01/<name>/00-findings_v0.md` (keys and six headings exact), 1 claim head, 4 verdict sections | **UNDECIDED**: nothing to judge; no worker lost anything either |
| 2. Overshoot: deciding fraction at hand-back ≤ 1.2 for at least 80% of the workers that got a notice | 0 workers got a notice; largest deciding fraction 0.602 | **UNDECIDED** (empty set) |
| 3. No anxiety (rough signal): at least 80% of workers that never reached 0.8 show the same tool use per minute as the matching role in B2, within a factor of 2 | All 7 never reached 0.8. Ratio of the run's tool calls per minute to B2's pooled rate for its role: 1.08, 1.10, 1.18, 1.32, 1.55, 1.71, 1.85. 7 of 7 (100%) lie in [0.5, 2] | **MET, as a ROUGH SIGNAL** (see the caveat below) |
| 4. Outcome: the synthesis states the correct maximum; if not, the defaults must not be lowered | Maximum, closed form, criterion and counts all correct (table below) | **MET**: the restriction does not apply. It says little about pressure, because no pressure was applied |
| (last bullet) if B3 cannot be run or measured, the budget stays "inert insurance, undecided" | B3 ran and was measured; nothing fired | the budget **stays inert insurance, undecided**; B3 adds the information that 0.40 USD / 4 min did not fire it either |

Caveat on rule 3: tool calls are distinct `tool_use` ids between a run's first record and its hand-back; runs last 0.56 to 2.39 minutes (B2 comparison runs 1.0 to 7.5 minutes); n = 1 run per arm. The B3 rates are higher in every role, not lower (pooled calls per minute, B3 against B2: explorer 8.18 against 5.79; author 2.51 against 1.62; proof-adversary 8.55 against 6.71; B3 has no reproducer), so there is no sign of workers slowing down or acting less. Short runs have a higher share of setup calls (reading the template and framing), which may account for part of the higher rate: CONJECTURE.

### Fractions at hand-back, B3 (MEASURED; `output_table.md` "Arm B3")
| Worker | deciding fraction | USD fraction (log) | t_frac (log) | which |
|:--|--:|--:|--:|:--|
| author-w01-1 | 0.602 | 0.494 | 0.602 | time |
| explorer-w01-a | 0.393 | 0.393 | 0.295 | USD |
| explorer-w01-b | 0.319 | 0.319 | 0.231 | USD |
| proof-adversary-w01-3 | 0.293 | 0.293 | 0.206 | USD |
| proof-adversary-w01-2 | 0.279 | 0.266 | 0.279 | time |
| proof-adversary-w01-4 | 0.266 | 0.266 | 0.145 | USD |
| proof-adversary-w01-1 | 0.220 | 0.220 | 0.147 | USD |

Output tokens are truncated in the transcripts (2,927 recorded of 42,100 exact Sonnet output tokens, 7%); the hook's estimate (chars/1.3) sums to 45,592, 108% of exact, so the fractions err high rather than low. The exact Sonnet cost of all seven workers together is USD 0.8655 (cost-state), so no single worker can have cost more than that.

### B3's synthesis against brute force (CHECKED, all 2^n strings, n ≤ 16)
| Item | Stated by B3 | Result |
|:--|:--|:--|
| maximum | Σ min(2^k, n−k+1) = 2^K − 2 + (n−K+1)(n−K+2)/2, K = least k with 2^k ≥ n−k+1 | equals brute force for n = 1..16; closed form equals the sum for every n in 1..3000 (0 disagreements) |
| extremal strings | all 2^{K−1} words of length K−1 occur and the n−K+1 windows of length K are pairwise distinct | 0 mismatches over all strings for n ≤ 14 and for n ≤ 16 |
| M list n = 1..20, N list n = 1..20 | 1, 3, 5, ... 166; 2, 2, 6, ... 1344 | equal to brute force for n ≤ 16 (n = 17..20 not rechecked) |
| special lengths | N = 2^{2^{k−1}} at n = 2^k+k−1 | 2, 4, 16 at n = 2, 5, 10: brute force 2, 4, 16 |
| four stated example strings (n = 4, 5, 10, 20) | 0010, 00110, 0001011100, 00000100110101111000 | each has exactly M(n) distinct substrings (8, 12, 42, 166) |

### B3 against B2 on scope (MEASURED)
| Item | B2 | B3 |
|:--|:--|:--|
| worker agent files, explorer / author / reproducer / proof-adversary | 1 / 3 / 2 / 3 (9) | 2 / 1 / 0 / 4 (7) |
| runs in the same order | 1 / 3 / 2 / 3 | 2 / 1 / 0 / 4 |
| worker requests (sum over files) | 68 | 36 |
| claims filed; verified at the standing label | 6 real claim files (lab_status prints 8, two proof files counted); 5 verified: 3 THEOREM, 2 CHECKED; 1 cited (not verified) | 4; 3 verified, all THEOREM; w01-c1 superseded by w01-c4 after a LABEL TOO STRONG verdict; 0 warnings |
| CHECKED claim, reproducer | 2 CHECKED, 2 reproducers | none; the exhaustive search n ≤ 20 sits in an explorer report and its numbers are in the synthesis labelled CHECKED |
| USD (cost-state): total; Opus PI; Sonnet workers | 4.6492; 2.6083; 1.9828 | 2.3470; 1.4784; 0.8655 |
| wall time, `end.txt − start.txt` (s) | 1348 | 473 (PI's last record to exit 4.4 s) |
| first-request prompt tokens, mean, explorer / author / proof-adversary | 13,372 / 13,876 / 13,512 | 13,347 / 13,476 / 13,335 (same lean start as B2, −43 to −44% against A) |
| M5 user_words entries; platform text | 2; 0 | 2; 0 |
| `synthesis.md`; stderr; exit | yes; empty; 0 | yes; empty; 0 |

Did the PI say it scoped work to the budget? In the 7 briefs the only budget lines are the two injected ones (`Budget: USD 0.40`, `Time: min 4`) and the harness sentence about the single note at 80%. One brief (1 of 7) adds: "Rules: no long computations (cap each call at 60 s)". `__statera__/wave-01.md` contains no sentence that says work was narrowed because of the budget; its only budget lines come after the fact: "Workers overran USD 0.40 (author ≈ USD 1.0, self-reported)". So the smaller scope is visible in the dispatch table (one author, no reproducer, one claim superseded) but is not stated as budget-driven: attribution of the smaller scope to the budget is CONJECTURE.

That note is not supported by the measurements: no worker had a deciding fraction above 0.602, and the seven workers together cost USD 0.8655 exact, below the "about USD 1.0" the author reported for itself in its hand-back and puzzle file. The synthesis repeats it ("Workers often went over their USD 0.40 briefs; the author reported about USD 1.0").

## Worst-fitting case
Against "B3 stress-tested the budget": the stress did not reach the mechanism. A budget of 0.40 USD / 4 min is still 1.7 times what the most demanding worker used (0.602 of its deciding budget), so the note, notice and stop have not fired in any of the three runs that carried the hook (B, B2, B3). The typical row (a proof-adversary at 0.22 to 0.29) is far from it; the worst-fitting row is author-w01-1, which ran longest (2.39 min) and reached 0.602 on time.

Against "the smaller scope costs nothing": B3 filed no CHECKED claim and used no reproducer, and the PI's note and the synthesis both state a USD 1.0 overrun that the logs and cost-state contradict, so a reader of the synthesis learns something false about the budget.

No prior work is cited.

## Not covered
- Whether the note, notice or stop work on a real worker: they have not fired in any arm. A direct test needs a brief with a budget below what a worker uses in its first minute (for example `Budget: USD 0.05`, `Time: min 1`).
- Whether tool use per minute drops under pressure that the worker feels: no worker reached 0.8, so the rule compared unpressured runs only.
- The ceiling analysis for B3 (not run; its stderr is empty and it ended 4.4 s after the PI's last record); brute force beyond n = 16; the proofs in B3.
- Per-worker exact USD (output truncated).

## Steering questions
- [now] Close the budget question as "inert insurance, undecided" after three runs with the hook in which it never fired, with the evidence that 0.40 USD / 4 min also did not fire it, or run one arm with a brief small enough to force a note (`Budget: USD 0.05`, `Time: min 1`)?
- [now] The PI's note and the synthesis of B3 state a worker overran its USD 0.40; the measurements say it did not. Should the author and PI files say that a worker cannot know its spend and must not report one?
- [later] Is the narrower scope of B3 (no reproducer, one author) something the PI chose because of the 0.40 line, or chance? The files do not say.

## Pointers
- `__reports__/reflective_run/w02/explorer-w02-c/measure_m1_m7.py`: `python3 -I measure_m1_m7.py > output_table.md` (about 5 s). New in this version: arm B3 in every loop, `b3_section` (harness fractions, deliverables, explorer shape, tool calls per minute, B3's closed form and criterion, scope table, brief and wave-note lines), `tool_calls_by_run`.
- `__reports__/reflective_run/w02/explorer-w02-c/output_table.md`: all four arms; B3 starts at "Arm B3".
- Raw data (read only): `.../scratchpad/w02/expC/B3/{stdout.jsonl,stderr.txt,start.txt,end.txt,exit.txt,lab/__statera__/harness.jsonl,lab/__statera__/synthesis.md,lab/__statera__/wave-01.md,lab/__statera__/handbacks/wave-01-author-w01-1.md}`; transcripts in `~/.claude/projects/*expC-B3-lab`.
- `__scrupuli__/wave-02-explorer-w02-c.md`: puzzle 6 is new.
