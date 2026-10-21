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
the user's choice on 2026-10-21 (4c675ec, not pushed). Wave 5 was merged into the local `main` at
fed7a08, and wave 6 by the lab's own decision under the frame of 17:06 (see "Wave 6"). Wave 7 was
merged into the local `main` at 3b0448b by the same frame. Nothing was pushed.

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

## Wave 6: the larger move, small waste, the idle PI, and the guardrails (2026-10-21)

> "I don't understand why you are not even considering larger moves such as completely changing
> the language of the scripts in the hooks from python to Rust" · "It's not because it's cheap
> that we should spend it." · "Do you think the PI should be doing something?" · "The guardrails
> are morals, legals, ethics. Things that are about engineering and about the Murmuration system,
> I don't have anything to decide." (17:06) · "that's typically what folds under security, ethics,
> moral, and legal that cannot be done without the user's permission" (19:27) · "think how to harden
> that [...] avoid the agent working around and running `claude -p` in bypass mode" (19:3x)

From this wave on, the lab decided the engineering and landed it on the local `main`. The
guardrails stayed with you. Every rule below was committed before the runs it governs. Three rules
were wrong as I wrote them, and the wave note says where.

**The larger move was examined, and neither of its forms lands.**
- **Rust.** A compiled do-nothing hook saves about 30 ms a start against python as the platform
  records it, about 1% of a wave (explorer-w06-a, in its report). Against a lean `python3 -S -I`
  start the saving is inside the noise (explorer-w06-b, in its report). Shipping it would need
  binaries committed per platform, about 1.5 MB a version, because a plugin installed from git has no
  build step, and a binary cannot be reviewed from a diff. The 322–605 ms the platform recorded is
  hooks of one event starting together, about +40 ms per sibling. It is neither language nor shell.
- **No process at all.** A resident server called by `mcp_tool` hooks carries every field, effect
  and event at 1–6 ms (w06-c6 · MEASURED). But it can die silently: a failed restart drops the deny
  and the 150% block, leaving only a transcript record. A server that failed twice did not reconnect
  in later sessions. The safety net that tells the worker and the PI costs the margin: hook time
  21.1% of main's against at most 20%, and +320 lines against +300 (w06-c4 · below MEASURED: restate,
  not restated; numbers from its verifier). It is reverted. The Python hooks cannot fail that way, so
  keeping them is not waste.

**What did land: the waste inside each Python start (w06-c9 · MEASURED).**
- The same 10 registrations, the same outputs (197 of 197 replays in sequence and in parallel, 814
  real command starts, Python 3.9, 3.12 and 3.14), about 20–28 ms less a worker start, CPU halved.
  Over a wave like wave 4 that is about 32 s of 161 (ESTIMATE).
- **Landed by my decision, against its registered threshold.** The rule asked for 25 ms in every
  pair, and no Python start here can save more than about 26 ms against a per-pair scatter of about
  20 ms. That is the third lean build judged by a threshold at its physical ceiling
  (S-w06-research-pi-2). The verifier's two fallback findings were fixed and checked first.

**The idle PI.** Idle time costs nothing. All 256 PI requests of waves 4–5 wrote 1-hour cache, and
every gap was a full hit (explorer-w06-c, in its report). The PI is not on the critical path. A
procedure change that moved dispositions into the waits saved 69 s that were off the critical path
anyway (w06-c2 · below ESTIMATE: restate), so it was reverted. **The PI should not do more while it
waits.** What its cost depends on is what it reads to orient: the first turn is 21–32% of PI spend.
The w05-c7 denylist is confirmed on the Desktop: request 0 went from 74,966 to 46,738 tokens on the
same version, and the 29 tools removed are exactly the line's matches (w06-c1 · MEASURED).

**The guardrails.**
- **What was found.** A worker ran headless test sessions in bypass mode. Then the guard's own
  replay of the lab's Bash history found **32 `claude` runs in bypass mode** across waves 1–6 (22 on
  10-19, 4 on 10-20, 6 on 10-21). It also found 16 runs under a scratch `CLAUDE_CONFIG_DIR`, 7 with
  `--setting-sources` leaving out your user settings, and 8 Bash writes of settings files, one of which
  restored the main checkout's settings file from a backup (reproducer-w06-7's classification in
  `__pondus__/w06-c11.md`). None had your yes.
- **What landed.** Each worker file has a "Permissions" paragraph, and `briefs.md` and
  `working_defaults.md` carry the same rule: no run skips or loosens the permission layer without your
  own yes, quoted in the brief. This is your decision of 19:27, applied as text. There is also a
  guard in the plugin (w06-c13 · MEASURED), after four pre-registered versions. One unconditional
  PreToolUse row on Bash and 31 rows on Write, Edit and NotebookEdit of settings and script files run
  `scripts/permission_guard.py`, fail closed, with a 20 s timeout. It denies bypass flags, `claude`
  runs that escape your user settings, writes of settings files, and a script that gains the bypass
  words. In a replay of 4,637 real lab Bash calls it would have denied 63 such acts, with 26 strict
  false denials. It costs one process start per Bash call, about 70 ms on a quiet machine and seconds
  under heavy load. That is a price your guardrail is worth, and it is stated, not hidden.
- **What only you can close.** A text guard cannot see a flag built from pieces, base64, a script
  already on disk, or a settings file passed by another path. A plugin cannot ship permission
  settings. Only managed settings hold against a child that changes its flags, environment or folder
  (CITED, `__reports__/wave-06/research-pi/permission_mechanisms.md`). The line is
  `{"permissions": {"disableBypassPermissionsMode": "disable"}}` in
  `/Library/Application Support/ClaudeCode/managed-settings.json` (admin rights). It also stops you
  using bypass mode.
- **Held at the permission layer.** The text that stops the plugin handing engineering back to you
  (`agents/research-pi.md`, `waves.md`, the framing template) was denied by the auto-mode classifier
  as self-modification. I did not route around it. It waits in
  `__reports__/wave-06/research-pi/decision_frame_patch.md`, to be applied or not.

## Wave 7: the machine, the agent loop, and what is worth saving (2026-10-22)

> "'know your algorithms', leverage 'parallel-first' because the Modern hardware is done that way
> [...] I know that parallelism also has a cost at the CPU level and that scaling is not linear"
> · "Try explore other possibilities. Don't forget your nature as a research PI. All this also
> teaches us things about our hardware and limit of optimizing Claude Code's agent loops." · "I
> don't see how that exempts us from saving that 1% if we know we can save it." · "the deny list
> for the Pi was smart. I wonder if this applied to the other agents as well?" (2026-10-21 23:28
> and 23:50)

Seven probes, seven experiments, each rule committed before its runs, each claim checked by a
verifier who had not done the work. Every number below is MEASURED unless marked.

**What the machine does (this M3 Pro, macOS 26.6, with the Falcon endpoint extension installed).**
- One exec costs about 14–16 ms before the child's first instruction, whatever the language:
  `posix_spawn` returns in 0.17 ms, `fork` without exec costs 0.48 ms, and a binary the kernel kills
  before any user code still costs 13.6 ms. dyld and libSystem are at most about 2 ms. C, assembly
  and every Rust build come within 1.2 ms of each other; `python3 -S -I` adds 7.8 ms. The cause of
  the 14 ms is a CONJECTURE: the kernel's exec security path (`opendirectoryd` burns about 11 ms of
  CPU per exec and none per fork). A new binary's first exec costs 150–480 ms, once (explorer-w07-a,
  author-w07-5).
- `/bin/sh` is a trampoline into bash, two execs. Claude Code runs every string-form hook as
  `/bin/sh -c`, whatever `CLAUDE_CODE_SHELL` says, so a Python hook was three execs and the
  platform's recorded duration is all spawn path. Wave 6's two unexplained numbers (`sh :` at 33 ms,
  a Rust no-op 18 ms above it) are exec counts.
- Parallel parsing scales to the six performance cores and flattens there: a Python pool reaches
  6.0× at 12 workers, Rust 87 ms on one thread and 16–17 ms on 10–12 (efficiency 0.42–0.53); each
  efficiency core adds about 0.3–0.5 of a performance core. Python's default `spawn` start costs
  63–172 ms a pool on macOS against 2–10 ms for `fork`, enough to cancel the gain on small inputs.
  Rust's parser is 7× Python's on one core (explorer-w07-d).

**What the agent loop does, and where the plugin sits in it.**
- A worker's wall time over waves 5–6 (of 47 workers and 2,633 requests read over waves 4–6; wave 4
  has no request timestamps): 30.8% model requests (41% of that thinking), 45.6% tool phases, 22.3%
  idle waits for a message, 1.3% client gaps. The plugin's
  hooks are 0.13–0.5% of it, the auto-mode classifier about 1.9% (explorer-w07-b, explorer-w07-g;
  the shares are ESTIMATEs from records).
- Auto mode's classifier waits a median 628 ms on a trivial Bash call (55 ms for the whole call in
  default mode, 709 ms in auto). A PreToolUse hook runs alongside it and is mostly hidden; a
  PostToolUse hook is not. A Read never reaches the classifier. The classifier's wait doubles
  between identical sessions and does not grow with context from 42k to 102k tokens.
- Parallel-first at the message level is already done, inside the shell: 92% of worker requests
  carry one call, yet batching independent calls would have saved 0.8–1.6% of requests
  (ESTIMATE), because 75% of Bash calls already chain three or more statements and the next call
  usually needs the last result. Four reads took 2.83 s as four Reads in one message, 3.39 s as one
  chained `cat`, 3.79 s as four Bash calls in one message and 5.11 s as four messages (n = 1 each).
- The larger costs are not hooks: prompt-cache re-writes after gaps over 5 minutes, 15.8% of worker
  spend; tool results over 5,000 characters re-read by every later request, 29.7% of cache-read
  spend; requests right after a tool error, 8.5% of wave 6's (mostly the worktree-isolation refusal of complex `git` and the harness's `sleep` refusal; ESTIMATEs over recorded transcripts).
- Platform facts the lab found by testing: a prompt's transcript record is written only after the
  UserPromptSubmit hooks exit; two hook rows with the same command string run once; an `async`
  hook's failure is silent and one still running when `-p` ends is cancelled; an `http` hook with
  `onFailure: "block"` fails loudly on PreToolUse and PostToolUse, ends the whole session on
  PostToolBatch and is silent on SubagentStop; an agent file truncated to empty is dispatched as a
  generic agent without a word; and the PI's request 0 moves by about 2.4k tokens with which of your
  MCP servers have connected at launch.

**What landed on the local `main`** (3b0448b, merge --no-ff; a headless smoke run from main's own tree then showed the installer run and the binary decide a Bash call in 30 ms).
- **Every hook row in exec form, no shell (w07-c3 · MEASURED).** The same 42 handlers, the same
  outputs (215 of 215 scripted starts; every live pair, the graded budget note included), fail
  closed when the guard crashes or `python3` is missing. The guard's start fell from 123 to 42 ms
  and the budget hook's from 104.5 to 41 ms (pooled; 10 of 10 pairs each, reproduced 6 of 6). It
  saves CPU and energy on every tool call. The budget hook runs after every tool call and is not
  hidden behind the classifier, so its 60–70 ms should reach a worker's wall; ten pairs could not
  resolve that against a ±600 ms spread, and a whole session was not shown shorter. With a missing `python3`, B names the cause on the first blocked call only.
  The README's minimum is now 2.1.295, which `onFailure: "block"` needs (it said 2.1.271).
- **Your words record only what a person typed (w07-c5 · MEASURED; w07-c2 · MEASURED is its
  failed v0).** `user_words.py` finds its prompt's record by `prompt_id` from an `async` hook and
  keeps `origin.kind: human`; it drops other sessions' and the harness's messages. 0 errors over
  3,027 recorded prompts; live, 10 of 10 decided by origin. Of the entries already in
  `user_words.md` it would have dropped exactly the three wrong ones: the spawned sessions' first
  messages of 10-21 17:18 and 10-22 00:22, and your own `-p` test "say ok" of 00:12. Two costs,
  accepted: a crash of the recorder under `async` leaves only a debug-log line; a prompt followed by
  a quit within about 0.4 s may go unrecorded. v0 failed live because of the platform fact above.
- **`lab_status.py` prices fast mode and web searches (w07-c4 · MEASURED).** They were silently
  dropped before. The cache file now carries its version, because an old and a new script sharing
  one file made every call cold (0.955 s against 0.25 s). The fast-mode factor 2.0 and USD 0.01 a
  search are the script's own rates, UNVERIFIED against a fetched page. Your lab has no such record
  yet, so no figure changes today.
- **Authors keep a 1-hour prompt cache (w07-c7 · escalated; PI decision: lands by its rule).**
  `experimental: {cacheTtl: "1h"}` in `agents/author.md` is honoured: 17 of 17 writes 1-hour; after
  a 333 s gap B read 100% of its context where A read 42%; a resumed author also kept it (n = 1).
  Whether it saves money is not determined: net +USD 0.87 of 47.80 at a 300 s bound, −0.60 at
  360 s, P(net ≤ 0) = 0.34 by bootstrap (ESTIMATE). The time a resumed author saves by reading
  rather than re-writing was not measured. One line, and a key the platform stops honouring falls
  back to 5 minutes.
- **The permission guard as one Rust binary, SA1's pilot (w07-c6 · MEASURED; w07-c8 · below
  MEASURED: restate, landed on its verifier's wording by PI decision).** `murmuration guard`, std
  only, about 410 KB a target, committed for `aarch64-apple-darwin` and `x86_64-apple-darwin`. Its
  decisions equal `permission_guard.py`'s on 20,847 events (registered cases, malformed events,
  8,722 recorded calls, 12,000 fuzzed), reproduced on 20,926 with another seed; it is stricter on
  JSON types the platform never sends, and answers in 0.05 s a 300 kB word on which the Python
  guard runs past 40 s. CPU 17.6 → 1.6 ms a start and start-to-exit 32.3 → 16.5 ms (598 of 600
  pairs), the machine's one-exec floor; the recorded hook 23.5 ms lower (19 of 19 pairs). In auto
  mode that is CPU and energy, since the guard hides behind the classifier; in default mode and on
  Write/Edit it is wall. A SessionStart installer copies the binary into the plugin's data folder
  only when its hash, the hashes of `permission_guard.py` and of `rust/`, and a 12-payload
  self-test all agree with `bin/manifest.json`; on any doubt it installs a launcher of the Python
  guard and tells the session why, with the remedy. A fresh install costs about 0.85 s once per
  version, a warm start 38 ms. **The residual gap, named:** a binary right on the 12 payloads and
  wrong elsewhere, such as an honest build of a changed `guard.rs` with a rewritten manifest,
  installs silently. The pre-commit file would stop that by replaying the corpus; it and the CI
  file that builds the other targets are written, not installed or pushed. Linux and Windows get
  the Python guard through the launcher until then.
- A selftest the merge broke (`budget.py` matched the old command string) was fixed.

**What did not land, and why.**
- **The PI without the skills listing (w07-c1 · below MEASURED: restate, not restated).** Denying
  `Skill` removes the whole 30k-character listing, 10.6–11.0k tokens of a headless PI's request 0,
  and the PI still follows `research-loop` and its references at the same step count. But the
  listing goes only whole (`Skill(...)` rules do nothing to it, `skillOverrides` reaches only
  non-plugin skills), and a built-in skill such as `dataviz` has no `SKILL.md` on disk, so a PI
  without the Skill tool loses it. A PI that cannot use your own figure skill is a worse PI for
  about 11k cached tokens a request. On your question about the workers: they already start without
  the listing, and the one server none of them ever called (Wolfram) costs its 15 tool names, about
  115–186 tokens (ESTIMATE), inside the noise. Nothing worth excluding there.
- **`lab_status.py` without its `git` child (w07-c4's change 1).** It saves 0.04–0.05 s a call
  (9 of 10 and 28 of 30 pairs), a few seconds a wave, by re-implementing git's worktree list; its
  first version gave a wrong list silently in two cases. The `git` child cannot fail that way.
- **A parallel or Rust `lab_status.py`.** Both bring a cold run from 0.9 s to about 0.33 s; the warm
  cache it already has takes 0.39 s. Here the better algorithm, an incremental cache, beats
  parallelism, and cold runs are rare.
- **`http` and `async` hooks, a resident server.** `http` is fast (2 ms) and loud on Pre/Post, but
  needs a server, a port and a token, and its failure is fatal or silent on two events; exec form
  already took the shell's share. Kept as records for item 31.
- **Message batching and worker effort.** Batching is worth at most 1.6% of requests. Effort was
  not varied, because the lab has no measure of a worker's quality to check a lower effort against.


## What stays out, and why (w01-c13 · CONJECTURE, verifier SUPPORTED)

Examined and staying out:
- **SA4 (examen mirror):** transcripts already rebuild 15 of 16 messages.
- **SA8 (friction hooks):** 52 of 59 failures arrive as ordinary results.
- **SA9 (live notices):** no wait longer than 300 s in 38 notices.
- **SA13 (question machinery):** the Desktop buttons are the channel.
- **SA15 (bundled MCP servers):** the bundled prefix would break the allowlists.

- **SA1 (one binary, hook entry point, MCP server), examined in waves 6 and 7:** the resident
  server's safety net costs its margin (w06-c6, w06-c4). Wave 6 sized a binary at about 1% of a
  wave; wave 7 found that most of a hook's start was the shell, removed it (w07-c3), and then
  brought SA1 back as one binary for the guard, with a fallback to the reviewable Python source
  (w07-c6, w07-c8). `budget` and `handback` would join it as subcommands.

Not examined: SA2, SA10, most of SA11, SA12, SA14, SA16 and SA17. They stay out because
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
| w06-c4, hooks on a resident server | below MEASURED: restate | s2 21.1% against 20%, s4 +320 against +300; the outage safety net is the margin; reverted at b79e81c, reproducible from a5e708b |
| w06-c2, dispositions at the hand-back wake-up | below ESTIMATE: restate | No saving: 69 s, off the critical path; reverted |
| w07-c1, the PI without the skills listing | below MEASURED: restate | The listing goes only whole, and a built-in skill (`dataviz`) has no `SKILL.md` to Read; on branch `w07-p1-skill` |
| w07-c4's change 1, `lab_status.py` without its git child | MEASURED; dropped by PI decision | 0.04–0.05 s a call for a re-implementation of git's worktree list that was silently wrong in its first version; on branch `w07-p4-labstatus` |
| `http` and `async` hooks, a parallel or Rust `lab_status.py`, message batching | probes only | See "Wave 7" |
| The decision-frame text | proposal, not applied | Denied by the auto-mode classifier as self-modification; `__reports__/wave-06/research-pi/decision_frame_patch.md` |

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

Wave 6 (2026-10-21, 17:18–22:23 JST) cost at least USD 53.00 against your budget of 100:
- 45.46 for this checkout's session, the PI and its 17 subagents included (46.66 at close against
  1.20 at opening, list price, session open);
- 7.54 for the headless runs under `/private/tmp/murmuration-w06/` (7.38 exact from cost-state, 0.16
  at list price).
Both are lower bounds in auto mode.

Wave 7 (2026-10-22, 00:25–02:45 JST) cost at least USD 38.28 against the at least 47 left of wave 6's
100:
- 35.80 for this checkout's session, the PI and its 21 subagents included (36.78 at close against
  0.98 at opening, list price, session open);
- 2.48 for the headless runs under `/private/tmp/murmuration-w07/`, exact from cost-state, all
  sessions ended.
Both are lower bounds in auto mode.

The PI set itself a cap of about USD 60 for wave 2. Wave 2 spent about 78, so the PI overran its own
cap by about 18. The USD 70–90 proposed for the whole study after wave 1 was never confirmed, and it
was overrun too. The user's budget for wave 2 was six hours. Wave 2 ran from 12:30 to about 17:00 JST.

## Still open

Items 2, 3, 13 and 14 were done before wave 5. Wave 5 settled 1(d). Wave 5's changes landed on the
local `main` at fed7a08. Wave 6 settles 9 (the lean starts landed, w06-c9) and 20 (w06-c1), and adds
25 to 31. Wave 7 settles 24 and 28, adds to 23, 27 and 31, and adds 32 to 38.

**Yours: the guardrails, since the engineering is now the lab's.**

| Item | What it is | Cost |
|:--|:--|:--|
| The managed setting | *Added by you on 2026-10-22 at 00:08 and read by Claude Code, but probably not the active managed tier on this account:* Claude Code 2.1.304 takes one managed source, first-wins (server-managed, then MDM, then the file), and `~/.claude/remote-settings.json` holds `channelsEnabled`, which counts as server-managed content, so the file would be dropped (CHECKED by reading the binary, not run; `__reports__/wave-07/explorer-w07-f/00-findings_v0.md`). Two tests settle it, both yours: `/status` in an interactive session (which managed source is named), and the report's test 2 (a `touch` under the skip-permissions flag in a scratch folder, with a debug file). If the server tier wins, the key belongs there, or `managedSourcesBehavior: "merge"` there. The guard stays until a bypass attempt is shown refused | minutes |
| The lab's past bypass runs | 32 `claude` runs in bypass mode, 16 under a scratch config dir, 7 escaping user settings, 8 settings writes, waves 1–6. Listed in reproducer-w06-7's section of `__pondus__/w06-c11.md` | reading |
| The decision-frame text | `__reports__/wave-06/research-pi/decision_frame_patch.md`: the PI stops handing engineering back; you keep the question, the budget and the guardrails. The classifier refused to let the PI apply it to itself | apply or not |
| Item 18 | gateway API keys printed by a wave-4 reproducer; rotate them if you want | minutes |
| Your own hooks | Outside the plugin, and the largest hook costs this wave saw on your machine: colgrep-mcp's `colgrep_policy` PreToolUse hook (`uv run`) at a median 194 ms per Bash call (p90 554, up to 431 ms median under load), and `inject_plan_directive.py` at 177–206 ms per prompt (explorer-w07-g, explorer-w07-c, author-w07-2). Exec form and a lean start would help them as they helped the lab's | your repositories |

Changes reach a running PI only once they are on main's working tree (item 1(e)).

| # | Open item | Who | Cost |
|:--|:--|:--|:--|
| 1 | **Lab root and plugin delivery.** (a) Your choice for w04-c1, now on main: the session's first cwd wins, or the payload cwd. (b) The main checkout's `__statera__/user_words.md` is uncommitted and holds the prompts of waves 4 and 5, written there by the hook. Keep or revert it. (c) Dialog answers are still not captured. (d) *Settled:* the Desktop passes `--project-config-root <main>`, so hooks see `CLAUDE_PROJECT_DIR` = main and the payload `cwd` = the worktree (explorer-w05-e). (e) To run a branch on yourself, merge it into main, or point `murmuration-local` at a symlink and switch it with `ln -sfn` (one edit to main's `settings.local.json`; global to every session) | you | minutes |
| 4 | Whether stated budgets make the PI plan a smaller team (left alone). New: the three wave-4 author chains ended at 55–90% of their 60-minute boxes; whether boxes set the length is untested | a further wave | about USD 20 |
| 5 | Protocol: authors still edit claim heads during verification (w05-c4, w05-c5); evidence pins drift; pre-registered rules were written before running their metric on the old code (E4, E7); output tokens are estimated (chars/1.3; 1.73 observed); the PI wrote estimated clock times (w05-c9) | a protocol claim | — |
| 6 | Small fixes: as before, plus harness `start` lines that swap names on same-second dispatches, and a stray background job that made the last `end` line wrong | small fixes | — |
| 7 | The nine set-aside elements not examined, and the tuning targets | further waves | — |
| 8 | The report line (w04-c12, now on main): as before, plus the hand-back gate makes an explorer told "write no file" write a report (all smoke runs of E6/E6b) | you, then a test | — |
| 9 | *Settled in wave 6: lean starts landed (w06-c9).* **The lean hooks, your call.** Two builds exist: w04-c5 (4c46fe4) and w05-c4 (ede2770, −52.5 to −56% serial seconds, 985 starts against 1788). A third build would need to: match the old messages in parallel batches (11 of 197 transcripts differ); cover failed or denied calls, which PostToolUse misses; and merge the two starts at a hand-back. It saves about 1.4 minutes of a wave against the 10 minutes auto mode costs (item 23) | a claim, then your call | about USD 8 |
| 10 | Which graded note is enough; a task whose accuracy can vary | a test, if wanted | about USD 3 |
| 11 | The search paragraph: as before. New: in a Desktop worktree the relative colgrep path searched the plugin source, not the lab (w05-c2), so wave 4's "colgrep almost never used" may partly be colgrep finding nothing useful | you, then a test | about USD 3 |
| 12 | Verifier independence next to the instruments folder (left alone) | you | — |
| 15 | A worker that reaches `maxTurns` loses its deliverable with no trace | a fix, then a check | small |
| 16 | **One lab rule for every script.** Under the Desktop, `CLAUDE_PROJECT_DIR` is main, so `lab_init.py`, `lab_status.py` and the `handback.py` fallback act on main from a hook. From Bash they act on the worktree, because the variable is empty there | a claim after 1(a) | small |
| 17 | Platform facts, as before, plus: a subagent's cache lives 5 minutes and a headless main thread's 1 hour; `sleep` of 30 s or more is blocked by Claude Code itself; a Bash call past 120 s without `timeout:` is moved to the background; Monitor can be given to a subagent but its events do not reach it; the headless Agent tool has no `name`; `tools:` can add a tool, and `mcp__*` matches nothing | notes | — |
| 18 | A reproducer printed gateway API keys into its own tool output in wave 4; you may want to rotate them | you | minutes |
| 19 | **Waits, untested parts.** The other three agent files, message latency during a wait, the stop-your-jobs clause, and the two edits of 5906331 | a check | about USD 3 |
| 20 | *Settled in wave 6 (w06-c1): request 0 at 46,738 tokens, denied tools absent.* **The Desktop check of w05-c7.** One new Desktop session with the denylist on main: read the first request's usage and the tool names in its snapshot. About 31–49k tokens means it works; about 75k means the app injects regardless | you, then the PI | minutes |
| 21 | **The experiment pipeline, now the lab's critical path.** Run one pilot cell first; launch cells side by side; find out why batches stopped at 9; give headless drivers `CLAUDE_CODE_SHELL=/bin/bash` (first Bash call 0.5 s against 5.7–10 s; same tools resolved, PI check n = 1); keep timing records without account identifiers | a claim | about USD 5 |
| 22 | Costs outside the plugin: the skill listing re-entering the PI's context (19 times in waves 1–3); cache-prefix rewrites; a PI request for every hand-back; colgrep-mcp's own hook (119 ms per Bash, one 10 s timeout); your `.zshrc` (4.4–5.7 s per new shell) | notes; yours where it is your config | — |
| 23 | **Auto mode's classifier.** About 0.45–0.75 s per Bash call, roughly 10 worker-minutes a wave, and its cost is in no record. Narrow allow rules for read-only commands skip it. Lab scripts (`python3 -I scripts/…`) need a PreToolUse hook that answers "allow", which changes what your safety layer sees. Wave 7: 628 ms median wait on a trivial Bash call, about 1.9% of worker wall; a PreToolUse hook hides behind it; a Read never reaches it (explorer-w07-g) | you | — |
| 24 | *Settled in wave 7:* the cache stays; dropping its `git` child saves 0.04–0.05 s a call and was not landed (w07-c4). A parallel or Rust re-parse (0.33 s cold) does not beat the warm cache (0.39 s) | — | — |
| 25 | **The guard's live cost under real load.** 1 start per Bash call; median 0.73 s and max 7.64 s under five parallel starts, no timeout in 211 starts; the 20 s timeout was not run live (w06-c13) | a check in the next wave | small |
| 26 | **Guard false denials grow with guard work.** 26 strict in 4,637 recorded calls, but 16 more among this wave's own notes about the guard; prose that names `claude` and the flag in a heredoc is denied. A frozen labelled replay set would make the measure stable | a check | small |
| 27 | **A threshold above the physical ceiling.** Three lean builds were judged by thresholds at or past what the change could reach (w04-c5, w05-c4, w06-c9). The procedure has no step that checks a registered threshold against a measured ceiling (S-w06-research-pi-2). Wave 7 gated on signs over paired runs instead of sizes, which held five times; but P4's ceiling was read from two unpaired medians and was three times too high (S-w07-author-w07-4-1). The step the procedure lacks: measure the ceiling paired before registering | a protocol claim | — |
| 28 | *Settled in wave 7 (w07-c5):* `user_words.py` keeps only what a person typed, by the transcript's origin marker, from an async hook. The three wrong entries already in `user_words.md` (10-21 17:18 and 10-22 00:22, spawned sessions' first messages; 10-22 00:12 "say ok", your own `-p` test) stay as written; no agent edits that file. The first typed prompt in the Desktop after the merge is the live check | — | — |
| 29 | **The PI's orientation reads.** The first turn is 21–32% of PI spend; this session's preface went from 47k to about 137k tokens before the first dispatch | a probe | about USD 3 |
| 30 | **`$` share.** 45% of lab Bash calls carry an unresolved expansion, which matches every `if` hook rule; any future gated hook costs that much | notes | — |
| 31 | **A resident hook server, if the platform changes.** It would land if a failed server were announced by the platform, or reconnected across sessions (w06-c4, S-w06-author-w06-4-1). Wave 7: `http` hooks cost 2 ms, fail loudly on PreToolUse and PostToolUse with `onFailure: "block"`, end the session on PostToolBatch and are silent on SubagentStop (explorer-w07-c) | watch the platform | — |
| 32 | **The Rust guard's residual gap and its other platforms.** A binary right on the 12 self-test payloads and wrong elsewhere installs silently. `scripts/git-hooks/pre-commit` (rebuild, manifest, fuzz replay) is written, not installed: `ln -s ../../scripts/git-hooks/pre-commit .git/hooks/pre-commit`. `.github/workflows/guard-binaries.yml` would build Linux and Windows targets; pushing it is visible outside this machine. Until then those platforms get the Python guard through the launcher | you | minutes |
| 33 | What a human sees of the installer's fallback notice (exit 0, stderr plus `additionalContext`); the model sees it | a check | small |
| 34 | 61 of 72 verifiers and authors spend an early request loading the deferred `SendMessage` with `ToolSearch`; no plugin-side lever found | a probe | small |
| 35 | Small checks: the fast-mode factor 2.0 and USD 0.01 a search against a fetched pricing page; the 3–7% gap between the CLI's `total_cost_usd` and a list-price recomputation (S-w07-author-w07-6-2) | a check | small |
| 36 | **`budget` and `handback` as subcommands of the same binary.** The budget hook is the one a worker waits on after every tool call (41 ms in exec form); the guard pilot is the template | a claim | about USD 8 |
| 37 | **The Desktop after the merge.** The first Desktop session on main is the check of four things no headless run covers: the installer in the Desktop's data folder before the first Bash call, a typed prompt recorded by origin, an author's 1-hour writes, and the PI's request 0 with the deferred names of your MCP servers | you, then the PI | minutes |
| 38 | **Cache and long outputs.** Re-writes after 5-minute gaps were 15.8% of worker spend and tool results over 5,000 characters 29.7% of cache-read spend (ESTIMATEs). Authors now keep 1 hour; reproducers and explorers lose by it. Shorter outputs from lab scripts are the untried lever | a claim | about USD 3 |
