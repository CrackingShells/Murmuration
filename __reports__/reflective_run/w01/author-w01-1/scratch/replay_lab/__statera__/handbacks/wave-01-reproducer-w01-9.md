# Hand-backs of wave-01-reproducer-w01-9

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T11:57:46+09:00 | agent_id=abe8d9dc8f9133a34 type=murmuration:reproducer event=PostToolUse status=delivered bytes=4595 sha256=3afcb47f2a53
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

reproducer-w01-9 on w01-c9 (supersedes w01-c4)

verdict: OVERSTATED
reason: The numbers reproduce independently, but the title says more than was run. It names "three leading platform blocks" when only two blocks plus the paste wrapper touch typed text. "Would store" rests on a rebuilt hook prompt that was checked byte for byte on 2 records. The cut of a message that literally begins with a reminder block is named only under Cost, not in the statement. The author agreed to all three and proposes narrower wording, which needs a superseding claim.

What I found independently:
- **Patch and selftests:** `proposal.diff` applies cleanly to a fresh copy of `scripts/` in `scratch/` (not a git worktree). The patched `user_words.py` is byte-identical to the author's. The `user_words`, `resume_brief` and `lab_status` selftests pass. `lab_init` fails only because `skills/.../templates` is not beside the scratch copy, and the diff does not touch it. The author's `--quick` and `replay_dedup.py` outputs match what I got.
- **Order and edge cases, fired through the patched hook with my own inputs:**
  - A pasted `/lab …` and a pasted `/clear` are stored.
  - A typed `/lab` outside a wrapper is skipped, with or without a paste after it.
  - A whitespace-only or empty wrapper stores nothing.
  - A nested wrapper stores the inner one with its tags.
  - A reminder followed by `/lab` or `/clear` stores nothing.
  - A reminder followed by plain words or a paste stores just the words.
  - A reminder followed by a pasted `/lab` is stored.
  - A user typing a leading exact-form reminder block loses it (only the text after it is stored). A typed reminder-only message stores nothing.
  - Mid-text, one-line, CRLF-form and unclosed reminders, and a wrapper with a mismatched id, are left untouched.
  - New and unmentioned in the claim: a reminder followed by a `<cross-session-message>` or `<task-notification>` is now skipped. The shipped `startswith` test stored these.
- **Headline, from my own extraction (not the author's code):** 72 distinct typed prompts (65 user records, 7 mid-turn). Shipped stores 72 and patched stores 72. 51 differ and 0 are dropped. The cuts are 69 reminders, 5 `<artifact-view-context>` blocks and 1 paste wrapper, and every changed entry is explained by those cuts alone. Characters are 70,893 to 37,197 against the author's 70,784 to 37,088. The removed amount is the same (33,696), and the 109-character baseline gap is one slash-command record (raw tags against a rebuilt `/name args`).
- **"14 not typed" row:** 14 distinct uuids, each in one file only, so no fork copies. 8 are "finished a turn" notices, 1 is the session-start brief and 5 are scheduled prompts. Shipped stores 14. Patched skips the 8 notices and stores 6. The brief still stores 3,757 characters that are not the user's words.
- **Statement scope:**
  - `<side-sessions-event>` never leads a typed prompt (0 of 72). It leads only the 8 notices, and whether those fire the hook is unverified.
  - Hook-prompt fidelity is shown byte for byte on this run's 2 records only. The other 70 typed prompts are rebuilt as text blocks joined with `\n`.
  - The platform dependence of the tags and the paste wrapper is named. The paste wrapper has a single real instance, so the order, nesting and paste-command cases rest on selftest only.
  - 3 `[Request interrupted by user]` records are in neither class and would be stored by both rules if the hook fires on them.

Exchange with author-w01-4: five questions, all answered in `__reports__/reflective_run/w01/author-w01-4/c9_errata.md`. The author left the claim head unchanged. It proposes the title "two leading blocks and the paste wrapper on typed text; a third tag for notices that may not fire the hook". It also proposes adding the literal-reminder cut to the statement, and "would store, given that join" for the count. No new artifact changed my verdict.

Files:
- `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__pondus__/w01-c9.md` (my section appended; the file is untracked)
- `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-reproducer-w01-9.md` (6 puzzles)
- `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-9/` (`cases.py`, `derive.py`, `removedonly.py`, `forks.py`, `side.py`, `side2.py`, their outputs, and `scratch/scripts/`)

Nothing was committed and `agents/`, `skills/`, `scripts/`, `hooks/` were not edited.
