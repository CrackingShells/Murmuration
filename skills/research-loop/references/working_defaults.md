# Working defaults for the PI

## At the start of a session

- Look at the state of the project: `git status`, the last few commits, the current wave note in
  `__statera__/`, the last entries of `__statera__/user_words.md`, and the open puzzles
  (`/lab-status`).
- If `__design__/framing.md` still holds template placeholders, fill it first: the user's question
  in their words, your reading of it, notation, scope and rules. Every brief points to it.
- If the session was resumed or compacted, the current wave note and the open puzzles are shown to
  you automatically. Read them before doing anything else.

## While working

- Dispatch independent work in parallel: several explorers in one message, not one after another.
- Report outcomes faithfully. If a check failed, say so with its output; if a step was skipped,
  say that; when something is done and verified, say it plainly.
- Before an action that is hard to reverse or visible outside the project (pushing, publishing,
  sending, deleting data), ask the user and wait for a clear yes.
- Quote spend and budget use only from `__statera__/harness.jsonl` or `/lab-status`, never from a worker's
  own figure.
- A worker that asks for more budget in its hand-back is yours to decide: raise it by resuming it with
  `Budget: USD <x>` / `Time: min <t>` lines, or let the hand-back stand. Briefs never go below USD 0.30
  and 3 minutes.
- Never stop processes by name pattern (`pkill`, `killall`). Stop only the process ids you started.
- Commit your own files only, with a message that says why. Team members do the same.
- A scratch lab you will delete: start Claude Code in it with `COLGREP_DATA_DIR=<folder>/.colgrep`.
- Use whatever search and reference tools the environment offers (semantic code or document
  search, literature search, a computer-algebra system) rather than re-reading whole files.
- If a persistent memory is available, record there what the user teaches you about how they want
  the work done, not what the project files already hold.
