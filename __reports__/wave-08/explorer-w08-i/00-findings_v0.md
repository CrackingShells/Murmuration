---
type: findings
wave: wave-08
author: explorer-w08-i
date: 2026-10-24
version: v0
decision-required: confirm
---

# What the lab's labels are worth and what verification buys, waves 1-8: findings (v0)

Brief left in one place: the brief names `__instrumenta__/w07_ttl_by_type.py` as the script behind w07-c7's +USD 0.87; it is not (row 4 below). All scripts are `__instrumenta__/w08i_*.py@465c229` (uncommitted when this was written; committed with this report).

## Result
Of 76 claims with a verdict, 38 (50%) were SUPPORTED the first time, 25 OVERSTATED and 13 ESCALATE; every one of the 77 verdict sections is a reproducer's (no proof-adversary was ever dispatched) [source: `claims_verdicts.tsv`, MEASURED]. Verification cost USD 30.45 in 50 named reproducer rows plus about 4.17 for wave 7's unnamed ones (about 8% of the USD 411.93 total, 1/3 of the author cost per claim) [ESTIMATE, `agent_spend.tsv`]. I found 9 later flags on standing claims or synthesis lines (`corrections_table.md`; 9 of the 47 standing claims, 19%, floor); the sharpest is that the budget selftest failed at two merges, wave 7's 5e16a53 and wave 8's 15d4c94, both because two branches were each tested alone: 2 of 15 landing states I re-ran failed their own selftests, and all 7 selftests take about 50 s (budget alone 2.6 s) [source: `selftest_history.tsv`, CHECKED at 15 commits].

## Table
Verdicts by wave (final verdict of each verifier section; wave = the claim's wave). [source: `python3 -I __instrumenta__/w08i_claims_table.py --summary`, MEASURED]

| wave | SUPPORTED | OVERSTATED | ESCALATE | sections | first-pass SUPPORTED claims |
|:--|--:|--:|--:|--:|:--|
| w01 | 3 | 7 | 4 | 14 | 3 of 14 |
| w02 | 5 | 4 | 1 | 10 | 6 of 10 |
| w03 | 1 | 0 | 1 | 2 | 1 of 2 |
| w04 | 6 | 3 | 3 | 12 | 5 of 12 |
| w05 | 7 | 2 | 1 | 10 | 7 of 10 |
| w06 | 9 | 5 | 1 | 15 | 7 of 14 (+ revisions) |
| w07 | 5 | 2 | 1 | 8 | 5 of 8 |
| w08 | 4 | 1 | 1 | 6 (+ w08-c2 unverified, by PI decision) | 4 of 6 |
| all | 40 | 24 | 13 | 77 (+1 not verified) | 38 of 76 |

(The sections column sums 77; the summary script prints 78 because it counts the one unverified claim. "First-pass" = first verdict of the first section of a claim; a claim superseded after OVERSTATED counts as not first-pass.)

Other counts, all MEASURED from `claims_verdicts.tsv` and `lab_status.py` unless marked:
| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Verifier types | 77 of 77 sections are reproducers; 0 proof-adversary; 0 THEOREM labels | MEASURED | `claims_verdicts.tsv` col vtype |
| Authors | 13 sections are on PI-authored claims: 6 SUPPORTED, 7 OVERSTATED (54% not SUPPORTED); 64 sections on other authors' claims: 34 SUPPORTED, 17 OVERSTATED, 13 ESCALATE (47% not SUPPORTED) | MEASURED | `claims_verdicts.tsv` col author |
| Current state of 77 claims | MEASURED 33, CHECKED 2, CONJECTURE 3, below-label 10, escalated 9, superseded 19, unverified 1 | MEASURED | `python3 scripts/lab_status.py` (counted by script) |
| The exchange changed a verdict | 3 sections show two different verdicts with `changed_by:` (w02-c4 SUPPORTED to OVERSTATED; w04-c6 OVERSTATED to SUPPORTED; w06-c13 OVERSTATED, OVERSTATED, SUPPORTED); `changed_by:` occurs in 10 of 77 sections; 4 more sections repeat the same verdict in a revision (w06-c4, w06-c9, w08-c6, w08-c7) | MEASURED | `claims_verdicts.tsv` cols verdict_sequence, changed_by |
| SUPPORTED after the verifier found a defect that was then fixed | 15 of 40 SUPPORTED sections say so in their `reason:` (w01-c3, w01-c14, w02-c6, w03-c1, w04-c1, w04-c6, w04-c8, w05-c4, w05-c5, w06-c7, w06-c9, w06-c13, w07-c4, w08-c4, w08-c6), by my hand reading | CONJECTURE (hand count of reason lines) | `__pondus__/*.md` |
| ESCALATE | 13 sections, all in 13 distinct claims; 8 of them say in their reason that the evidence alone gives OVERSTATED; in every one the author or the verifier wants the statement changed, which the rules send to the PI. 9 were decided by PI restatement in place, 4 by a superseding claim (w01-c4, w01-c5, w06-c3, w08-c1) which was verified again | MEASURED (counts), CONJECTURE (reading of reasons) | `__pondus__/<claim>.md` reason lines; wave notes |
| PI against a verifier | none found against a verdict's reading; one landing against a registered threshold (w06-c9: outputs SUPPORTED) and one by decision without a verifier (w08-c2, USD 2-3 to verify a change it would not land) | CONJECTURE (notes read, not every line) | `__statera__/wave-06.md:228-237`, `wave-08.md:130` |
| Claims whose current text is an unverified PI restatement | 11 (the 9 decided ESCALATEs and w02-c7, w02-c8) | MEASURED | `corrections_table.md` last section |
| lab_status says `escalated: PI decides` after the PI decided | 9 claims (12% of 77) | MEASURED | `python3 scripts/lab_status.py`; wave notes |
| Synthesis lines without a claim | 26 of 37 "Still open" rows carry no claim id (they are explorer or PI readings) | MEASURED | `__statera__/synthesis.md` lines 590-625 |
| Labels in notes above the current label | none found: every line naming one claim next to a label word that differs from lab_status states the weaker state in the same row (synthesis lines 44, 49, 51, 303, 465, 513-518); the exceptions are w05-c1 and w02-c10 stated as "MEASURED, restated/by PI decision" while lab_status says escalated | MEASURED (script), CONJECTURE (my reading of the 14 synthesis hits) | `label_vs_note.tsv` |

Spend, USD at list price from the agent rows of `lab_status.py` [ESTIMATE; the unit is a verifier's own transcript, so the author's exchange time is in the author's row]:
| Group | USD | Rows | Source |
|:--|--:|--:|:--|
| Named reproducers, waves 1-6, 8 | 30.45 | 50 | `verification_cost.md` |
| Unnamed `murmuration:reproducer` (all of wave 7 and perhaps some other waves) | 4.17 | 1 | `agent_spend.tsv` |
| Authors (named 99.20 + unnamed 10.17) | 109.4 | 31 rows | same |
| Explorers (named 42.9 + unnamed 7.32) | 50.2 | 29 rows | same |
| PI (3 main threads) | 153.6 | 3 | same |
| Lab total (cost-state where ended) | 411.93 | | `lab_status.py` |
| Per verified claim (named rows) | 0.45 (30.45 / 68 claims) | | `verification_cost.md` |
| Per non-SUPPORTED section (named rows) | 0.90 (30.45 / 34) | | `verification_cost.md` |
| Per author claim (authors / 77) | 1.42 | | |

Wave 8 harness `end` lines, last per verifier (`used`, session list price with chars/1.3 output floor): reproducer-w08-1 0.99, reproducer-w08-3 0.79, reproducer-w08-6 0.42 (two end lines, resumed); lab_status rows 0.89, 0.74, 0.37. `harness.jsonl` holds wave 8 only (53 lines), so waves 1-7 verifier cost is from transcripts [source: `__statera__/harness.jsonl`, MEASURED].

What the later flags show (details in `corrections_table.md`; kinds counted by me):
| Kind | Cases | Caught by a verifier at the time? (CONJECTURE) | Check and cost |
|:--|:--|:--|:--|
| Step nobody ran | selftest at merges 5e16a53 (w07-c3) and 15d4c94 (w08-c4); the arms of w05-c1 not diffed against main | no, and in neither case was the step in a brief or protocol until w08-c8 | `--selftest` of 7 scripts on the merged tree, 50 s, USD 0; `git diff` of exports, seconds |
| Threshold | w04-c5, w05-c4, w06-c9 | verifiers applied the rule as written | measure the floor first, USD 1 |
| Confound (load, hooks in arms) | w05-c1, w06-c14 vs w07-c3, w08 ceiling | one of three | `loadavg` beside each pair, minutes |
| Data gap | w07-c7 wave-4 pauses | partly (flagged, sign withdrawn) | re-parse timestamps, USD 0.5-1 |
| Script bug | `w07_ttl_by_type.py` | no verifier existed | reproducer, USD 0.4-0.9 |
| Scope wording | synthesis row 29 | no verifier existed | claim id on the row |

## Worst-fitting case
The story "verification mostly catches over-wide titles, and what slips through is a step nobody ran" fits worst at **w07-c7**. The brief's reading (a verified thing wrong) does not hold for it: its verifier had already seen the blank wave-4 pauses, recomputed the net at four bounds (+0.87, +0.45, -0.60, -6.70) and a bootstrap (P(net <= 0) = 0.34), and the author withdrew the sign; the PI landed it as "money undetermined" [source: `__pondus__/w07-c7.md` verifier section; `__statera__/wave-07.md:353-366`]. The later estimate (-0.02 per life) is inside that interval. The defect the brief names (misaligned `tool_s`) sits in a PI addendum nobody verified, not in this claim's script (`w07c7_c4.py` line 28 uses the previous row's `model_s + tool_s`). What does fit worst is the claim file: its title still reads "+USD 0.87 ... nets only slightly positive" and the file carries no note of the decision, so a human who opens it, or reads `lab_status` ("escalated: PI decides"), meets a stale statement.
Second worst: 8 of 13 ESCALATEs would be OVERSTATED on evidence alone, so ESCALATE is partly a rule artifact ("author agrees to restate"), not a different kind of failure; counting it as "verifier caught an error" is right, counting it as "PI overrode" is wrong (0 overrides found).

## Not covered
- Later corrections I could not find: my search is textual (claim ids, correction words, wave notes, puzzles, synthesis). A wrong claim nobody revisited is invisible here; the 9 standing claims with a later flag (w08-c4, w07-c3, w07-c7, w05-c1, w04-c5, w05-c4, w06-c9, w06-c14, w07-c6) are 9 of 47 standing (38 SUPPORTED + 9 escalated and landed), a floor of 19% [CONJECTURE, not a rate: the flags differ in weight, from a failed selftest to a stale threshold].
- Verifier cost of waves 3-5 explorers, wave-7 verifiers by name, the author's exchange time and the PI's decision time are not separable; the PI is 37% of spend and its verification share is not measured.
- What a proof-adversary would have bought: none was dispatched; no claim is a THEOREM.
- I did not re-run any claim's measurement; the selftest history is the only re-run. Selftests ran at 15 commits only (the 13 merge or landing commits of waves 1-8 that touch scripts, hooks or bin, plus d0ef374 and the 15d4c94 rerun); the other 65 commits touching those folders were not run.
- No money value for a wrong landing: a failed selftest at merge cost minutes (fixed 2 and 1 minutes later) and no hook broke (wave-07.md:342), so the USD cost of the miss is about zero here.

## Steering questions
- [now] Should `lab_status.py` learn a PI decision (a line in the claim file or the wave note that clears "escalated: PI decides" with the decided state)? It would clear 9 stale entries.
- [now] Should a statement the PI restates in place be re-verified by a short reproducer (USD 0.4-0.9 each, 11 claims = about USD 5-10)? or kept as is because the figures are the verifier's own?
- [now] Should every synthesis row that asks the human to act on a number carry a claim id (26 of 37 do not)?

## Pointers
All in `__reports__/wave-08/explorer-w08-i/` unless a path says otherwise; commands from the lab root.
- `claims_verdicts.tsv`: `python3 -I __instrumenta__/w08i_claims_table.py`; summary `... --summary`.
- `later_refs.tsv`: `python3 -I __instrumenta__/w08i_later_refs.py` (97 lines; read the MEASURED/CHECKED/ESCALATE rows by hand).
- `label_vs_note.tsv`: `python3 -I __instrumenta__/w08i_label_vs_note.py` (41 data lines).
- `agent_spend.tsv`: `python3 -I __instrumenta__/w08i_agent_spend.py`; `verification_cost.md`: `python3 -I __instrumenta__/w08i_verification_cost.py claims_verdicts.tsv agent_spend.tsv`.
- `selftest_history.tsv`: `python3 -I __instrumenta__/w08i_selftest_history.py <scratch> <commits>` (about 70 s per commit; run for 9d9d7ae 3b0448b 710228b 5e16a53 ad2440a 33582f1 47d2cd2 4dd4734 fed7a08 4c675ec 84ff038 544c9e3 b23c5c8, then 15d4c94 d0ef374). Rows with exit 1: 5e16a53 budget.py and 15d4c94 budget.py. The 15d4c94 and d0ef374 rows were run first, alone, and appended.
- `corrections_table.md`: the nine flagged items by hand, with sources.
