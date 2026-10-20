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
| author-w04-1 | author | w04-c1: lab root from the session's first recorded cwd (user_words.py, resume_brief.py); USD 4, 30 min | |
| author-w04-2 | author | w04-c2 (E1, report line in explorer.md) and w04-c3 (E2, notes-off control); USD 12 + runs ≤ 12, 60 min | |
| author-w04-3 | author | w04-c4 (E3, search and reuse in a lab with ≥ 40 scripts); USD 8 + runs ≤ 8, 60 min | |
| author-w04-4 | author | w04-c5 (E4, measure then lean the hooks; owns budget.py, handback.py, hooks.json, lab_status.py); USD 8, 60 min | |
| author-w04-6 | author | w04-c6 (item 14: lab_init message, briefs sentence); USD 3, 30 min | yes; filed MEASURED at b42f9f2, fixed two bugs found in the exchange (c3bfe2c) |
| reproducer-w04-6 | reproducer | verify w04-c6 | SUPPORTED at c3bfe2c (changed from OVERSTATED at b42f9f2) |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|
| w04-c6 | lab_init says whether the colgrep index was built, current, empty, or the parent's; briefs keep helper code a file | MEASURED (c3bfe2c, cee84af) |

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

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
