## S-w01-research-pi-1
The `UserPromptSubmit` hook (`scripts/user_words.py`) stored a `<system-reminder>` block, injected
by the desktop app to say the session runs in a git worktree, as part of the user's verbatim words.
The pasted-content wrapper `<pasted_content id=…>` was stored too. The file that promises "prompts
as the user typed them" now holds platform text the user never typed.
refs: __statera__/user_words.md (entry 2026-10-19 10:56, first five lines); scripts/user_words.py

## S-w01-research-pi-2
This session was opened by the desktop app in a worktree on `main` (9ecbc6a), which has no lab; the
lab lives on branch `roadmap/reflective_run` in the main checkout. The hook nevertheless appended
the prompt to the main checkout's `__statera__/user_words.md`, and the app then refused my writes to
the main checkout. I fast-forwarded the worktree branch to `roadmap/reflective_run` and copied the
hook's entry over. The lab state is git-tracked files in one checkout; a session started anywhere
else (worktree, other branch) does not see it, and nothing told me. Also: `__scrupuli__/` and
`__pondus__/` did not exist after checkout, because git does not track empty directories.
refs: git log of claude/murmuration-system-optimization-8cff9e (ff to 79fb6cf); main checkout `git diff __statera__/user_words.md`

## S-w01-research-pi-3
`/lab-status` reported "no usage records" for spend: `scripts/lab_status.py` reads transcripts from
`~/.claude/projects/-Users-hacker-Documents-src-CrackingShells-Murmuration`, while this session's
transcript is under the worktree's project folder `-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e`.
Cost tracking keyed on the project path misses every worktree session.
refs: output of `python3 scripts/lab_status.py` at 2026-10-19 ~11:00; scripts/lab_status.py

## S-w01-research-pi-4
Only `explorer` sets `maxTurns` (60). Author, reproducer and proof-adversary have none, although
v5 listed `maxTurns` as the pair-loop backstop ("Pair loops never converge → the verifier owns
termination; maxTurns").
refs: agents/*.md frontmatter; __reports__/genesis/12-architecture_v5.md §Risks

## S-w01-research-pi-5
The second prompt of this run (11:04, the user confirming the budget) was again appended to the
**main checkout's** `__statera__/user_words.md`, not to this worktree's lab. So the hook resolves
the project as `CLAUDE_PROJECT_DIR` (the repository the app was opened on), not the session's
worktree: in a desktop-app worktree session the lab's record of the user's words never reaches the
lab that is running. The 11:04 entry also quotes my own sentence back (`> I set a working budget…`),
which the user's reply-to-quote UI inserted; it is stored as the user's words.
refs: /Users/hacker/Documents/src/CrackingShells/Murmuration/__statera__/user_words.md (entry 2026-10-19 11:04); scripts/user_words.py `project_root`

## S-w01-research-pi-6
The platform already hands the PI a per-run ledger line: the task-notification for explorer-w01-e
carried `subagent_tokens 219458, tool_uses 57, duration_ms 467684`. That is most of v5's
`__expensa__` run event (SA3), delivered to the main thread for free, yet the lab writes it nowhere
and `/lab-status` re-derives spend from transcripts by a path that misses worktree sessions
(S-w01-research-pi-3). Is the notification's `usage` block also visible to a hook
(PostToolUse on the Agent tool, SubagentStop), so it could be appended without the PI's help?
refs: this run's transcript, task-notification for task a53e063b007b7a428 (explorer-w01-e)

## S-w01-research-pi-7
My quick count of non-sidechain user entries in 82e8a947 (filtering only the obvious wrappers) gives
69; explorer-w01-e reports 28 human prompts. The difference is what counts as "the human's words",
the same question as S-w01-research-pi-1. explorer-w01-d is counting independently; compare.
refs: inline script in this run (PI, ~11:15); __reports__/reflective_run/w01/explorer-w01-e/prompts_82e8a947.json

## S-w01-research-pi-8
explorer-w01-c hit `maxTurns: 60` after 62 tool uses, 281k tokens and 10.4 minutes, and returned
nothing: no report, no puzzle file; the platform said only "stopped at its 60-turn limit". The
turn limit is a hard stop with no wrap-up turn, so the work is stranded until the PI notices and
resumes it. This is exactly the case v5's SubagentStop presence gate (SA6) targeted, but in a
different shape: the missing thing is not a label or a puzzle but the whole deliverable. Does
SubagentStop fire at a maxTurns stop, and can a hook there (or the brief) make an agent write as it
goes, so a limit stop leaves a usable partial report?
refs: this run's transcript, task-notification for task a1f4458ce75dacdec (explorer-w01-c); agents/explorer.md `maxTurns: 60`
