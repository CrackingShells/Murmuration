# Synthesis: how Murmuration should optimize itself

> "Search how the system should optimize itself, starting mostly from the elements we considered
> adding but set aside as over-engineering for now. Each of them may come back, change shape, or
> stay out, depending on what the evidence shows." (`__statera__/user_words.md`, 2026-10-19 10:56)

> "You are supposed to decide that based on experiment on the new architecture. or based on the
> logging you will be able to measure." (the user's answer in the question dialog, 12:26; quoted
> in `__statera__/wave-02.md`, because dialog answers never reached `user_words.md`)

Every statement below carries the current label of its claim, from `python3 scripts/lab_status.py`.
"By PI decision" means the verifier escalated and the PI decided, as recorded in the wave notes.
Nothing is merged to `main`. The changes are on branch `claude/murmuration-system-optimization-8cff9e`.

## The answer

Two of the seventeen set-aside elements came back, both smaller than first designed, and one part of the first did not pass its experiment.

The first is the SubagentStart/SubagentStop pair (SA5, SA6). Its new shape is three things:
- a budget for each worker, in USD and in minutes, with one note at 80% and a hand-back notice at 100%. It is built and verified, but it did **not** pass its pre-registered landing rule in the experiment, so it is switched off on the branch (see below);
- a verbatim copy of every hand-back, kept for the PI and the user and never fed back to agents;
- a one-time request to an explorer for its findings report.

The second is the cost ledger (SA3). It became `/lab-status` reading USD from Claude Code's own records, with no new store.

Nothing argued for the other fifteen. Six were examined: the examen mirror, the friction and FileChanged hooks, the question machinery, bundled MCP servers, and the parts of SA11 that were looked at. Nine were not, among them the Rust binary and the JSONL stores (w01-c13, CONJECTURE).

The larger gains came from faults in what had shipped. Each one is now fixed and verified:
- The record of the user's words held platform text.
- Cost tracking missed worktree sessions, double-counted forks and showed no USD.
- Workers were cut off by turn limits, were refused their report files, and carried a 30k-character skill listing they never used.
- The status script showed a revised verdict as its superseded state.

## What landed, with its evidence and cost

| Change | Claim · label | Evidence | Cost |
|:--|:--|:--|:--|
| `/lab-status` spend in USD for every session of the lab, each message counted once, subagent output marked as a lower bound, a notice when git is missing | w02-c1 · MEASURED | Matches Claude Code's `cost-state` within 0.05% on 213 cells. The shipped reader found 0 sessions from the main checkout and inflated forks ×1.32–1.44 | about +200 lines; 0.7 s per run |
| Prompt hook keeps only the user's text | w02-c2 · MEASURED | Over five real transcripts: 72 typed prompts kept, 51 cleaned, 0 dropped | +31 lines; relies on undocumented tags |
| Verbatim hand-back saver; deny-once report request (the budget part is in "Not landed") | w02-c5 · MEASURED | Without the notices, workers spent 3.1 B. With them, the note was obeyed in 7 of 7 cells and the notice in 5 of 5 where it could be tested. 15 of 15 hand-backs were saved byte for byte, and the report followed the deny in 13 of 13 | about 40 ms per worker tool call |
| Findings-report template in research-loop; workers without the `Skill` tool; `maxTurns` 150 as a fallback | w02-c4 · below MEASURED: restate | The claim as filed stated "template shape" from runs without hooks. In the experiment, worker start context was 42–45% smaller at every role present, and every explorer report sat at the convention path in the template's shape (B, B2, B3) | +444 words |
| `/lab-status` reads a verifier's latest verdict | w02-c9 · MEASURED | Only w02-c4 changes state on this lab, which is the one case of a revised verdict | small |
| Spend figures come from the harness log or `/lab-status`, never from a worker | w02-c10 · MEASURED by PI decision | The one worker that reported spend (B3) had read the platform's session-wide counter as its own, and the PI quoted that figure to the user | +47 words |
| README: the above, and how to run a lab headless | w02-c7 · below MEASURED: restate; restated by PI decision, the verifier's own result supports it | In one of five runs (A), `claude -p` stopped the last worker 10 minutes after the PI's last turn, and the run lost its synthesis. Arm B survived a 49-minute idle gap, so the stop does not happen every time. The recommended setting is CITED to the platform's message and untested | 9 lines |

## The experiment on the new architecture (w02-c8 · below MEASURED: restate; restated by PI decision, the verifier's own figures support the statement used here)

One research question (the most distinct substrings of a binary string of length n, and which
strings reach it) was run headless five times, one run per arm. The metrics and rules were committed
before each run (`__reports__/reflective_run/w02/00-experiment_protocol_v0.md`).

| | A shipped | B candidate | B2 + time budget | B3 small budgets | B4 forced |
|:--|:--|:--|:--|:--|:--|
| synthesis, correct | none | yes | yes | yes | yes |
| worker runs | 14 | 18 | 9 | 7 | 2 |
| lost deliverables | 1 (ceiling) | 0 | 0 | 0 | 0 |
| budget notes / stops | n/a | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 4 |
| USD | 4.88 | 6.47 | 4.65 | 2.35 | 1.22 |
| wall time | 21 min | 76 min | 22 min | 8 min | 6 min |

Read plainly:
- Every arm got the mathematics right.
- A lost its ending to the platform's background ceiling while its PI waited. That is a platform and waiting effect, not a plugin effect: B finished with the ceiling on.
- At the default budgets the budget hook never fired. At USD 0.05 it fired, and both workers kept their deliverables, but they ended at 3.0 and 2.4 B by the hook's estimate, about 3.8 B by exact cost. The report-writing request alone cost about 1.7 B, and the hook checks only between tool calls. The pre-registered rule (overshoot at most 1.2 B) failed, so the budget hook does not land.
- Smaller stated budgets came with smaller teams, lower cost and the same correct answer. That the budgets caused this is CONJECTURE: n = 1 per arm, and the arms differ in more than the budget.

## What stays out, and why (w01-c13 · CONJECTURE, verifier SUPPORTED)

Examined and staying out:
- **SA4 (examen mirror):** transcripts already rebuild 15 of 16 messages.
- **SA8 (friction hooks):** 52 of 59 failures arrive as ordinary results.
- **SA9 (live notices):** no wait longer than 300 s in 38 notices.
- **SA13 (question machinery):** the Desktop buttons are the channel.
- **SA15 (bundled MCP servers):** the bundled prefix would break the allowlists.

Not examined: SA1, SA2, SA7, SA10, most of SA11, SA12, SA14, SA16 and SA17. They stay out because
nothing argued for them, not because the evidence ruled them out.

## Not landed

| Claim | State | Why |
|:--|:--|:--|
| w01-c10, the prompt hook's lab root (cwd first) | below CONJECTURE: restate | It has a regression in the opposite worktree case, and the Desktop payload is unobserved |
| w01-c6, close message to the human | below CONJECTURE: restate | It plausibly pre-empts 3 of 55 prompts; you chose "neither for now" |
| w01-c7, asking habit | below CONJECTURE: restate | It removes 1–2 of 19 asks; you chose "neither for now" |
| AskUserQuestion capture | prototype only (in w02-c2) | It works headless; a one-minute Desktop test is needed |
| Worker budget, USD and time (w02-c5, w02-c6 · MEASURED) | built and verified; switched off on the branch | The mechanism works in probes: notes reach foreground and background workers and are obeyed. But in a real study it either never fired (default and USD 0.40 budgets) or overshot well past 1.2 B (USD 0.05). Re-enable it by reverting one commit if you judge the rule too strict for tiny budgets |

## Cost of the study

The study's own sessions cost USD 114 at least, by `/lab-status` at 16:41. That is a lower bound,
because this session is still open. Headless runs outside the repository add about 32: the five
arms (19.57) and the probes (about 12). The total is about USD 146.

The PI set itself a cap of about USD 60 for wave 2. Wave 2 spent about 78, so the PI overran its own
cap by about 18. The USD 70–90 proposed for the whole study after wave 1 was never confirmed, and it
was overrun too. The user's budget for wave 2 was six hours. Wave 2 ran from 12:30 to about 17:00 JST.

## Still open

| # | Open item | Who | Cost |
|:--|:--|:--|:--|
| 1 | Desktop probe for the prompt hook's lab root and for capturing question-dialog answers: what do plugin hooks receive in a Desktop worktree session? | you, with a new Desktop session | 1 minute |
| 2 | Your `~/.claude/plugins/installed_plugins.json` holds 212 local entries for `murmuration@murmuration-local`. The study's headless runs added them while they ran under this worktree's settings. Clean it up? | you | minutes |
| 3 | The scratchpad's raw run folders, and `__reports__/reflective_run/w01/author-w01-2/runs/` (228 MB, untracked), carry your email and organization id. Delete them? | you | — |
| 4 | The budget hook: keep it off, or re-enable it with a stated floor? It acts only between tool calls, so it cannot bound a budget smaller than a few requests (about USD 0.20 for Sonnet), and the overshoot rule was written without that floor | you | one commit |
| 5 | Whether stated budgets make the PI plan a smaller team (B–B4): a dedicated test with several runs per arm | a further wave | about USD 20 |
| 6 | Protocol: authors edited claim heads during verification; PI-authored claims get late answers; derived tables can truncate silently; proof files under `__pondus__/` are read as claims; the verdict-line rule now favours a stray quoted line | a protocol claim | — |
| 7 | Hand-backs repeat most of the report; the platform's subagent prompt discourages report files (2 of 5 explorers skipped the template in one test); one wave-2 puzzle file used a heading that `/lab-status` cannot track | small fixes | — |
| 8 | The nine set-aside elements not examined, and the tuning targets not covered (`omitClaudeMd`, `autoCompactWindow`, a 1-hour cache for authors waiting on a verifier) | further waves | — |
