---
type: findings
wave: wave-08
author: explorer-w08-k
date: 2026-10-24
version: v0
decision-required: confirm
---

# Decision sections for five escalated claims without a recorded label: findings (v0)

Within the brief (no leaving). One note on method: `__pondus__/` heads of w03-c2, w04-c4, w04-c7, w04-c10 already carry the PI's in-place restatement (a `restated:` line, new title), so "what the head says" and "what the verifier's result supports" coincide for them; only w07-c7's head still carries the pre-decision wording.

## Result
For all five, the verifier's own recount carries MEASURED for the restated wording, so I propose `restated at MEASURED` for each (CONJECTURE: my reading of what the evidence carries). Each is applied by `scripts/lab_status.py` on a scratch copy and reads `MEASURED (PI decided: restated, not re-verified)`, with no new warning (CHECKED, 83 claim files; the 6 warnings are the same 6 as on the real tree) [source: `__reports__/wave-08/explorer-w08-k/lab_status_scratch.txt`]. Two of the five need a caveat that the PI may want to weigh: w03-c2 (the narrowed `.ignore` block was tested only by the author) and w07-c7 (the label is MEASURED for c1 to c3 only; the money, c4, is an undetermined ESTIMATE).

## Table
| Claim | Verifier's independent result supports (CONJECTURE, my reading) | PI decided where (quote) | Proposed | Scratch `lab_status.py` | Source |
|:--|:--|:--|:--|:--|:--|
| w03-c2 | counts of 40 workers and of the 3-worker lab reproduced; own same-question control (USD 1.50): scripts under `__instrumenta__/` 3 of 3 vs 0 of 4, inline Python 1 vs 0 (no effect); Grep honours `.ignore` (wider block); fold-in tested. At most OVERSTATED for the first head | `__statera__/wave-03.md:136` "PI decision on the ESCALATE of w03-c2 ... The head is restated in place to the verifier's figures" | restated at MEASURED, with caveat | MEASURED (PI decided: restated, not re-verified) | `__pondus__/w03-c2.md` verdict reproducer-w03-2 |
| w04-c4 | s1, s3, s4, strict reuse 7 of 15 recounted from raw runs with own extractor; "ran or adapted" is 11 of 15, not 14; rule INCONCLUSIVE; quick run matched | `__statera__/wave-04.md:223` "the head is restated in place to the verifier's figures" | restated at MEASURED | same | `__pondus__/w04-c4.md` |
| w04-c7 | every table figure and the rule's outcome recounted from 12 raw runs; precondition probe 3.76; three wordings do not stand (near fit tests finding, version 2.1.302, causal reading of Q's s3); "SUPPORTED once restated at ..." | `__statera__/wave-04.md:236` "the head is restated in place to the verifier's statement" | restated at MEASURED | same | `__pondus__/w04-c7.md` |
| w04-c10 | s7 4 of 6, fit 3 of 3, near fit 1 of 3, positions 369 and 315, 0 colgrep calls re-derived from 6 raw runs; the unqualified "finding works" would be OVERSTATED | `__statera__/wave-04.md:245` "title and scope restated in place (3a5429a) to 'at the rule's edge'" | restated at MEASURED | same | `__pondus__/w04-c10.md` |
| w07-c7 | c1 recomputed from 6 raw transcripts (B 17 of 17 1-hour, A 16 of 16 5-minute); c2 rerun, A and B apart, n = 1 each (A 42.1%, B 100%); resumed B author keeps 1-hour (n = 1); c3 only for the 6-tool 12k headless author; c4 sign not determined (sensitivities below the table) | `__statera__/wave-07.md:363` "PI decision: w07-c7 stands as the verifier restates it" | restated at MEASURED, scope c1 to c3 | same | `__pondus__/w07-c7.md`; `__reports__/wave-08/explorer-w08-c/00-findings_v0.md` |

(w07-c7 c4 sensitivities in the verifier's section: +0.87 at 300 s, +0.45 at 330 s, -0.60 at 360 s, -6.70 at 600 s; bootstrap P(net <= 0) = 0.34.)

## Per claim

### w03-c2
- Verifier (reproducer-w03-2, ESCALATE): all counts reproduce; "supports OVERSTATED at most"; the author accepted its restatement and asked the PI to decide.
- PI: `__statera__/wave-03.md:136` and the five bullets under it; the head was restated in place (`restated:` line in the head).
- Choosing the label: the head's `.ignore` clause is about the narrowed folder-only block. The verifier tested a wider block (`*.json`, `*.txt`, `*.log`, `raw/`, `derived/`), and its Grep results are about that; the narrowed block's Grep result (6 of 10 files) is the author's one probe (`ignore_grep_probe.json`). The mechanism (Grep honours `.ignore`) is the verifier's. I still propose MEASURED because the scope clause says "one Grep probe of the final `.ignore`"; if the PI wants the label to follow only what a second party ran, no vocabulary label sits between MEASURED and withdrawn for one clause, so a narrower statement (drop the Grep clause) is the other option.
```markdown
## decision: research-pi

decision: restated at MEASURED
ref: __statera__/wave-03.md:136
statement: With the build, 3 of 3 helper scripts of one headless lab were saved under `__instrumenta__/` (0 of 4 in a same-question control at 7f98b1f, n = 1 per arm; inline Python 0 against 1, no effect shown), and a lab's folder-only `.ignore` keeps hand-backs, `raw/`, `runs/` and `generated/` out of the colgrep index and of Grep without a path; search and reuse were not exercised.
reason: The verifier's counts and probes reproduced and its control gives the 3-of-3 against 0-of-4 figure; the narrowed block's Grep result (6 of 10 files returned) is the author's one probe, with the verifier's Grep probes on the wider block showing the same mechanism.
```

### w04-c4
- Verifier (reproducer-w04-4, ESCALATE): s1, s3, s4, cost, strict reuse (7 of 15) and duplicates reproduce; the author's "ran or adapted in 14 of 15" is 11 of 15 after recoding; the verifier gave a suggested restatement (strict first). The PI: `__statera__/wave-04.md:223`.
- The head already carries a restated title ("reused ... in 7 of 15; the other 8 adapted by copy (4), wrote new code after a header (3) or with no search (1)"). I quote the verifier's own suggested wording in `statement:`, which is shorter and omits the arm X and C exploratory numbers.
```markdown
## decision: research-pi

decision: restated at MEASURED
ref: __statera__/wave-04.md:223
statement: In a lab of 46 scripts, author workers listed `__instrumenta__/` before writing in 14 of 15 runs (colgrep `search` 0 of 15) and reused an existing script as is or in place in 7 of 15; 4 more adapted a copy, 3 wrote new code after seeing only a header, 1 wrote without looking; the E3 rule is INCONCLUSIVE under the strict reading.
reason: The verifier recounted s1, s3, s4 and the strict count from the raw runs with its own extractor; its recoding gives 11 of 15 "ran or adapted", not 14 of 15.
```

### w04-c7
- Verifier (reproducer-w04-7, ESCALATE): "the claim, as it stands, would be OVERSTATED in those three places and SUPPORTED once restated at 'at 429 scripts with both targets in the first 10 names, a cut listing was used, colgrep 1 of 6 (P) and 0 of 6 (Q), and Q's untested cause'". The PI: `__statera__/wave-04.md:236`.
```markdown
## decision: research-pi

decision: restated at MEASURED
ref: __statera__/wave-04.md:236
statement: At 429 scripts with both targets among the first 10 names, a cut listing sufficed; colgrep `search` was used in 1 of 6 runs with P and 0 of 6 with Q, strict reuse was 3 of 6 per arm (all on the fit task), Q is not proposed, and why Q did not change behaviour is untested.
reason: The verifier recounted every table figure and the rule's outcome from the 12 raw runs and wrote that the claim is SUPPORTED once restated at this wording; the near-fit-tests-finding sentence and version 2.1.302 are dropped.
```

### w04-c10
- Verifier (reproducer-w04-10, ESCALATE): data check out; "absent a restatement I would call the current title OVERSTATED". The PI: `__statera__/wave-04.md:245` (title restated in place at 3a5429a). The verifier did not read the restated head; hence "not re-verified" is accurate.
```markdown
## decision: research-pi

decision: restated at MEASURED
ref: __statera__/wave-04.md:245
statement: With both target scripts past position 300 of a 429-file listing, workers opened the target in 4 of 6 runs, at the rule's edge (the lowest passing count): the fit script 3 of 3, the near fit 1 of 3 (the pass rests on one run, pt2r2); found by `ls | grep -i`, colgrep `search` 0 of 6.
reason: The verifier re-read all 6 raw runs and confirmed each count; it called only the unqualified "finding works" OVERSTATED, and the head now carries the edge.
```

### w07-c7
- Verifier (reproducer-w07-6, ESCALATE): c1 and c2 reproduce on non-concurrent runs; the author withdrew "nets slightly positive" and the verifier found the sign not determined; c3 holds for the 6-tool headless author only. The PI: `__statera__/wave-07.md:363` "w07-c7 stands as the verifier restates it". The head's title still says "nets only slightly positive" and its label is compound; the tool shows it flat as MEASURED.
- Later evidence: explorer-w08-c recomputed (own model, not `w07c7_c4.py`) a mean of -0.02 USD per life for authors on waves 5 to 7, 6 events in 14 lives, 8 of the claim's 14 re-writes are wave-4 authors with blank gaps [source: `__reports__/wave-08/explorer-w08-c/00-findings_v0.md:115`]. That agrees with "sign not determined" and does not touch c1 to c3. Puzzle 2 of explorer-w08-i: its correction is that the misaligned column is in the PI addendum `w07_ttl_by_type.py`, not in w07-c7's own script; so the decision does not go stale.
- Why `restated` and not `stands`: the head wording that the decision withdraws is still the title; a `statement:` line carries the verifier's version. MEASURED is stated for c1 to c3 in the statement, and the money is named as an ESTIMATE of undetermined sign.
```markdown
## decision: research-pi

decision: restated at MEASURED
ref: __statera__/wave-07.md:363
statement: In Claude Code 2.1.304, `experimental: {cacheTtl: "1h"}` in the plugin's author agent file makes the 6-tool headless haiku author's cache writes 1-hour writes (17 of 17 requests, 0 five-minute) and keeps its cache across a gap of 333 to 422 s (n = 1 per arm); the sign of the money is not determined (ESTIMATE: +USD 0.87 of 47.80 at a 300 s bound, -0.60 at 360 s).
reason: The label covers the measured c1 and c2 and c3 narrowed to this configuration; c4 stays an ESTIMATE of undetermined sign, as the verifier found.
```

## Worst-fitting case
w07-c7. One label (MEASURED) is applied to a claim whose head label is compound and whose c4 is an ESTIMATE of undetermined sign; `lab_status` shows only `MEASURED`, so a reader of the state line alone gets a stronger picture than the statement. The proposed `statement:` states the limit, but the state line does not (CONJECTURE: this is the weakest of the five). The close second is w03-c2 (narrowed-block Grep result by the author only). The best fit is w04-c7, where the verifier wrote the label and the wording itself.

## Not covered
- I did not re-run any experiment; the readings are of the verdict sections and wave-note lines. I did not decide that MEASURED is the PI's intended label (no wave-note line says it for any of the five; `__reports__/wave-08/author-w08-9/decisions_table.md`).
- No wave-note line "names the label"; the wave-note refs are the first line of each decision bullet. Line numbers drift if the notes are edited.
- I did not append to any real claim file; the proposals are in `__reports__/wave-08/explorer-w08-k/proposed_sections.md`.

## Steering questions
- [now] Append the five sections (or four, leaving w07-c7 until the compound label is settled)? The text is in `proposed_sections.md`; the PI appends them by a shell append.
- [now] For w07-c7, is `restated at MEASURED` acceptable when the state line cannot say that c4 is an ESTIMATE, or should the PI file a superseding claim at c1 to c3 only?

## Pointers
- Scratch run (CHECKED, 83 claim files): `mkdir`, copy `__pondus__ __statera__ __scrupuli__` to `/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-8-928ebd/ad75be4f-14dd-4dd8-90c7-fb175ed36239/scratchpad/k_scratch`, append each block of `proposed_sections.md`, `python3 scripts/lab_status.py --project <scratch>`. Output filtered to the five claims and warnings: `__reports__/wave-08/explorer-w08-k/lab_status_scratch.txt`. Real tree: `git diff --stat -- __pondus__` empty after my work. (`scripts/lab_status.py` of this worktree; no helper script written, so none cited from `__instrumenta__/`.)
- Verifier sections: `__pondus__/w03-c2.md`, `w04-c4.md`, `w04-c7.md`, `w04-c10.md`, `w07-c7.md` (the `## verdict:` blocks).
