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

Two of the seventeen set-aside elements came back, both smaller than first designed. The budget part of the first failed its wave-2 rule; in wave 3 it came back in a new shape, after the user judged that rule wrong for the question.

The first is the SubagentStart/SubagentStop pair (SA5, SA6). Its new shape is three things:
- a budget for each worker, in USD and in minutes (w03-c1 · MEASURED). Notes come at 50, 75, 87.5 and 93.75% and at every check from 100%, as `Spent X of USD Y (Z%); t of T min (W%)`. From 100% the worker finishes if one or two steps do it, otherwise it hands back and asks the PI for more. The PI can resume it with a raise. Wave 2's version, with one note at 80% and a stop at 100%, was switched off by its rule; see "Wave 3";
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
| Worker budget v2: graded notes on `PostToolBatch`, the 1.5× ceiling block on `PostToolUse`, finish-or-hand-back past 100%, raise on resume, floor USD 0.30 and 3 min | w03-c1 · MEASURED | `PostToolBatch` fired at 109 of 109 batches; `PostToolUse` missed 13 of 172 calls. A block on `PostToolBatch` ends the worker with no hand-back (4 of 4), so the block stays on `PostToolUse`. Notes in the exact format, raise and active time reproduced on the final file | about 90–100 ms per tool call of every agent (parked, see open item 9) |
| Helper scripts as files in `__instrumenta__/`, one scoped search (5 results) before writing, colgrep index built at `/lab`, folder-only `.ignore` | w03-c2 · escalated; restated by PI decision on the verifier's figures | Scripts landed under `__instrumenta__/` in 3 of 3 cases against 0 of 4 without the build (n = 1 per arm). Inline Python was 0 against 1, no measurable effect. Search and reuse were not exercised | one paragraph per agent file; index build at `/lab` |
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

## Wave 3: the budget and the scripts, on the user's reading

The user read the wave-2 budget failure as built in: "We can't expect the hook to have an effect if
the budget is so small the agent goes over it before the hooks triggers." In B4 the first request
alone used 0.55–0.81 of a USD 0.05 budget (w02-c8). Wave 3 rebuilt the budget to the user's design
(w03-c1). No hook fires inside a model request, so the limit is one request's cost, and briefs now
carry a floor. The notes go on `PostToolBatch` and the block stays on `PostToolUse`. The user
recognised that mix from another project, where a block on `PostToolBatch` had ended workers the
same way.

The user also saw agents "free-wheeling the bash commands with gigantic bash or python scripts". In
waves 1–2, 967 of 1,703 worker Bash calls were heredocs, 715 ran inline Python, and 1 colgrep search
was made (w03-c2, the verifier's own count). Every worker received a routing hook that says "Chain
several steps into one Bash call", the auto-mode note offering heredocs, and the plugin's own
`cat >> <<'EOF'` verdict append. Which of these dominates is untested. w03-c2 makes helper code a
file, found again by one scoped search. In one small run that moved where scripts are saved. It
showed no reuse, because parallel workers start before any script exists.

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

## Cost of the study

The study's own sessions cost USD 136.30, by `/lab-status` at the close of wave 3. Headless runs
outside the repository add about 41: the five arms (19.57), the wave-2 probes (about 12) and the
wave-3 probes (about 9.5, from the workers' `total_cost_usd`). The total is about USD 178 (ESTIMATE).
Wave 3 cost about 31.6 against the PI's cap of about 15.

The PI set itself a cap of about USD 60 for wave 2. Wave 2 spent about 78, so the PI overran its own
cap by about 18. The USD 70–90 proposed for the whole study after wave 1 was never confirmed, and it
was overrun too. The user's budget for wave 2 was six hours. Wave 2 ran from 12:30 to about 17:00 JST.

## Still open

| # | Open item | Who | Cost |
|:--|:--|:--|:--|
| 1 | Desktop probe for the prompt hook's lab root and for capturing question-dialog answers: what do plugin hooks receive in a Desktop worktree session? | you, with a new Desktop session | 1 minute |
| 2 | Your `~/.claude/plugins/installed_plugins.json` holds 212 local entries for `murmuration@murmuration-local`. The study's headless runs added them while they ran under this worktree's settings. Clean it up? | you | minutes |
| 3 | The scratchpad's raw run folders, and `__reports__/reflective_run/w01/author-w01-2/runs/` (228 MB, untracked), carry your email and organization id. Delete them? | you | — |
| 4 | Whether stated budgets make the PI plan a smaller team (B–B4): a dedicated test with several runs per arm | a further wave | about USD 20 |
| 5 | Protocol: authors edited claim heads during verification; PI-authored claims get late answers; derived tables can truncate silently; proof files under `__pondus__/` are read as claims; the verdict-line rule now favours a stray quoted line | a protocol claim | — |
| 6 | Hand-backs repeat most of the report; the platform's subagent prompt discourages report files (2 of 5 explorers skipped the template in one test); one wave-2 puzzle file used a heading that `/lab-status` cannot track | small fixes | — |
| 7 | The nine set-aside elements not examined, and the tuning targets not covered (`omitClaudeMd`, `autoCompactWindow`, a 1-hour cache for authors waiting on a verifier) | further waves | — |
| 8 | **Report check against the budget:** the one-time report request refuses an explorer's first hand-back and pushes it past 100% after it has decided to stop. That happened in 5 runs (e2, e3, e5, e6, q1), costing about 27% of B in e2 and e3. A candidate fix is one line in the explorer file: write the report before handing back | small fix, then a check | — |
| 9 | **The hooks' own cost** (you parked this): the budget hook is a Python process on every tool call of every agent, the PI's included, at about 90–100 ms, and it rescans the transcript each time. The same question applies to the other hooks and to `/lab-status` | a later wave | — |
| 10 | **Compliance or anxiety:** 5 of 8 workers handed back on their own at 75–99%. It needs a run without notes at the same budgets to tell which | a test | about USD 3 |
| 11 | **Search and reuse of `__instrumenta__/`:** not exercised. It needs a lab whose workers start after scripts exist, with dozens of scripts | a test | about USD 5 |
| 12 | **Verifier independence:** the instruments folder sits next to the code a proof-adversary must not reuse. Should verifiers be exempt from the reuse rule for the code under test? | your call, or a protocol claim | — |
| 13 | **Stale colgrep indexes on your machine:** 155 of 228 stale, about 3.4 GB. CLI searches on subfolders of an unindexed tree make one index each, and `/private/tmp` is indexed as one project. Prune them? (`index_prune` makes a dry run first) | you | minutes |
| 14 | Small fixes: `lab_init.py` says "built the colgrep index" when a lab joined a parent's index; a brief that says "no claim file is needed" made an agent skip writing its script as a file (1 run against 6) | small fixes | — |
