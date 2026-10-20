# Synthesis: how Murmuration should optimize itself

> "Search how the system should optimize itself, starting mostly from the elements we considered
> adding but set aside as over-engineering for now. Each of them may come back, change shape, or
> stay out, depending on what the evidence shows." (`__statera__/user_words.md`, 2026-10-19 10:56)

> "You are supposed to decide that based on experiment on the new architecture. or based on the
> logging you will be able to measure." (the user's answer in the question dialog, 12:26; quoted
> in `__statera__/wave-02.md`, because dialog answers never reached `user_words.md`)

Every statement below carries the current label of its claim, from `python3 scripts/lab_status.py`.
"By PI decision" means the verifier escalated and the PI decided, as recorded in the wave notes.
Waves 1–3 were merged to `main` by the user (84ff038). Wave 4 is on branch
`claude/murmuration-wave-4-3417be`, not merged; see "Wave 4" below.

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

## Wave 4: the open items, run overnight (2026-10-20, 09:27–12:00 JST)

> "Method note: following the teachings of the lab research loop skill, the items above are open
> puzzles not a checklist." (the user's 09:27 prompt; it reached the main checkout's
> `user_words.md`, not this one, which is item 1 itself)

Every experiment was pre-registered in `__reports__/reflective_run/w04/00-experiment_protocol_v0.md`
before it ran. Its addenda (E1b, E1c, E2b, E3b, E3c) were each committed before their runs. Labels
are the current ones from `/lab-status`.

**Item 1, the Desktop probe.**
- In this Desktop worktree session, the session cwd was the worktree (transcript, app log). The
  worktree had its own lab.
- The prompt hook still wrote the user's 09:27 prompt to the main checkout. It left main with an
  uncommitted `__statera__/user_words.md`.
- The budget hook's own records from the same session landed in the worktree. So the payload `cwd`
  was the worktree, and the Desktop's `CLAUDE_PROJECT_DIR` was very likely the main checkout
  (CONJECTURE: no hook environment could be dumped from a running session).
- **w04-c1 · MEASURED:** `user_words.py` and `resume_brief.py` now find the lab from the session's
  first recorded cwd, then the payload cwd, then `CLAUDE_PROJECT_DIR`.
  - Headless with the Desktop's pair, the shipped rule put 3 of 3 prompts in main; the new one put 3
    of 3 in the worktree. w01-c10's payload-first rule followed the shell's `cd` into another repo.
  - Cost: about +2 ms per prompt.
  - It gives up one case: a session that starts in main and enters a worktree partway through keeps
    its words in main.
  - Dialog answers are still not captured. That needs you to answer one dialog.

**Item 8, the report check past 100%.**
- With a brief that names the report, as `briefs.md` asks, the deny did not happen: 0 of 12 runs
  (w04-c2, superseded).
- It happened with the wave-3 brief that asks for the list in the hand-back.
- **w04-c8 · MEASURED**, at that brief, 150 files, USD 0.30:
  - Unchanged explorers were denied in 3 of 3 runs and overshot by 0.12–0.23 B after deciding to stop.
  - With the one line ("write the report before handing back, also when a budget note says to hand
    back"), there were 0 denies and 0 overshoot.
  - Reports were in the template's shape in only 1 of 3, the one run that opened the template file.
    The line gives no path, so the rule did not propose it.
- **w04-c12 · MEASURED:** the same line with the template's path met E1c's rule exactly on every
  threshold (denies 1 of 3, shape 2 of 3), against E1b's A run separately. The line is on the branch
  for your decision ("Still open" 8).

**Item 10, compliance or anxiety.**
- The `--max-budget-usd` flag that every earlier driver passed shows the worker the whole session's
  spend at every request (a `budget_usd` attachment). The wave-3 "5 of 8" is therefore confounded
  (CONJECTURE: those transcripts are gone).
- **w04-c11 · MEASURED**, with no cap and a task of about 1.5 B, n = 3 per arm, one task, one model,
  one worker type:
  - With the hook's notes, explorers changed what they did at the budget: 2 of 3 stopped (at 33 and
    56 of 70 items), and 1 of 3 compressed its method against the brief and finished 70 of 70 at
    1.11 B.
  - With no spend information at all, 3 of 3 ran on to 1.49–1.98 B.
  - No anxiety clause was met. The notes did their job, and nothing showed early stopping with budget
    left.
  - All 369 delivered items were correct.
- Side result (exploratory): without notes, two workers hit `maxTurns` and lost their whole
  deliverable with no hand-back and no trace in the harness.

**Item 11, search and reuse of `__instrumenta__/`.** All three claims are escalated, each restated by
PI decision on its verifier's figures.
- **w04-c4, 46 scripts:** workers listed the folder before writing in 14 of 15 runs, by `ls`.
  colgrep was used 0 of 15. Strict reuse was 7 of 15, so the result is inconclusive.
- **w04-c7, 429 scripts:** a cut `ls | head` showed the targets, and colgrep was used 1 of 6 (P) and
  0 of 6 (Q). A reworded paragraph (Q) did not change behaviour, so it was not proposed.
- **w04-c10, targets past position 300:**
  - Finding held at the rule's edge: 4 of 6 runs, the fit script 3 of 3, the near fit 1 of 3.
  - The targets were found by `ls | grep -i <keyword>`, which no agent file mentions. colgrep was
    used 0 of 6.
- Read plainly:
  - The paragraph makes workers look (exploratory: 2 of 6 looked without it).
  - Workers look with `ls` and `grep`, not with the colgrep search the paragraph names.
  - A near fit is mostly rewritten, not extended.
  - With opaque names, one worker overwrote an unrelated script.

**Item 9, the hooks' own cost (w04-c5 · MEASURED).**
- Before the change:
  - `budget.py` costs about 90 ms wall per start on the main thread, where it does nothing, and
    120–126 ms on a 5.6 MB worker transcript.
  - It starts twice per tool call.
  - In the design session that was 700 main-thread starts and 4,921 worker starts.
- The lean version:
  - a POSIX `sh` gate, so the main thread never starts Python;
  - `-S -I`;
  - code moved into cached modules;
  - the transcript read from a stored offset;
  - the report check, cheapest test first.
- Result: identical answers on 291 of 291 replayed worker runs.
- reproducer-w04-5's paired measurement (420 pairs): main thread wall down 61% (CPU down 91%), long
  worker wall down 48.4% (interval 47.9–49.1%, CPU down 79%).
- E4 asked for at least 50% on both, so **the lean version is not proposed** and is set aside on the
  branch tip (`4c46fe4`).
- Two costs found:
  - the gate reads its socket byte by byte, so it is slower than the old hook above about 200 KB of
    payload (typical payloads are 1–3 KB);
  - the code grew by 38%.
- The ablation shows where the gain is: the gate (main thread), the offset read (about 35 of 50 ms
  on long workers) and `-S -I`. The hand-written JSON buys 6.5 ms for 60 lines.

**Item 14 (w04-c6 · MEASURED).** `/lab` now says whether the colgrep index was built, was already
current, was empty, or belongs to a parent. It no longer fails on non-UTF-8 colgrep output.
`briefs.md` keeps helper code a file when a brief waives the claim file. The verifier found two
real bugs in the exchange, both fixed.

**What the wave showed about the team itself.**
- Every verifier changed something:
  - 2 real bugs (w04-c6);
  - a bound that was not a bound (w04-c1);
  - a grader that scored prose as data (w04-c8, w04-c11);
  - three titles stronger than the data (w04-c7, w04-c10, w04-c11);
  - a test that did not test finding (w04-c7).
- Of 12 wave-4 claims, 3 were superseded and 3 escalated and restated before they could be stated.
- Headless workers read files outside their lab (another session's scratchpad, an old plugin
  cache) while looking for the skill.

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
| w01-c10, the prompt hook's lab root (cwd first) | below CONJECTURE: restate | Replaced by w04-c1 (first recorded cwd), on the wave-4 branch |
| w04-c5, the lean hooks | MEASURED; not proposed | E4's long-worker criterion missed (48.4% against 50%); set aside at `4c46fe4` |
| w04-c12, the report line with the template path | see "Still open" 8 | On the wave-4 branch for your decision |
| w01-c6, close message to the human | below CONJECTURE: restate | It plausibly pre-empts 3 of 55 prompts; you chose "neither for now" |
| w01-c7, asking habit | below CONJECTURE: restate | It removes 1–2 of 19 asks; you chose "neither for now" |
| AskUserQuestion capture | prototype only (in w02-c2) | It works headless; a one-minute Desktop test with one answered dialog is needed |

## Cost of the study

The study's own sessions cost USD 136.30, by `/lab-status` at the close of wave 3. Headless runs
outside the repository add about 41: the five arms (19.57), the wave-2 probes (about 12) and the
wave-3 probes (about 9.5, from the workers' `total_cost_usd`). The total is about USD 178 (ESTIMATE).
Wave 3 cost about 31.6 against the PI's cap of about 15.

Wave 4 (2026-10-20, 09:27–10:55 JST) cost at least USD 53.15 against your budget of 100:
- 26.63 for this checkout's session, the PI and its 15 subagents included. That is list price,
  because the session was still open, so it is a lower bound (`/lab-status`, 162.93 − 136.30).
- 26.52 for the headless runs outside the repository: Claude Code's cost-state, exact, all
  sessions ended (`lab_status.py` run on `/private/tmp/murmuration-w04/`).
- The registry md5 of `installed_plugins.json` was unchanged from start to close.
- The wave ended at 10:55, before the 12:00 stop.

The PI set itself a cap of about USD 60 for wave 2. Wave 2 spent about 78, so the PI overran its own
cap by about 18. The USD 70–90 proposed for the whole study after wave 1 was never confirmed, and it
was overrun too. The user's budget for wave 2 was six hours. Wave 2 ran from 12:30 to about 17:00 JST.

## Still open

Items 2, 3, 13 and 14 are done. Items 1 and 8–11 were worked in wave 4 and keep only what is
left. 15–18 are new.

| # | Open item | Who | Cost |
|:--|:--|:--|:--|
| 1 | **Lab root, what is left.** (a) Your choice for w04-c1: the session's first cwd wins (a shell `cd` elsewhere is harmless; a session that starts in main and enters a worktree keeps its words in main), or the payload cwd wins (the reverse). (b) Your 09:27 prompt sits uncommitted in the main checkout's `__statera__/user_words.md`, written by the shipped hook: keep or revert it. (c) Dialog answers are still not captured; the prototype in w02-c2 needs one answered dialog in a new Desktop session. (d) The Desktop's hook CLAUDE_PROJECT_DIR is inferred, not dumped: a new Desktop session with the probe of w01-c10 settles it | you | minutes |
| 4 | Whether stated budgets make the PI plan a smaller team: several runs per arm (left alone, as you asked) | a further wave | about USD 20 |
| 5 | Protocol: authors edit claim heads during verification (again in w04-c6); evidence lines pin a commit the code has since left (w04-c1, w04-c4); graders parse prose lines as data (w04-c8, w04-c11); hand-backs quote the last note's figure and estimate their own resume cost; PI-authored claims, proof files and the verdict-line rule as before | a protocol claim | — |
| 6 | Small fixes: hand-backs repeat the report; `/lab-status` warns on a cost section in a puzzle file (w04-c6 proposes a wording); a parallel dispatch logs the default budget in its `start` line though the state holds the brief's; an uppercase agent name is truncated silently; a one-word hand-back ("placeholder") went through; hand-back files carry absolute transcript paths | small fixes | — |
| 7 | The nine set-aside elements not examined, and the tuning targets (`omitClaudeMd`, `autoCompactWindow`, a 1-hour cache for waiting authors) | further waves | — |
| 8 | **The report line (w04-c12 · MEASURED), your call.** On the branch in `agents/explorer.md` (ff2d5da). It met E1c's rule with every condition exactly on its threshold (denies 1 of 3, shape 2 of 3, median final 1.083 against A's 1.097), against E1b's A run 17 minutes earlier, not side by side. Before the first hand-back the template was opened in 1 of 3 runs, as with B' in w04-c8, so the path in the line is not shown to help; the report check accepts an off-template report; in E1c the rows went to the hand-back, not the report. A heading check in `handback.py` is untested | you | — |
| 9 | **The lean hooks (w04-c5), your call.** Set aside at `4c46fe4` (revert it to take them): main thread wall −61% and CPU −91%, long worker wall −48.4% (rule: 50%) and CPU −79%, identical on 291 replays, +38% code. A next build would: read the gate's input in blocks (it is slower than the old hook above about 200 KB of payload), drop the hand-written JSON (6.5 ms for 60 lines), decide the ceiling at PostToolBatch so PostToolUse need not start at all (halves starts), and respect `PYTHONDONTWRITEBYTECODE`. Your conda base has an editable hatchling install that adds about 9 ms to every Python start on this machine | a claim, then your call | about USD 8 |
| 10 | Closed by w04-c11 (the notes change what workers do at the budget; no anxiety at n = 3). Left: which graded note is enough to stop a worker, and a task whose accuracy can vary (workers script the arithmetic) | a test, if wanted | about USD 3 |
| 11 | **The search paragraph, your call.** Workers look before writing (14 of 15, 6 of 6, 6 of 6) but by `ls`, `head` and `ls \| grep -i`, almost never by the colgrep search the paragraph names (2 of 27 rule runs). Finding past a listing's cut held at the rule's edge (4 of 6); a near fit is mostly rewritten (strict reuse 7 of 15 at 46 scripts). Options: name the practice that works (list, grep the names, read first lines, pick a name not in the listing) and keep colgrep for content search; or keep colgrep and test why it is not used. Headless sessions have no Glob, so the fallback cannot be followed; with numbered names one worker overwrote a script | you, then a test | about USD 3 |
| 12 | Verifier independence next to the instruments folder (left alone, as you asked) | you | — |
| 15 | **A worker that reaches `maxTurns` loses its deliverable with no trace**: no hand-back, no `end` line, no hand-back file (2 of 2 uncapped no-notes explorers in w04-c3's exploratory arm). The budget notes prevent it; nothing catches it when they are off | a fix, then a check | small |
| 16 | **One lab rule for every script.** The lab is now found three ways: user_words/resume_brief (first cwd), budget/handback (live cwd, then parents), lab_init/lab_status (CLAUDE_PROJECT_DIR first; `/lab` in a Desktop worktree still writes to main) | a claim after you decide 1(a) and 9 | small |
| 17 | Platform facts found in wave 4, for drivers and briefs: `--max-budget-usd` shows every worker the session's spend; parallel `claude -p` launches sometimes fail with "Not logged in" (5 of 33); a worker's background job keeps `claude -p` alive after its result; headless sessions have no Glob or Grep; the platform replaces a launch CLAUDE_PROJECT_DIR; workers read files outside their lab (another session's scratchpad, an old plugin cache) while looking for the skill; every request carries a token counter | notes | — |
| 18 | **A reproducer printed its process environment into its own tool output**, including the API keys of a local gateway (`RIVAULT_*` variables). Nothing went to a file or to git; the text is in that subagent's transcript under `~/.claude/projects/`. You may want to rotate those keys | you | minutes |
