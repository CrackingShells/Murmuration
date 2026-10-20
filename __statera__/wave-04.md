# Wave 04

opened: 2026-10-20

## The user's sentence this wave serves

The user's 09:27 prompt is not in this checkout's `__statera__/user_words.md`: the prompt hook
appended it to the main checkout's file (see "Item 1" below). Quoted from this session's
transcript:

> In this order, as far as the budget goes: 1. Open item 1, the Desktop probe. [...] 2. Open item 8.
> [...] 3. Open item 10, compliance or anxiety. [...] 4. Open item 11, search and reuse of
> `__instrumenta__/`. [...] 5. Open item 9, the hooks' own cost. [...] "Everything has a cost.
> things that look fast (like 100ms) piles up [...] the system itself must be frugal [...] be
> lean." Measure first, then make the hooks lean. 6. Open item 14, the small fixes, if budget is
> left.

> Leave alone: Open item 12 [...] Open item 4 [...]

> Budget: USD 100 of total spend for this wave, and stop by 12:00 JST. Pre-register each
> experiment's metrics and decision rule in a committed file before running it.

> Method note: following the teachings of the lab research loop skill, the items above are open
> puzzles not a checklist.

## What does not add up

- The prompt hook was built to keep the user's words in the lab the team works in. In every
  Desktop worktree session so far it wrote them somewhere else, and nobody has seen why.
- The report check and the budget notes pull an explorer in opposite directions past 100%: the
  note says "hand back now", the check refuses a hand-back without a report.
- Five of eight wave-3 workers stopped at 75–99% of their budget. A worker cannot know its spend
  without the notes, so the notes are the obvious cause; whether that is the budget working or the
  budget frightening is open.
- The scripts rule was only ever exercised in labs where no script existed yet.
- A hook that costs ~0.1 s runs on every tool call of every agent, the PI's included, and does
  nothing for the PI.

## Item 1: what this Desktop session shows (PI measurements)

All [source: this session, `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-4-3417be/c533f1c6-c56e-4c8d-b6ff-e90c3ddea2f4.jsonl`, and the Desktop log `~/Library/Logs/Claude/main.log` lines 58263–58267]:
- The Desktop created the worktree and started the session in it at 09:27:17 ("Starting local
  session … in …/murmuration-wave-4-3417be"). The transcript lives under the worktree's project
  folder, and its first 56 records carry `cwd` = the worktree.
- The worktree has its own lab: `__statera__/` is tracked in git, so a fresh worktree carries it.
  In wave 1 the worktree had no lab at first; now it does.
- The 09:27 prompt was nevertheless appended to the **main checkout's**
  `__statera__/user_words.md` (main now shows `M __statera__/user_words.md`, uncommitted, written by
  the hook). The worktree's file ends at the 23:51 prompt of 2026-10-19.
- `user_words.py` takes `CLAUDE_PROJECT_DIR`, then the payload `cwd`. With the session cwd = the
  worktree, the landing in main means the hook's `CLAUDE_PROJECT_DIR` was the main checkout, or
  its payload `cwd` was. I could not dump the hook environment: hooks added to
  `.claude/settings.local.json` and a project agent with its own hooks were both not picked up by
  the running session (0 records), and `ps -E` shows no environment on this machine. The Claude
  process runs with `--setting-sources=user,project,local` and protects the **main checkout's**
  `.claude/settings*.json`, `.claude/agents/**` and `.mcp.json` in `--disallowedTools`: the
  Desktop treats the main checkout as the project root. That fits CLAUDE_PROJECT_DIR = main
  (CONJECTURE, strongly supported; not dumped).
- The session cwd follows the Bash tool: one `cd` into the main checkout moved 7 transcript
  records and the app's "primary working directory" to main until I `cd`'d back. A cwd-first rule
  would follow the shell (w01-c10's risk, seen here live).
- Dialog answers: an `AskUserQuestion` answer is a tool result, not a prompt, so the
  UserPromptSubmit hook never sees it; nothing in the plugin captures it. Testing a capture needs
  the user to answer a dialog; not done tonight.

Decision: w01-c10 is not revived as filed (cwd first follows the shell). A new claim w04-c1
resolves the lab from the session's first recorded `cwd` (the transcript's first record), then
`CLAUDE_PROJECT_DIR`.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| author-w04-1 | author | w04-c1: lab root from the session's first recorded cwd (user_words.py, resume_brief.py); USD 4, 30 min | yes; MEASURED, bound fixed in the exchange (37de695) |
| reproducer-w04-1 | reproducer | verify w04-c1 | SUPPORTED; ran the resume and EnterWorktree cases |
| author-w04-2 | author | w04-c2/c3 (E1, E2); resumed with raises for w04-c8/c9 (E1b, E2b), w04-c11, w04-c12 (E1c); USD 12 + 6 + 3 | yes, every time; headless runs USD 11.79 + 4.52 + 0.95 by `total_cost_usd` |
| reproducer-w04-2 | reproducer | verify w04-c2 | OVERSTATED (sizing, attribution) |
| reproducer-w04-3 | reproducer | verify w04-c3 | OVERSTATED (task could not separate the readings; wave-3 cap) |
| reproducer-w04-8 | reproducer | verify w04-c8, then w04-c12 | w04-c8 SUPPORTED (parser defect found); w04-c12 SUPPORTED, on its thresholds |
| reproducer-w04-9 | reproducer | verify w04-c9, then w04-c11 | w04-c9 OVERSTATED; w04-c11 SUPPORTED |
| author-w04-3 | author | w04-c4 (E3); resumed for w04-c7 (E3b), w04-c10 (E3c) and three restatements; USD 8 + 5 + 3 | yes; headless runs USD 4.74 + 3.20 + 0.56 |
| reproducer-w04-4 | reproducer | verify w04-c4 | ESCALATE (s2 coding) |
| reproducer-w04-7 | reproducer | verify w04-c7 | ESCALATE (targets on screen; version; Q not followed) |
| reproducer-w04-10 | reproducer | verify w04-c10 | ESCALATE (pass at the rule's edge) |
| author-w04-4 | author | w04-c5 (E4, measure then lean the hooks); USD 8, 60 min | yes; at its time limit, about USD 5 by its own reading |
| reproducer-w04-5 | reproducer | verify w04-c5, paired timing | SUPPORTED; long-worker criterion not met (48.4%) |
| author-w04-6 | author | w04-c6 (item 14); USD 3, 30 min | yes; two bugs fixed in the exchange (c3bfe2c) |
| reproducer-w04-6 | reproducer | verify w04-c6 | SUPPORTED at c3bfe2c (OVERSTATED at b42f9f2) |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|
| w04-c1 | user_words.py and resume_brief.py find the lab from the session's first recorded cwd | MEASURED (on the branch) |
| w04-c2 | E1: with a brief that names the report, no deny; line not proposed | superseded by w04-c8 |
| w04-c3 | E2: compliance by the rule; task cannot separate the readings | superseded by w04-c9, then w04-c11 |
| w04-c4 | 46 scripts: workers look by `ls`; strict reuse 7 of 15; inconclusive | escalated; restated by PI decision |
| w04-c5 | lean hooks: main thread -61%, long worker -48.4%, identical replay | MEASURED; not proposed by E4, set aside at 4c46fe4 |
| w04-c6 | lab_init index message; briefs keep helper code a file | MEASURED (on the branch) |
| w04-c7 | 429 scripts, targets on screen: cut `ls` sufficed; Q not proposed | escalated; restated by PI decision |
| w04-c8 | E1b: line B' removes denies and overshoot; shape 1 of 3; not proposed | MEASURED |
| w04-c9 | E2b as first filed | superseded by w04-c11 |
| w04-c10 | targets past the cut: finding 4 of 6, at the rule's edge, by `ls \| grep` | escalated; restated by PI decision |
| w04-c11 | with notes, workers change what they do at the budget; without, they run to 1.5-2 B | MEASURED |
| w04-c12 | E1c: line B'' with the template path; proposed by the rule, every condition on its threshold | MEASURED (line on the branch, ff2d5da) |

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|
| S-w04-author-w04-1-1 | parked: open item 17 (platform resets a launch CLAUDE_PROJECT_DIR) in __statera__/synthesis.md |
| S-w04-author-w04-1-2 | parked: open item 1 (Desktop transcript at the first prompt) in __statera__/synthesis.md |
| S-w04-author-w04-1-3 | parked: open item 16 (one lab rule for every script) in __statera__/synthesis.md |
| S-w04-author-w04-1-4 | followed: w04-c1 (scope); parked: open item 17 in __statera__/synthesis.md |
| S-w04-author-w04-1-5 | followed: w04-c5 (the verifier measured in interleaved pairs) |
| S-w04-author-w04-1-6 | parked: open item 1 (your choice: first cwd or payload cwd) in __statera__/synthesis.md |
| S-w04-author-w04-2-1 | followed: w04-c11 (no cap); parked: open item 17 in __statera__/synthesis.md |
| S-w04-author-w04-2-2 | parked: open item 15 (maxTurns loses the deliverable silently) in __statera__/synthesis.md |
| S-w04-author-w04-2-3 | followed: w04-c8 (E1 restated) |
| S-w04-author-w04-2-4 | followed: w04-c12 |
| S-w04-author-w04-2-5 | followed: w04-c11 (E2b) |
| S-w04-author-w04-2-6 | parked: open item 5 (hand-backs quote the last note) in __statera__/synthesis.md |
| S-w04-author-w04-2-7 | parked: open item 6 (an uppercase name truncates silently) in __statera__/synthesis.md |
| S-w04-author-w04-2-8 | followed: w04-c12 |
| S-w04-author-w04-2-9 | parked: open item 10 (a task whose accuracy can vary) in __statera__/synthesis.md |
| S-w04-author-w04-2-10 | parked: disclosed in w04-c8 and w04-c11 (USD 0.017 over the cap) |
| S-w04-author-w04-2-11 | parked: open item 8 (B'' still let 1 of 3 be denied) in __statera__/synthesis.md |
| S-w04-author-w04-3-1 | parked: open item 11 in __statera__/synthesis.md |
| S-w04-author-w04-3-2 | parked: open item 11 (Glob absent in headless sessions) in __statera__/synthesis.md |
| S-w04-author-w04-3-3 | parked: open item 17 (a worker's background job keeps `claude -p` alive) in __statera__/synthesis.md |
| S-w04-author-w04-3-4 | parked: open item 11 (overwrite with numbered names) in __statera__/synthesis.md |
| S-w04-author-w04-3-5 | parked: open item 6 (a one-word hand-back) in __statera__/synthesis.md |
| S-w04-author-w04-3-6 | followed: w04-c4 (exploratory arm C) |
| S-w04-author-w04-3-7 | parked: open item 17 ("Not logged in" on parallel launches) in __statera__/synthesis.md |
| S-w04-author-w04-3-8 | parked: open item 11 (extend in place or by copy) in __statera__/synthesis.md |
| S-w04-author-w04-3-9 | followed: w04-c7 (precondition probed; 336 set kept out) |
| S-w04-author-w04-3-10 | followed: w04-c7 (Q not proposed) |
| S-w04-author-w04-3-11 | followed: w04-c10 (targets renamed past the cut) |
| S-w04-author-w04-3-12 | parked: open item 17 in __statera__/synthesis.md |
| S-w04-author-w04-3-13 | parked: open item 11 (workers use `ls | grep`, the paragraph names colgrep) in __statera__/synthesis.md |
| S-w04-author-w04-3-14 | followed: w04-c10 (scope) |
| S-w04-author-w04-4-1 | followed: w04-c5 (posix_spawn timer; verifier's pairs) |
| S-w04-author-w04-4-2 | followed: w04-c5 (verifier's 420 interleaved pairs) |
| S-w04-author-w04-4-3 | parked: open item 9 in __statera__/synthesis.md |
| S-w04-author-w04-4-4 | parked: open item 9 (an editable install in your conda base slows every Python start) in __statera__/synthesis.md |
| S-w04-author-w04-4-5 | followed: w04-c5 (offset read) |
| S-w04-author-w04-4-6 | parked: method note (wave-3 transcripts sit under the worktree's folder only) |
| S-w04-author-w04-4-7 | parked: open item 17 (UserPromptSubmit also fires for queued notifications; user_words.py skips them) in __statera__/synthesis.md |
| S-w04-author-w04-4-8 | parked: open item 6 (hand-back files carry an absolute transcript path) in __statera__/synthesis.md |
| S-w04-author-w04-4-9 | parked: open item 9 (mutation tests for the lean version) in __statera__/synthesis.md |
| S-w04-author-w04-4-10 | parked: open item 9 (drop the per-call PostToolUse start) in __statera__/synthesis.md |
| S-w04-author-w04-6-1 | followed: w04-c6 |
| S-w04-author-w04-6-2 | parked: open item 6 in __statera__/synthesis.md |
| S-w04-author-w04-6-3 | parked: open item 6 (the `/lab-status` warning wording) in __statera__/synthesis.md |
| S-w04-reproducer-w04-1-1 | followed: w04-c1 (resume statement withdrawn) |
| S-w04-reproducer-w04-1-2 | parked: open item 1 in __statera__/synthesis.md |
| S-w04-reproducer-w04-1-3 | parked: open item 16 in __statera__/synthesis.md |
| S-w04-reproducer-w04-1-4 | followed: w04-c1 (bound fixed at 37de695); parked: open item 5 (evidence pins) in __statera__/synthesis.md |
| S-w04-reproducer-w04-1-5 | parked: open item 17 (transcript-format dependency) in __statera__/synthesis.md |
| S-w04-reproducer-w04-10-1 | followed: w04-c10 (restated at the rule's edge) |
| S-w04-reproducer-w04-10-2 | followed: w04-c10 (name seen 5 of 6) |
| S-w04-reproducer-w04-10-3 | parked: open item 11 in __statera__/synthesis.md |
| S-w04-reproducer-w04-10-4 | parked: open item 17 in __statera__/synthesis.md |
| S-w04-reproducer-w04-10-5 | parked: open item 17 (workers read outside the lab) in __statera__/synthesis.md |
| S-w04-reproducer-w04-10-6 | parked: open item 11 in __statera__/synthesis.md |
| S-w04-reproducer-w04-2-1 | followed: w04-c8 (E1 restated: the task fit the budget) |
| S-w04-reproducer-w04-2-2 | followed: w04-c8 (brief attribution CONJECTURE) |
| S-w04-reproducer-w04-2-3 | parked: method note (two readings of "first hand-back"; final fractions agree) |
| S-w04-reproducer-w04-2-4 | followed: w04-c8 and w04-c12 (uncapped XB-shaped cells run) |
| S-w04-reproducer-w04-2-5 | parked: open item 15 in __statera__/synthesis.md |
| S-w04-reproducer-w04-3-1 | parked: open item 17 (the token counter every worker sees) in __statera__/synthesis.md |
| S-w04-reproducer-w04-3-2 | followed: w04-c11 (bases named) |
| S-w04-reproducer-w04-3-3 | followed: w04-c11 (E2b's added clause) |
| S-w04-reproducer-w04-3-4 | parked: open item 9 (a hook_cancelled in ux-c1) in __statera__/synthesis.md |
| S-w04-reproducer-w04-3-5 | parked: harmless count (the first request has no attachment) |
| S-w04-reproducer-w04-3-6 | parked: open item 10 (which graded note suffices) in __statera__/synthesis.md |
| S-w04-reproducer-w04-4-1 | followed: w04-c4 (recoded, restated) |
| S-w04-reproducer-w04-4-2 | parked: open item 11 (near-fit task design) in __statera__/synthesis.md |
| S-w04-reproducer-w04-4-3 | followed: w04-c4 (strict reading stated first) |
| S-w04-reproducer-w04-4-4 | parked: open item 11 (listing every lab folder at start) in __statera__/synthesis.md |
| S-w04-reproducer-w04-4-5 | parked: open item 5 (evidence pins) in __statera__/synthesis.md |
| S-w04-reproducer-w04-5-1 | parked: open item 9 (gate reads its socket byte by byte) in __statera__/synthesis.md |
| S-w04-reproducer-w04-5-2 | followed: w04-c5 |
| S-w04-reproducer-w04-5-3 | parked: open item 9 in __statera__/synthesis.md |
| S-w04-reproducer-w04-5-4 | followed: w04-c5 (replay list committed) |
| S-w04-reproducer-w04-5-5 | parked: open item 18 (keys printed in a tool output) in __statera__/synthesis.md |
| S-w04-reproducer-w04-5-6 | parked: open item 9 (stale header text) in __statera__/synthesis.md |
| S-w04-reproducer-w04-6-1 | followed: w04-c6 |
| S-w04-reproducer-w04-6-2 | followed: w04-c6 |
| S-w04-reproducer-w04-6-3 | followed: w04-c6 |
| S-w04-reproducer-w04-6-4 | parked: open item 6 in __statera__/synthesis.md |
| S-w04-reproducer-w04-7-1 | followed: w04-c10 (E3c) |
| S-w04-reproducer-w04-7-2 | parked: method note (run-folder names) |
| S-w04-reproducer-w04-7-3 | followed: w04-c7 (restated) |
| S-w04-reproducer-w04-7-4 | parked: method note (s3 is an upper bound) |
| S-w04-reproducer-w04-7-5 | followed: w04-c10 |
| S-w04-reproducer-w04-7-6 | parked: open item 11 in __statera__/synthesis.md |
| S-w04-reproducer-w04-8-1 | followed: w04-c12 (template path) |
| S-w04-reproducer-w04-8-2 | followed: w04-c8 (parser fixed at 1acb430) |
| S-w04-reproducer-w04-8-3 | followed: w04-c8 (head) |
| S-w04-reproducer-w04-8-4 | parked: open item 8 in __statera__/synthesis.md |
| S-w04-reproducer-w04-8-5 | parked: disclosed in w04-c8 |
| S-w04-reproducer-w04-8-6 | parked: open item 8 in __statera__/synthesis.md (thresholds met exactly, no side-by-side A) |
| S-w04-reproducer-w04-8-7 | parked: open item 8 in __statera__/synthesis.md (the report check accepts an off-template report) |
| S-w04-reproducer-w04-8-8 | parked: open item 8 in __statera__/synthesis.md (rows in the hand-back, not the report) |
| S-w04-reproducer-w04-9-1 | followed: w04-c11 |
| S-w04-reproducer-w04-9-2 | parked: open item 9 (arm C logs blocks it never sent) in __statera__/synthesis.md |
| S-w04-reproducer-w04-9-3 | parked: method note (cost spread across identical runs) |
| S-w04-reproducer-w04-9-4 | followed: w04-c11 |
| S-w04-reproducer-w04-9-5 | parked: open item 5 (hand-backs' resume estimates) in __statera__/synthesis.md |
| S-w04-reproducer-w04-9-6 | parked: method note (one file per call loosely kept) |
| S-w04-research-pi-1 | followed: w04-c1 |
| S-w04-research-pi-2 | parked: open item 6 (parallel dispatches log the default budget) in __statera__/synthesis.md |
| S-w04-research-pi-3 | followed: w04-c1 (cited as CONJECTURE) |

## Notes

- Pre-registration: `__reports__/reflective_run/w04/00-experiment_protocol_v0.md`, committed
  before any run.
- Spend cap for this wave: USD 100 (the user's), stop by 12:00 JST. PI's plan: about 55 for
  authors and their runs, 15 for verifiers, the rest for the PI's own turns and slack.
- Registry md5 at start: `8d71e8c0f33b7e927133e7e44194de37`.
- **PI decision on the ESCALATE of w04-c4** (reproducer-w04-4, 10:2x): the head is restated in place
  to the verifier's figures. Workers listed `__instrumenta__/` before writing in 14 of 15 runs, all
  by `ls`; colgrep `search` 0 of 15. Strict reuse (run as is or edited in place) 7 of 15. Under the
  strict reading fixed in the 10:10 addendum, before the verifier read the claim, E3 is
  INCONCLUSIVE. Three near-fit runs the author first coded as "extension by copy" read only first
  lines and wrote a new loop. At 46 scripts `ls` is the cheaper search, so E3 did not test the
  user's condition; E3b (300 scripts, pre-registered 10:10) does.
- **w04-c1 is SUPPORTED, with a choice left open for the user**: the session's first cwd wins
  over the payload cwd. This gains the shell-`cd` case (seen live in this session) and loses the
  "EnterWorktree mid-session" case (reproducer-w04-1). Neither has been counted in real use.
  `budget.py`/`handback.py` still follow the live cwd and `lab_status.py`/`lab_init.py` take
  CLAUDE_PROJECT_DIR first, so the lab is found by three different rules. One rule for all of them
  is a follow-up after w04-c5 (which owns those files) lands.
- **PI decision on the ESCALATE of w04-c7** (reproducer-w04-7): the head is restated in place to
  the verifier's statement. At 429 scripts with both targets among the first 10 names, a cut
  listing sufficed; colgrep `search` 1 of 6 (P) and 0 of 6 (Q); strict reuse 3 of 6 per arm, all on
  the fit task; Q is not proposed, and why Q did not change behaviour is untested. Since finding was
  not tested, E3c (targets past position 200, pre-registered 05c0bbf) runs as w04-c10.
- **PI decision on w04-c5's straddle** (author-w04-4 asked): E4's rule is read as written. The
  verifier's own paired measurement of long-worker wall time decides; it is not redefined after the
  fact. If it straddles again, the claim goes to the user as "met for the main thread, at the edge
  for long workers".
- **PI decision on the ESCALATE of w04-c10** (reproducer-w04-10): title and scope restated in place
  (3a5429a) to "at the rule's edge": finding 4 of 6, the lowest passing count, resting on one
  near-fit run (pt2r2); fit 3 of 3, near fit 1 of 3; found by `ls | grep -i`, colgrep 0 of 6.
- **PI decisions on w04-c2 and w04-c3** (both OVERSTATED): no in-place restatement; w04-c8 and w04-c9
  supersede them, each opening with the restated earlier result.
- **PI decision on w04-c5** (reproducer-w04-5: SUPPORTED; long-worker wall down 48.4%, interval
  47.9–49.1%): E4's rule is not met, so the lean hooks are not proposed. They are set aside on the
  branch tip (4c46fe4), as wave 2 did with a failed rule. Revert that commit to take them. All
  selftests and `claude plugin validate .` pass after the set-aside.
- **w04-c12 lands on the branch** by E1c's rule (ff2d5da). Every condition sits exactly on its
  threshold, against a reused arm A; the user decides.
- **Left for the user, not touched:** the main checkout's uncommitted `__statera__/user_words.md`
  (the shipped hook wrote the 09:27 prompt there). The registry md5 was unchanged at close.
- **Spend at close:** this checkout's sessions USD 26.63 (list price, a lower bound; `/lab-status`
  162.93 − 136.30); headless runs outside the repository USD 26.52 (exact, cost-state). Total at least
  53.15 against the user's 100. The PI's plan was about 70.

closed: 2026-10-20
- `/lab-status` warns that w04-c1's `supersedes:` line carries a parenthesis after the id, so
  w01-c10 still shows as "below CONJECTURE: restate" instead of superseded. That is the author's
  head and is left as filed (open item 5).
