# Wave 03

opened: 2026-10-19

## The user's sentence this wave serves

These came in chat after the study closed. They are not in `__statera__/user_words.md`, because the
prompt hook writes to the main checkout's lab from this worktree (S-w01-research-pi-5). Quoted
verbatim from this session's transcript:

> Regarding the budget hook, the failed test is indeed systemic. We can't expect the hook to have an
> effect if the budget is so small the agent goes over it before the hooks triggers. [...] Also you
> only notified it at 80%. What about a logarithmic to 100% (25, 50, 62.5, 75, 83.5, etc.) and always
> above 100%. Obviously there is the edge case that if the agent is just on the way to get an answer it
> should finish rather than paying the cost of reporting to other agents. If the agent really want to
> keep working while not having strong results, then it must make its case back to the PI which has
> the money overall. Or maybe that makes the dynamics too complicated?

> Be careful of PostToolBatch, this was in the end not used in another project because it seemed not
> to be triggered exactly when one wanted. So go for it but be aware of it if something goes wrong.
>
> yes, you can build it, but I would prefer a format of the budget reminder saying "Spent X of USD Y
> (Z%); t of T min (W%)"

## What does not add up

The budget hook was switched off (b14130f) by a pre-registered rule that judged only how tightly the
100% stop holds. That rule was wrong for the question: the user asked for a budget delivered to the
agent "without triggering context or deadline anxiety". On those terms the hook had passed every run:
it delivered the budget, caused no slowdown (B3, rough signal) and lost no deliverable (B4). The overshoot
in B4 was built in: the first request alone used 0.55–0.81 of a USD 0.05 budget (w02-c8). So the
hook needs a stated floor, notes that grow denser towards the limit, a choice between finishing and
handing back past 100%, and a way for the PI to raise a budget on resume.

## Design given to the author (PI decision, from the user's answers)

- Checks at request boundaries only. No hook fires inside a model request: of the 22 hook-output
  schemas in Claude Code 2.1.302, none is per request [source: the binary's schemas, read by the PI].
  Use `PostToolBatch` if a probe shows it fires once per tool batch in subagents (foreground and
  background, single and parallel calls) and its `additionalContext` reaches the worker. Otherwise
  keep `PostToolUse`, made safe for parallel calls. The user warned that `PostToolBatch` misfired in
  another project.
- Notes at 50, 75, 87.5 and 93.75% of the deciding budget (the larger of the USD and time fractions),
  then at every check from 100%. At most one note per check, with the current figures.
- The note text is exactly `Spent X of USD Y (Z%); t of T min (W%)`, facts only below 100%.
- From 100%: the same line, plus this sentence: "If one or two more steps finish the result, finish it.
  Otherwise hand back now: what you have, what is missing, and what more budget would buy." At the
  hard ceiling (1.5 of the deciding budget), the old `decision: block` path applies: hand back now.
  The hand-back itself is never blocked.
- Raise on resume: a `Budget: USD x` or `Time: min t` line in a message the PI sends to resume a worker
  grants that much more, counted from that moment. Time counts active time only, not the idle gap
  before the resume.
- Floor: briefs give no budget under USD 0.30 (about ten requests at USD 0.03–0.04 each, ESTIMATE from
  w02-c8's first-request figures), and nothing under 3 minutes.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| author-w03-1 | author | w03-c1: build the budget hook v2 to the design above, probe `PostToolBatch` first | yes; claim filed MEASURED, tree left uncommitted; USD 3.43 + 0.29 by `total_cost_usd` (author's figure, from cost records) |
| reproducer-w03-1 | reproducer | verify w03-c1 | SUPPORTED, after one fix found in the exchange (parallel starts); USD 1.9 by `total_cost_usd`; landed as 7f98b1f |
| author-w03-2 | author | w03-c2: helper scripts as files in `__instrumenta__/`, one scoped search before writing, index built at `/lab`, measured against the wave-2 baseline | yes; claim filed MEASURED (n = 1); inline Python fell to 0, scripts saved as files, but no search and no reuse was exercised; tree uncommitted |
| reproducer-w03-2 | reproducer | verify w03-c2; main risk: `.ignore` may hide lab files from the Glob and Grep tools | ESCALATE; USD 1.52 by `total_cost_usd`; decided below |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- **Author's choices accepted pending the verdict:** notes on `PostToolBatch` (fired at 109 of 109
  batches in its probes), the 1.5 ceiling block on `PostToolUse`, because a `decision: block` on
  `PostToolBatch` stopped workers with no hand-back (4 of 4). The raise sets the limit to
  max(limit, spend) + x: a raise never takes away unspent budget. This differs from my "x more from
  that moment" only for a worker that hands back below its limit, where the author's reading is the
  more generous, and I accept it. The reproducer must rerun one end-to-end cell on the final file,
  because e1–e4 and e7 ran on an earlier copy.
- **The user confirmed the PostToolBatch trap** from another project: a block sent on `PostToolBatch`
  ends the worker with no hand-back, and that project also ended with a mix of the two events.
- **Next claim, w03-c2 (after w03-c1 lands, since it touches the same files): helper scripts as files,
  found again by a small targeted search.** Baseline in this study's 42 worker transcripts
  [PI measurement, `scratchpad/heredoc_measure.py`, unverified until w03-c2]:
  - 1,041 of 1,811 Bash calls were heredocs, 781 ran inline Python, and only 20 Python files were
    written with Write;
  - heredoc commands are 56% of all worker output characters;
  - 1 colgrep search in 42 workers, against 598 Bash calls that used a shell search command and 238
    Python heredocs that walk files;
  - this worktree has no colgrep index.

  On this machine, 155 of 228 colgrep indexes are stale (orphaned, shadowed or machine state), about
  3.4 of 4.6 GB [source: `list_indexes`]. The user's words: "a strict discipline to maintain colgrep
  indeces and targeted searches goes a long way to saving repeated wastes", and "we shouldn't have any
  such meta-discourse, but everything should point at this behavior emerging". Side finding: the
  colgrep shell-search hook denied a PI heredoc whose text merely named those commands (a false
  positive on heredoc content).
- **PI decision on the ESCALATE of w03-c2** (reproducer-w03-2, which the author accepted):
  - The head is restated in place to the verifier's figures: where scripts are saved (3 of 3 in
    `__instrumenta__/` against 0 of 4 in a control at 7f98b1f, n = 1 per arm). Inline Python is 0
    against 1, which shows no effect. The 715-against-0 contrast compares different tasks.
  - `.ignore` is narrowed to folders (the hand-back copies, raw and run folders). Grep honours it,
    and hiding `*.json` and `*.txt` hid derived tables and would hide `package.json` in a code project.
  - The housekeeping line loses `colgrep clear`: in a lab folded into a parent's index, that command
    clears the whole parent index.
  - The search paragraph is kept in the agent files only.
  - Search and reuse remain unexercised. They need a lab with many scripts.
- **Parked for later, at the user's request: the hooks' own cost.** The user, on the 89–104 ms per
  budget-hook run (w03-c1): "this is too long", and "the system itself must be frugal, and the
  manifestation of the system running must also achieve results while being frugal. [...] there are
  obvious parts where there is no reason to waste anything, so we don't do it: be lean. Don't tackle
  that now, keep it for later". To look at:
  - the hook is a Python process started on every tool call of every agent, the PI's included, and it
    does nothing for the PI;
  - it rescans the transcript on each call rather than reading only what was added;
  - five registrations share one script;
  - the same questions apply to `handback.py`, `user_words.py` and `lab_status.py`.

  No measurement has been made yet.
- Spend cap for this wave: about USD 15 for the build and its verification. A test on a harder
  question (about USD 10–20) is not part of this cap; the user decides it after the build.

closed: YYYY-MM-DD
