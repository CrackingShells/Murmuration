## S-w04-research-pi-1
The session cwd follows the PI's own Bash `cd`: one `cd` into the main checkout moved 7 transcript records and the app's "primary working directory" to main until the next `cd` back. Any hook that resolves the lab from the payload `cwd` follows the shell of whoever typed last, the PI included.
refs: ~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-4-3417be/c533f1c6-c56e-4c8d-b6ff-e90c3ddea2f4.jsonl (cwd counts: 56 worktree, 7 main at 09:29)

## S-w04-research-pi-2
Four authors dispatched in one message got `start` log lines with B 3.0 / T 20 and `source: unknown` in `__statera__/harness.jsonl`, though their briefs said USD 4, 12, 8, 8. Their state files hold the brief's figures (author-w04-2: B 12, T 60, `brief_read: true`), so the notes use the right budget; but the log, which `/lab-status` and the PI read, shows the defaults for every parallel dispatch.
refs: __statera__/harness.jsonl (09:34:50–52 start lines), __statera__/.harness/a682e6ed4c8ec011f.json, scripts/budget.py:439-453

## S-w04-research-pi-3
The PI's PreToolUse(Agent) and the authors' SubagentStart records were written to the worktree's lab, so the payload `cwd` was the worktree at 09:34. The 09:27 prompt went to main. Unless the payload `cwd` of UserPromptSubmit differs from that of PreToolUse, the Desktop's hook CLAUDE_PROJECT_DIR is the main checkout.
refs: __statera__/harness.jsonl; /Users/hacker/Documents/src/CrackingShells/Murmuration/__statera__/user_words.md (09:27 entry); scripts/user_words.py:project_root; scripts/handback.py:lab_root
