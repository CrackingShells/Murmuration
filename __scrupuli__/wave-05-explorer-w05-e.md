## S-w05-explorer-w05-e-1
The Desktop launches every session of this lab with `--project-config-root <main checkout>`, a flag that `claude --help` does not list, and denies the session Edit on main's `.claude/settings*.json`, hooks, skills and agents folders. Wave 4's misrouted `user_words.md`, wave 5's misrouted `--scope local`, and the ignored worktree settings all follow from this one flag. Why does the Desktop pin the root to main for a worktree session: a choice (shared project config), or a side effect? Is there a Desktop setting for it? The headless runs show the flag decides everything; nothing I ran shows what the Desktop does with it.
refs: __reports__/wave-05/explorer-w05-e/01-run_log.md (rows ps, G_*, F*, H*)

## S-w05-explorer-w05-e-2
Scripts that prefer `CLAUDE_PROJECT_DIR` to the event `cwd` (`scripts/lab_init.py:95`, `scripts/lab_status.py:93`, `scripts/handback.py:73` as a fallback) act on the main checkout in a Desktop worktree session, where `CLAUDE_PROJECT_DIR` is main and the payload `cwd` is the worktree (run H1). Does `lab_status.py` read the wrong lab's `__statera__` right now, and did `/lab` do so in wave 4?
refs: scripts/lab_init.py:95, scripts/lab_status.py:93, __reports__/wave-05/explorer-w05-e/01-run_log.md (H1)

## S-w05-explorer-w05-e-3
This worktree's `.claude/settings.local.json` still enables `murmuration@murmuration-local` and `.claude-plugin/` has no `marketplace.json`, while `__statera__/wave-05.md` Notes say the `murmuration-w5` setup was written here. Either it was reverted or the note describes a file that exists only in another place. In my CLI runs such a setup would load both plugins and drop the second one's hooks (E7), so "running the latest on myself" may have been silently false twice.
refs: .claude/settings.local.json, __statera__/wave-05.md (Notes), __reports__/wave-05/explorer-w05-e/01-run_log.md (E7a, E7b)

## S-w05-explorer-w05-e-4
The platform reported 322 to 379 ms for a SessionStart hook whose script takes 42 ms (python) or 158 ms (python plus git) when I time it alone; wave 4 measured hooks at about 0.1 s. Where do the other 200 ms or more go (spawn, parallel hooks in the same group, cold start)? If it is per-hook fixed cost, the hook count matters more than the script.
refs: __reports__/wave-05/explorer-w05-e/01-run_log.md (H3, timings table)
