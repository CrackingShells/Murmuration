# Synthesis (draft: arm B2 and the claim on the experiment are pending)

> "Search how the system should optimize itself, starting mostly from the elements we considered
> adding but set aside as over-engineering for now. Each of them may come back, change shape, or
> stay out, depending on what the evidence shows." (`__statera__/user_words.md`, 2026-10-19 10:56)

> "You are supposed to decide that based on experiment on the new architecture. or based on the
> logging you will be able to measure." (the user's answer in the question dialog, 12:26; quoted
> in `__statera__/wave-02.md`, because the dialog never reached `user_words.md`)

Every statement below carries the current label of its claim, from `python3 scripts/lab_status.py`.
"By PI decision" means the verifier escalated and the PI decided, as recorded in the wave notes.

## The answer in one paragraph

Of the seventeen set-aside elements, the evidence brought back two, both smaller than first
designed. The first is the SubagentStop/SubagentStart pair (SA5, SA6). A hook saves every worker's
hand-back verbatim, asks an explorer once for its findings report, and gives each worker a budget in
USD and in minutes: one note at 80% and a hand-back notice at 100%. The second is the cost ledger
(SA3). It became `/lab-status` reading spend in USD from Claude Code's own records, with no new
store. Nothing argued for the other set-aside elements: the Rust binary, the JSONL stores and index,
the examen mirror, the friction and FileChanged hooks, the instruments, the question machinery,
bundled MCP servers and the depth reviewer (w01-c13, CONJECTURE). The changes that mattered most
were fixes to what had shipped. The record of the user's words held platform text. Cost tracking
missed worktree sessions, double-counted forks and gave no USD. Workers were cut off by turn limits,
refused their report files, and carried a 30k-character skill listing they did not use.

## What landed on the study branch (not merged to `main`)

| Change | Claim · label | Evidence (one line) | Cost |
|:--|:--|:--|:--|
| `/lab-status` spend in USD for every session of the lab, counted once, with subagent output marked as a lower bound and a notice when git is missing | w02-c1 · MEASURED | Matches Claude Code's `cost-state` within 0.05% on 213 cells; finds this lab from both checkouts; the shipped reader inflated forks ×1.32–1.44 and found 0 sessions from the main checkout | 1083 lines (was 880); 0.7 s |
| Prompt hook keeps only the user's text: leading platform blocks cut, then the command tests, then pastes unwrapped | w02-c2 · MEASURED | Over 5 real transcripts, 72 typed prompts kept, 51 cleaned, 0 dropped | +31 production lines; undocumented tags |
| Worker budget in USD (80% note, hand-back notice at 100%) and verbatim hand-back saver with a deny-once report check | w02-c5 · MEASURED | Notices reached the worker and were obeyed (5 of 5 where testable). Without them workers spent 3.1 B. 15 of 15 hand-backs saved byte for byte. The report followed the deny in 13 of 13 | ~40 ms per worker tool call; undocumented fields (`SubagentHandback`, transcript layout) |
| Time budget beside the USD budget | w02-c6 · *pending verdict* | 1-minute budget: note and notice fire on time and are obeyed. Arm B's 49-minute explorer would have been asked to hand back at 21 min | defaults rest on one run (CONJECTURE) |
| Findings-report template in research-loop; workers without the `Skill` tool; `maxTurns` 150 as a fallback | w02-c4 · below MEASURED: restate (template shape 3 of 5 with hooks; `/lab-status` still prints SUPPORTED, see S-w02-research-pi-3) | Worker first-request context 42–44% smaller at every role in the experiment; reports at the convention path. Landing decided by the experiment rule, *see the claim on the experiment* | +444 words |
| README: the above, and how to run a lab headless | w02-c7 · *pending* | Arm A lost its last explorer and its synthesis to `claude -p`'s 10-minute background ceiling | 9 lines |

## The experiment (pre-registered in `__reports__/reflective_run/w02/00-experiment_protocol_v0.md`)

*To be completed with arm B2 and the claim filed on the measurements.*

## What stays out, and why (w01-c13 · CONJECTURE, verifier SUPPORTED)

Examined and staying out: SA4 (examen mirror: transcripts already rebuild 15 of 16 messages), SA8
(friction hooks: 52 of 59 failures arrive as ordinary results), SA9 (live notices: no wait longer
than 300 s in 38 notices), SA13 (question machinery: the Desktop buttons are the channel), SA15
(bundled MCP servers: the bundled prefix would break the allowlists). SA5 and SA6 came back in a
changed shape (above), as did SA3. Not examined: SA1, SA2, SA7, SA10, most of SA11, SA12, SA14,
SA16, SA17. These stay out because nothing argued for them, not because the evidence ruled them out.

## Below their label, or not landed

| Claim | State | Why |
|:--|:--|:--|
| w01-c10, the prompt hook's lab root (cwd first) | below CONJECTURE: restate | A regression in the opposite worktree case; the Desktop payload is unobserved |
| w01-c6, close message to the human | below CONJECTURE: restate | Plausibly pre-empts 3 of 55 prompts; the user chose "neither for now" |
| w01-c7, asking habit | below CONJECTURE: restate | Removes 1–2 of 19 asks; the user chose "neither for now" |

## Still open

*To be completed at close.*
