# Hand-backs of wave-01-reproducer-w01-10

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T12:00:11+09:00 | agent_id=a33f44eb9a534960c type=murmuration:reproducer event=PostToolUse status=delivered bytes=3959 sha256=217a4b799166
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

reproducer-w01-10 on w01-c10: verdict OVERSTATED. I appended my section to /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__pondus__/w01-c10.md.

**Independent result**
- **Transcript timing: reproduced.**
  - At both prompts the transcript cwd is the worktree: 10:56 (line 7, 01:56:27.356Z) and 11:04 (line 233, 02:04:30.029Z).
  - The first main-cwd record is line 66 at 01:57:04.849Z. The 49 main records are contiguous (lines 66-144, ending 01:58:59Z).
  - The claim's "65", "232" and "229" are 0-based. Its "66-144" is 1-based.
  - 390 worktree records is the count at line 797 (02:39Z). The file now has 467 worktree and 49 main, so the claim's counts are an unnamed snapshot of a live file.
- **user_words.md: main got both entries first.**
  - The two copies are now identical.
  - The main copy was written at 11:04:30.240, 0.21 s after the prompt.
  - The worktree copy dates from the PI's hand `cp` at 11:04:47-48 (line 249). The 10:56 entry was carried over the same way at line 149.
  - No file shows what payload cwd or CLAUDE_PROJECT_DIR the hook saw, because hooks leave no transcript record for UserPromptSubmit.
- **Proposed rule: does what the claim says in the two named worktree cases, but has an unstated regression.**
  - I wrote my own `lab_root` and fired the author's patched `user_words.py` and the shipped one as hook subprocesses on a real git repo with a linked worktree. My function and the patched script agree on all 7 cases.
  - **The two named cases are fine.** A worktree without a lab falls back to main. A worktree with a lab, run from the worktree or a subfolder, writes to the worktree, where the shipped rule writes to main.
  - **Regression (my case F).** With CLAUDE_PROJECT_DIR = worktree and payload cwd = main, the patched rule writes to main and the shipped rule writes to the worktree. That is a session started in the worktree whose shell `cd`'d to main, which happened in this run from 01:57:04Z to 01:58:59Z, and the PI says the Desktop started in the worktree.
  - The claim's Risk section does not state this.
- **Labels and probe.**
  - The Desktop statements are all kept at CONJECTURE, and the measured statements are backed by runs.
  - The Desktop probe is not runnable as written. `make_settings.py` embeds the hook directory exactly as given, and the claim gives it as a relative path. In a throwaway worktree that path does not exist, so the hook would fail silently.
  - Step 1 also assumes the Desktop copies a gitignored `.claude/settings.local.json` into a new worktree. There is no evidence for that.

**Exchange.**
- **Regression:** accepted. The author says the rule "trades one failure for another and is not a fix until the Desktop probe says which state is the real one". It proposes an untested variant: when both candidate labs share a git-common-dir, take the linked worktree.
- **Line numbers and counts:** confirmed as mixed 0-based and 1-based, and the counts as snapshots. Use timestamps.
- **Probe:** use absolute paths, and put the hooks in a committed `.claude/settings.json` in the throwaway repo, or in the user settings.
- **Scope:** the prompt-cleaning hunks in the diff belong to w01-c9.
- All of this is in `__reports__/reflective_run/w01/author-w01-4/c10_errata.md`. The claim head is unchanged, and the author says any change to what the claim states goes to the PI.

The verdict stays OVERSTATED. The head still presents the rule as the fix, and the probe in it cannot run. A superseding claim with the errata folded in is needed. I also listed `changed_by:` pointing at the errata, which confirms my findings but does not change the verdict.

**Files**
- Scripts: `__reports__/reflective_run/w01/reproducer-w01-10/tl.py` and `rule_check.py`
- Puzzles (4): `__scrupuli__/wave-01-reproducer-w01-10.md`

The first puzzle asks for a fact that does not change when the agent's shell moves. Both rules fail one worktree case.
