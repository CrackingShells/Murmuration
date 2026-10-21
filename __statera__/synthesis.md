# Synthesis: how Murmuration should optimize itself

> "Search how the system should optimize itself, starting mostly from the elements we considered
> adding but set aside as over-engineering for now. Each of them may come back, change shape, or
> stay out, depending on what the evidence shows." (`__statera__/user_words.md`, 2026-10-19 10:56)

> "You are supposed to decide that based on experiment on the new architecture. or based on the
> logging you will be able to measure." (the user's answer in the question dialog, 12:26; quoted
> in `__statera__/wave-02.md`, because dialog answers never reached `user_words.md`)

Every statement below carries the current label of its claim, from `python3 scripts/lab_status.py`.
"By PI decision" means the verifier escalated and the PI decided, as recorded in the wave notes.
Waves 1–3 were merged to `main` by the user (84ff038). Wave 4 was merged into the local `main` at
the user's choice on 2026-10-21 (4c675ec, not pushed). Wave 5 is on branch
`claude/lab-system-optimization-1aa673`, not merged; see "Wave 5" below.

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

## Wave 5: the speed and leanness of operating the lab (2026-10-21)

> "I'd really like that you work on optimizing the speed and leanness of operating your lab. Of
> course, just like the other puzzle, this is not a checklist item but part of the trajectory."
> "note: make sure you are always running the latest version of the plugin on yourself"
> (`user_words.md` of the main checkout, 14:29; the hook wrote it there)

**The lab was not running the plugin it improves.**
- The plugin is read in place from the main checkout's working tree. Its cache copy, still at
  9eb759b from 19 October, is never read. So "updating the installation" changes nothing.
- The Desktop starts every session with the hidden flag `--project-config-root <main checkout>`
  (explorer-w05-e, reproduced headless). A worktree's own `.claude/` settings are therefore never
  read. `--scope local` from a worktree writes main's file. The prompt hook writes to main's
  `user_words.md`.
- Waves 3 and 4 measured their changes in headless runs on their branch. Their PIs and subagents
  ran main's copy.
- A reinstall-on-start hook cannot help: a directory plugin has nothing to update, and SessionStart
  fires after loading. "The latest version on myself" therefore means keeping main current. Wave 4
  was merged for that reason, by your choice. The other way is a symlinked marketplace path.

**Where a wave's time and money go.** The five probes measured wave 4:
- The PI was idle 75% of the time and owned about 11 minutes of the critical path.
- The 88 minutes were one author's experiment pipeline: 53 minutes of headless runs in 10 serial
  stages, 15 of them rerunning cells after a confound was found late.
- 80% of worker Bash time was 48 calls of 60 s or more, waiting.
- Orientation (skill, framing, agent files) was about 3% of worker spend. Re-reads were negligible.
- The hooks cost about 156 s per wave, `lab_status.py` about 0.8 s a call.
- Larger than all the hooks: auto mode puts a permission classifier on every Bash call, at a median
  of 448 to 747 ms. Its cost is in no record Claude Code keeps, so every spend figure in auto mode
  is a lower bound (explorer-w05-f, CHECKED on haiku headless runs).

**What changed, on the branch, each with an independent verdict:**
- **How a worker waits (w05-c1 · MEASURED, restated by PI decision).**
  - One paragraph in the worker files: no tool call waits more than 4½ minutes; poll in chunks; stop
    your own background jobs by pid.
  - An author subagent with 227k tokens of context, waiting on a 9-minute job, had 0 cold requests
    against 1 and cost 0.57 of the old file (0.53 in the verifier's pair; n = 3 per arm, one task).
  - The cause: a subagent's prompt cache lives 5 minutes, a headless main thread's 1 hour.
  - Not run: the other three agent files (same text, CONJECTURE), message latency during a wait, and
    the stop-your-jobs clause. Two text fixes came after the runs and are untested.
- **The colgrep path (w05-c2 · CHECKED).** The relative `__instrumenta__` searched the plugin
  source in a Desktop worktree session, not the lab. The agent files now say an absolute path.
- **The PI's tool schemas (w05-c7 · MEASURED, headless).**
  - A `disallowedTools:` line removes about 15,690 tokens from the PI's request 0, in 4 of 4 pairs.
    Connectors and project MCP servers stay.
  - An allowlist (w05-c3, superseded) did the same and silently dropped every server the plugin
    cannot name.
  - Artifact alone is 74% of the saving. Denying it is a judgement left to you.
  - The Desktop effect is an ESTIMATE (7.5–12% of a wave-4 PI) until one Desktop session is read.
- **`lab_status.py` (w05-c5 · MEASURED).** One git call instead of three, and a parse cache: 835 to
  261 ms warm, output identical. The verifier found two real defects in the cache, both fixed and
  retested.
- **Commits in a shared checkout (w05-c8 · CHECKED).** A plain `git commit` took another agent's
  staged revert into an unrelated commit (baba44f). Workers now commit by naming paths.
- **Reassessment in the procedure (w05-c10 · CONJECTURE).** After your remark that my plans never
  contain a re-plan, `waves.md` and the wave template ask for an entry each time results come back.
  In this wave six entries recorded changes of plan. That causation is not shown.

**Set aside.** The second lean hooks build (w05-c4 · MEASURED) halves the hooks' serial time
(−52.5% to −56%; starts 1788 to 985 a wave). E7's rule does not propose it:
- the build sends an extra message on 11 of 197 transcripts when tool calls come in parallel
  batches;
- it is 6% slower at a 500 KB payload, which the platform was not seen to send (31 KB at most);
- the rule's "identical on 291 of 291" was mine, and it was partly ill-posed.

It stays at ede2770, set aside at 0d3c879.

**What the team caught.** Verifiers changed something in 6 of the 7 claims they closed:
- two cache defects;
- an unrecorded protocol switch, and a pid file shared between parallel runs;
- a replay that could not see parallel batches;
- "intact" that was only "present";
- the missing `git add` for new files;
- my own estimated clock times in the wave note.

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
| w01-c10, the prompt hook's lab root (cwd first) | below CONJECTURE: restate | Replaced by w04-c1 (first recorded cwd), now on main with wave 4 |
| w04-c5, the lean hooks | MEASURED; not proposed | E4's long-worker criterion missed (48.4% against 50%); set aside at `4c46fe4` |
| w05-c4, the lean hooks, second build | MEASURED; not proposed | E7: an extra message on 11 of 197 transcripts in parallel batches, 6% slower at 500 KB; at ede2770, set aside at 0d3c879 |
| w04-c12, the report line with the template path | on main with wave 4 | Merged with wave 4 at your choice; its open questions stay in "Still open" 8 |
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

Wave 5 (2026-10-21, 14:29–16:16 JST) cost at least USD 44.47 against your budget of 150:
- 26.29 for this checkout's session, the PI and its 15 subagents included. That is list price,
  because the session was still open, so it is a lower bound;
- 18.18 for the headless runs under `/private/tmp/murmuration-w05/`, exact from cost-state, with
  all sessions ended.

Both are lower bounds in auto mode, because the permission classifier's cost is in no record.

The PI set itself a cap of about USD 60 for wave 2. Wave 2 spent about 78, so the PI overran its own
cap by about 18. The USD 70–90 proposed for the whole study after wave 1 was never confirmed, and it
was overrun too. The user's budget for wave 2 was six hours. Wave 2 ran from 12:30 to about 17:00 JST.

## Still open

Items 2, 3, 13 and 14 were done before wave 5. Wave 5 settled 1(d) and adds 19 to 24.

**Your decisions first.** On branch `claude/lab-system-optimization-1aa673`, each with its verdict:

| Change | Claim | Decide |
|:--|:--|:--|
| Waiting paragraph in the four worker files | w05-c1 · MEASURED (restated by PI decision) | land or not; two text edits after the runs are untested (5906331) |
| colgrep path made absolute in the agent files | w05-c2 · CHECKED | land or not |
| `disallowedTools:` on `research-pi` | w05-c7 · MEASURED headless | land or not, and whether Artifact stays denied (74% of the saving) |
| `lab_status.py` one git call and parse cache | w05-c5 · MEASURED | land the cache (+147 lines, two defects found and fixed) or only the git call (−11%, free) |
| Commit by naming paths, in briefs and working defaults | w05-c8 · CHECKED | land or not |
| "Reassessments" in `waves.md` and the wave template | w05-c10 · CONJECTURE | land or not |
| Second lean hooks build | w05-c4 · MEASURED, not proposed | leave set aside, or ask for a third build (item 9) |

Changes reach a running PI only once they are on main's working tree (item 1(e)).

| # | Open item | Who | Cost |
|:--|:--|:--|:--|
| 1 | **Lab root and plugin delivery.** (a) Your choice for w04-c1, now on main: the session's first cwd wins, or the payload cwd. (b) The main checkout's `__statera__/user_words.md` is uncommitted and holds the prompts of waves 4 and 5, written there by the hook. Keep or revert it. (c) Dialog answers are still not captured. (d) *Settled:* the Desktop passes `--project-config-root <main>`, so hooks see `CLAUDE_PROJECT_DIR` = main and the payload `cwd` = the worktree (explorer-w05-e). (e) To run a branch on yourself, merge it into main, or point `murmuration-local` at a symlink and switch it with `ln -sfn` (one edit to main's `settings.local.json`; global to every session) | you | minutes |
| 4 | Whether stated budgets make the PI plan a smaller team (left alone). New: the three wave-4 author chains ended at 55–90% of their 60-minute boxes; whether boxes set the length is untested | a further wave | about USD 20 |
| 5 | Protocol: authors still edit claim heads during verification (w05-c4, w05-c5); evidence pins drift; pre-registered rules were written before running their metric on the old code (E4, E7); output tokens are estimated (chars/1.3; 1.73 observed); the PI wrote estimated clock times (w05-c9) | a protocol claim | — |
| 6 | Small fixes: as before, plus harness `start` lines that swap names on same-second dispatches, and a stray background job that made the last `end` line wrong | small fixes | — |
| 7 | The nine set-aside elements not examined, and the tuning targets | further waves | — |
| 8 | The report line (w04-c12, now on main): as before, plus the hand-back gate makes an explorer told "write no file" write a report (all smoke runs of E6/E6b) | you, then a test | — |
| 9 | **The lean hooks, your call.** Two builds exist: w04-c5 (4c46fe4) and w05-c4 (ede2770, −52.5 to −56% serial seconds, 985 starts against 1788). A third build would need to: match the old messages in parallel batches (11 of 197 transcripts differ); cover failed or denied calls, which PostToolUse misses; and merge the two starts at a hand-back. It saves about 1.4 minutes of a wave against the 10 minutes auto mode costs (item 23) | a claim, then your call | about USD 8 |
| 10 | Which graded note is enough; a task whose accuracy can vary | a test, if wanted | about USD 3 |
| 11 | The search paragraph: as before. New: in a Desktop worktree the relative colgrep path searched the plugin source, not the lab (w05-c2), so wave 4's "colgrep almost never used" may partly be colgrep finding nothing useful | you, then a test | about USD 3 |
| 12 | Verifier independence next to the instruments folder (left alone) | you | — |
| 15 | A worker that reaches `maxTurns` loses its deliverable with no trace | a fix, then a check | small |
| 16 | **One lab rule for every script.** Under the Desktop, `CLAUDE_PROJECT_DIR` is main, so `lab_init.py`, `lab_status.py` and the `handback.py` fallback act on main from a hook. From Bash they act on the worktree, because the variable is empty there | a claim after 1(a) | small |
| 17 | Platform facts, as before, plus: a subagent's cache lives 5 minutes and a headless main thread's 1 hour; `sleep` of 30 s or more is blocked by Claude Code itself; a Bash call past 120 s without `timeout:` is moved to the background; Monitor can be given to a subagent but its events do not reach it; the headless Agent tool has no `name`; `tools:` can add a tool, and `mcp__*` matches nothing | notes | — |
| 18 | A reproducer printed gateway API keys into its own tool output in wave 4; you may want to rotate them | you | minutes |
| 19 | **Waits, untested parts.** The other three agent files, message latency during a wait, the stop-your-jobs clause, and the two edits of 5906331 | a check | about USD 3 |
| 20 | **The Desktop check of w05-c7.** One new Desktop session with the denylist on main: read the first request's usage and the tool names in its snapshot. About 31–49k tokens means it works; about 75k means the app injects regardless | you, then the PI | minutes |
| 21 | **The experiment pipeline, now the lab's critical path.** Run one pilot cell first; launch cells side by side; find out why batches stopped at 9; give headless drivers `CLAUDE_CODE_SHELL=/bin/bash` (first Bash call 0.5 s against 5.7–10 s; same tools resolved, PI check n = 1); keep timing records without account identifiers | a claim | about USD 5 |
| 22 | Costs outside the plugin: the skill listing re-entering the PI's context (19 times in waves 1–3); cache-prefix rewrites; a PI request for every hand-back; colgrep-mcp's own hook (119 ms per Bash, one 10 s timeout); your `.zshrc` (4.4–5.7 s per new shell) | notes; yours where it is your config | — |
| 23 | **Auto mode's classifier.** About 0.45–0.75 s per Bash call, roughly 10 worker-minutes a wave, and its cost is in no record. Narrow allow rules for read-only commands skip it. Lab scripts (`python3 -I scripts/…`) need a PreToolUse hook that answers "allow", which changes what your safety layer sees | you | — |
| 24 | Whether the `lab_status.py` cache is worth its code: 0.6 s saved per call against 147 lines, two defects found by the verifier, and a known limit (same size and mtime) | you | — |
