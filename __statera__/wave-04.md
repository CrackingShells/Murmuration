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

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- Pre-registration: `__reports__/reflective_run/w04/00-experiment_protocol_v0.md`, committed
  before any run.
- Spend cap for this wave: USD 100 (the user's), stop by 12:00 JST. PI's plan: about 55 for
  authors and their runs, 15 for verifiers, the rest for the PI's own turns and slack.
- Registry md5 at start: `8d71e8c0f33b7e927133e7e44194de37`.
