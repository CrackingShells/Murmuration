## S-w01-reproducer-w01-10-1
The shipped rule (CLAUDE_PROJECT_DIR first) and the proposed rule (payload cwd first) each get one of the two worktree cases wrong. Shipped: session started in main, moved into a lab-bearing worktree, goes to main (wrong). Proposed: session started in the worktree, shell cd'd to main, goes to main (wrong; shipped was right). Neither uses a fact that does not change when the agent's shell moves. The only such fact seen is the first transcript cwd, which a hook does not get; does the SessionStart payload cwd, stored once per session_id, give it?
refs: __reports__/reflective_run/w01/reproducer-w01-10/rule_check.py (cases C and F)

## S-w01-reproducer-w01-10-2
The user_words entry for 10:56 landed in main although the transcript cwd was the worktree for 40 s before and after the prompt, and the worktree had no lab until 10:58. The 11:04 entry landed in main (file mtime 11:04:30.24, 0.2 s after the prompt at 11:04:30.03) with a lab in the worktree. Both are explained by CLAUDE_PROJECT_DIR = main, but also by payload cwd = main (e.g. the Desktop running hooks from the repository root or from the marketplace directory the plugin is loaded from). No file in this run tells the two apart.
refs: ab96c5ed...jsonl lines 7, 233; __statera__/user_words.md mtime 11:04:48 (hand copy, line 249); main copy mtime 11:04:30.24

## S-w01-reproducer-w01-10-3
Hooks leave no trace in the transcript for UserPromptSubmit (no hook_success attachment for it, only for SessionStart). A Desktop transcript therefore cannot show what payload the hook received. Would a one-line stderr/stdout of cwd by the shipped hook (opt-in) be cheaper than the user probe?
refs: ab96c5ed...jsonl lines 4-6 (SessionStart attachments only)

## S-w01-reproducer-w01-10-4
Line numbering in the claim head mixes 0-based (65, 229, 232) and 1-based (66-144). Small, but it is the sort of slip that makes a reader doubt the other numbers; the 390/49 count has no snapshot (390 worktree records is reached at line 797, the file now has 467).
refs: __reports__/reflective_run/w01/reproducer-w01-10/tl.py
