## S-w04-author-w04-1-1
The platform overrides a CLAUDE_PROJECT_DIR set in the launch environment: I launched `claude -p` with CLAUDE_PROJECT_DIR = the main checkout, started in a linked worktree, and the hook saw the worktree. So the brief's "CLAUDE_PROJECT_DIR set to the main checkout to imitate the Desktop" does not imitate anything; the Desktop's main-checkout value must come from the Desktop launching differently (or from a different mechanism than the environment of the process). I imitated it with a prefix in the hook command. Whoever dumps the Desktop's real hook environment settles it.
refs: /private/tmp/murmuration-w04/author-w04-1/run1/A.jsonl and B.jsonl (field env_CLAUDE_PROJECT_DIR); __reports__/reflective_run/w04/author-w04-1/results.txt (first section)

## S-w04-author-w04-1-2
The first prompt of a headless session has no transcript file on disk at UserPromptSubmit (nor at SessionStart); the second prompt has one. The PI saw SessionStart attachments and the first prompt record in the Desktop transcript with timestamps right at hook time, but whether the file existed when the hook ran is unknown; if CLAUDE_CODE_EAGER_FLUSH=1 (set in this Desktop's environment) changes it, the first-prompt branch of the rule (payload cwd) never runs in the Desktop. Nothing I ran distinguishes the two.
refs: /private/tmp/murmuration-w04/author-w04-1/run1/B.jsonl (field transcript_exists); `env | grep EAGER_FLUSH` in this session

## S-w04-author-w04-1-3
`/lab` and `/lab-status` still resolve the project with CLAUDE_PROJECT_DIR first (`lab_init.py:project_root`, `lab_status.py:project_root`), and `lab_init.py` appends the question to `user_words.md` through `user_words.append_words`. In a Desktop worktree session `/lab <question>` would therefore still write to the main checkout (if CLAUDE_PROJECT_DIR = main), while the hook now writes to the worktree: two lab roots in one session. Not my files; the same rule needs a home that both can import, but those scripts take no hook payload (no transcript path), so the first-cwd rule has nothing to read there. The slash command's cwd is the live one.
refs: scripts/lab_init.py:94-95, scripts/lab_status.py:92-93, scripts/handback.py:66-74 (cwd-first, the shell-follows risk of w01-c10 applies to it)

## S-w04-author-w04-1-4
The Bash tool resets a `cd` outside the project when the target is not an added directory (headless without --add-dir: the payload cwd stayed in the worktree after `cd <main>`). w01-c10's "payload cwd follows the shell" is therefore only half true; it follows inside the project and the directories passed with `--add-dir`, which the Desktop does pass (the main checkout). This reduces, but does not remove, the shell hazard for cwd-first scripts such as handback.py.
refs: /private/tmp/murmuration-w04/author-w04-1/run1/B.jsonl (payload cwd wtA on all three prompts) against run3/changed.payload.jsonl (prompt 3: other)

## S-w04-author-w04-1-5
Timing noise: a first unpaired round of 30 gave 44 ms for the unchanged user_words.py in one round and 255 ms in another minutes later, while other agents were running. An unpaired before/after comparison on this machine could have shown a spurious +100 ms or a spurious speed-up; only the alternating pairs gave a stable difference (+1.4 ms). Any wave-4 item that quotes a hook cost in ms (item 9) should use paired alternation.
refs: /private/tmp/murmuration-w04/author-w04-1/timing/results.txt (unpaired), paired.txt (paired)

## S-w04-author-w04-1-6
A session that starts in the main checkout and enters a worktree with EnterWorktree has first cwd = main, so the new rule keeps its words in main: the same landing as the shipped rule, and the opposite of what a user who "works in the worktree" would want. Whether the Desktop ever starts that way is unknown (the PI's measurement says this session did not). Not tested headless; the claim leaves it out of scope.
refs: __pondus__/w04-c1.md (scope); w01-c10 cases 5/6 in __reports__/reflective_run/w01/author-w01-4/probe/cases.sh
