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
