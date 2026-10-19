# Wave 2, phase C: experiment protocol (written before any run)

Date: 2026-10-19, about 13:05 JST. Author: research-pi. This file is committed before the runs, so
the metrics and the decision rules cannot be fitted to the outcome afterwards.

## Question the user asked

> You are supposed to decide that based on experiment on the new architecture. or based on the
> logging you will be able to measure. This should be an informed decision.

## Arms

| Arm | Plugin | Source |
|:--|:--|:--|
| A (shipped) | the plugin as on `main` (9ecbc6a) | `git worktree`-free export: `git archive 9ecbc6a agents skills scripts hooks .claude-plugin` into a scratch folder |
| B (candidate) | the study branch after phase B: w02-c1 spend reader, w02-c2 prompt-text rule, w02-c3 budget and hand-back hooks, w02-c4 report templates and lean workers | `git archive <branch head>` of the same paths |

Same everything else: Claude Code 2.1.302 headless, `claude -p --plugin-dir <arm> --agent
murmuration:research-pi --permission-mode auto --max-budget-usd 15`. The research-pi agent file sets
Opus, and the workers' files set Sonnet. Each arm gets a fresh scratch lab made by its own
`scripts/lab_init.py`, outside this worktree (in the PI's scratchpad, `w02/expC/<arm>/`). n = 1 per
arm, a limit of the budget, stated as such.

## Research question given to both arms (verbatim, through `/lab`-equivalent `lab_init.py` and the prompt)

> How many distinct non-empty substrings can a binary string of length n have at most, and which
> strings reach that maximum? I would like an answer for general n, with the evidence for it.

Prompt suffix, the same in both arms: "You will not hear from me during this run. Run the study
with your team within the budget, and end with the synthesis in `__statera__/synthesis.md`."

Ground truth, for scoring only, computed by the PI after the runs by brute force for n ≤ 18: the
maximum is expected to be sum over k = 1..n of min(2^k, n − k + 1). This expectation is my
recollection of a known result [assumption]; the brute force decides, not the recollection.

## Metrics (all read from files and logs; none from a model's judgement)

| # | Metric | Source |
|:--|:--|:--|
| M1 | Total USD, exact | the session's `cost-state` after it ends (main + subagents), via the w02-c1 reader |
| M2 | Worker runs without a deliverable: turn-limit stops, budget stops, refused writes, hand-backs lost | subagent transcripts; harness log (B); `__statera__/handbacks/` (B) |
| M3 | Explorer deliverables at the convention path and in the template's shape | `__reports__/` tree; template slots present |
| M4 | Budget notes and stops: count, the spend fraction when each fired, overshoot past 1.0 B, and whether the agent handed back after the note | harness log (B); subagent transcripts |
| M5 | The user's words: entries in `__statera__/user_words.md`, and whether any holds platform text | the file |
| M6 | Outcome: does the synthesis state the correct maximum for general n (against the brute force) and identify the extremal strings; how many claims were filed, verified, and at what labels | `__statera__/synthesis.md`; `__pondus__/`; `lab_status.py` |
| M7 | Wall time and the number of worker runs | transcripts |

## Decision rules (fixed now)

- **w02-c3, the budget hook.** It lands if, in arm B, every worker that gets a note or a stop hands
  back a deliverable (M2 = 0 lost to the budget mechanism), and the overshoot past 1.0 B is at most
  20%. It does not land if any worker loses its deliverable to the deny or stop path.
- **w02-c3, the hand-back saver and the deny-once check.** It lands if every explorer in B has a
  report at the convention path (M3) and every hand-back is saved, and no deny loops.
- **w02-c4, templates and lean workers.** It lands if B's explorer reports are at the convention
  path in the template's shape (M3), and B's worker start context is smaller than A's at equal
  role, read from the first request of each worker transcript.
- **No regression on the outcome.** If B's synthesis is wrong where A's is right (M6), nothing of
  w02-c3 or w02-c4 lands until that is understood. A difference in cost (M1) between the arms is
  reported but does not decide alone at n = 1.
- w02-c1 and w02-c2 have already landed on their own verdicts. Here they are only observed: does
  M1 come out of the new reader, and is M5 clean in both arms?

## What this experiment cannot show

- One run per arm. A difference in outcome or cost can be noise.
- Headless runs have no Desktop buttons and no human in the loop. The human-facing changes, which
  the user set aside, are not tested.
- Both arms use the same machine and the same user's skills and MCP servers. The lean-worker
  change matters more for users with many skills, as this user has 90.

## Addendum, arm B2 (written before the run, about 15:15 JST)

Arms A and B left the budget rule undecided: no note or stop fired at real B (`w02/explorer-w02-c`).
The candidate now also carries a time budget (w02-c6: defaults explorer 20, author 20, verifiers 15
minutes; note at 0.8, hand-back notice at 1.0, whichever of USD or time crosses first).

| Arm | Plugin | Difference from B |
|:--|:--|:--|
| B2 | the study branch at the commit made just before this run (B plus w02-c6) | time budget; `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` set, to test the README advice of w02-c7 |

Same question, prompt, models, `--max-budget-usd 15` and permission mode as A and B. B2 is not a
fair comparison with B on cost or time, because the ceiling differs; it exists to see the budget
mechanism in a real study and the ceiling advice in use.

Rules for B2:
- **Time/USD budget:** if any note or notice fires, the rule of the main protocol applies: every
  worker that gets one hands back a deliverable, and the overshoot past 1.0 of the deciding budget
  is at most 20% of that budget, in USD or minutes. If none fires, the budget stays on the branch
  as inert insurance, at its measured cost of about 40 ms per tool call and one start note per
  worker, and the rule stays undecided.
- **Ceiling advice (w02-c7):** B2 must end with a `synthesis.md` and with no "stopping them" line in
  stderr.
- **No regression:** B2's synthesis must be correct against the brute force.
