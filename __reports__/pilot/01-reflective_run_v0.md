# Pilot: the first reflective run

Date: 2026-10-19. Branch: `claude/murmuration-system-optimization-8cff9e`, not merged and not pushed.
Roadmap task: `__roadmap__/murmuration/build/pilot/reflective_run.md`.

The full answer is in `__statera__/synthesis.md`. The wave notes are `__statera__/wave-01.md` and
`wave-02.md` and `wave-03.md`, all closed, with every puzzle disposed. The wave-1 proposals are in
`__reports__/reflective_run/00-decision_sheet_v0.md`, and the experiment is in
`__reports__/reflective_run/w02/`. This file records each proposed change, its claim and its
state, and the decision that is still yours.

## The question

> Search how the system should optimize itself, starting mostly from the elements we considered
> adding but set aside as over-engineering for now. (`__statera__/user_words.md`, 10:56)

## Changes on the branch, waiting for your decision

Each change landed on the branch only after an independent verdict. "Your decision" means merging
it to `main` or not.

| Change | Claim · current label | Commit | Your decision |
|:--|:--|:--|:--|
| `/lab-status` spend in USD for every session of the lab | w02-c1 · MEASURED | 2b8dda9 | pending |
| Prompt hook keeps only your text | w02-c2 · MEASURED | 9b96ac0 | pending |
| Hand-back saver and a one-time report request to explorers | w02-c5 · MEASURED | fbbbcc3, bb7f2ce | pending |
| Findings-report template; workers without `Skill`; `maxTurns` 150 as a fallback | w02-c4 · below MEASURED: restate (the experiment's measurements are in w02-c8) | fbbbcc3 | pending |
| `/lab-status` reads a verifier's latest verdict | w02-c9 · MEASURED | b396fd1 | pending |
| Spend figures only from the harness log or `/lab-status` | w02-c10 · escalated; narrowed statement accepted by PI decision | d4fb928 | pending |
| README: the above, plus running a lab headless | w02-c7 · below MEASURED: restate; head restated by PI decision | 20a2d3c, 3332c7d, b14130f | pending |
| Worker budget v2: notes at 50, 75, 87.5 and 93.75% and from 100% as `Spent X of USD Y (Z%); t of T min (W%)`, finish-or-hand-back, raise on resume, floor USD 0.30 and 3 min | w03-c1 · MEASURED (wave 2's version failed its rule and was switched off in b14130f) | 7f98b1f | pending |
| Helper scripts as files in `__instrumenta__/`, one scoped search before writing, colgrep index at `/lab` | w03-c2 · escalated; restated by PI decision on the verifier's figures | 9e4bbac | pending |

## Proposed and not landed, with the reason

| Proposal | Claim · current label | Reason |
|:--|:--|:--|
| Prompt hook picks the lab from the payload `cwd` | w01-c10 · below CONJECTURE: restate | It regresses the opposite worktree case, and the Desktop payload has not been observed |
| Close-of-wave message to you | w01-c6 · below CONJECTURE: restate | Small effect; you chose "Neither for now" |
| An asking habit for the PI | w01-c7 · below CONJECTURE: restate | Small effect; you chose "Neither for now" |
| Briefs stop asking for report files (P1) | w01-c14 · MEASURED (the saver part) | You judged dropping reports dangerous. Reports stay as the deliverable, under digit-led names that the Write refusal lets through |
| Higher `maxTurns` per role (P6) | w01-c8 · escalated | You asked for a budget instead of turns; it landed as w03-c1. `maxTurns` 150 stays only as a fallback |
| The other set-aside elements | w01-c13 · CONJECTURE | Six were examined and stay out; nine were not examined |

## Tuning targets of the roadmap task

| Target | Covered by |
|:--|:--|
| Per-role tool allowlists | w01-c13: keep the explicit allowlists; workers drop `Skill` (w02-c4) |
| `maxTurns` per role | w01-c8, w02-c4, and the switched-off budget |
| `effort` per role | Every message was at `high` effort, so the data offer nothing to tune (decision sheet, O8) |
| `omitClaudeMd`, `autoCompactWindow` | not covered |
| `cacheTtl` | explorer-w02-b found the subagent cache lifetime is settable; the setting was not tested in use |
| Brief length against skill context | the skill listing (about 30k characters per worker) is removed by w02-c4. Briefs against the preloaded skill were not covered |
| Whether parked puzzles came back | not covered |

## Gates

- Every proposed change is a claim with independent verdicts: yes, by the tables above. Your
  decision on each change is still pending.
- Accepted changes land as commits, and rejected ones stay recorded with their reason: the changes
  are commits on the branch, and the rejected ones are recorded here. Nothing lands on `main` until
  you merge.

The study cost about USD 178 in all (ESTIMATE), more than the PI's own caps in every wave. The breakdown is in the
synthesis, under "Cost of the study".
