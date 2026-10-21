# P4 v0: `lab_status.py` without the git child, and with fast mode and web search priced (registered before any run)

registered: 2026-10-22, by research-pi, before author-w07-4 starts. Claim: w07-c4. Open item 24.

## The change (B against A)

- A = `scripts/lab_status.py` at the commit this protocol is committed in.
- B = A with two changes, nothing else:
  1. `git_worktrees(root)` reads the repository's worktree list from the git directory
     (`<common git dir>/worktrees/*/gitdir`, the main checkout first) instead of starting
     `git worktree list --porcelain`. It falls back to the subprocess whenever the layout is not
     what it expects (no common dir, unreadable files, a `.git` file it cannot resolve).
  2. `merge_usage` keeps `speed` and `server_tool_use`, so that `message_usd`'s fast-mode factor and
     web-search price, which are unreachable today, apply (S-w07-explorer-w07-d-2).
- Not in B: a process pool or a Rust helper for the cold path. explorer-w07-d measured both at
  about 0.32–0.33 s cold, against 0.39–0.42 s for the existing warm cache, and cold runs are rare.
  Here the better algorithm is the cache that is already there; parallelism buys nothing a user
  waits for.

## Measured ceiling and noise, before the rule (open item 27)

- explorer-w07-d: warm `--spend` 0.386 s with the git child, 0.231 s without it (medians, load
  3–15). So the ceiling of change 1 is about 0.155 s a call, the git child's wait. Whole-script
  min-to-median spread under load 5–7: 0.05–0.15 s. [source:
  `__reports__/wave-07/explorer-w07-d/00-findings_v0.md`, `raw/tables_bench.txt`]
- A threshold in seconds would sit inside the spread. The rule gates on the sign over many
  interleaved pairs instead: under no true saving, 20 or more of 30 pairs faster has a probability
  of about 5%.

## Metrics and rule

- **o1 (same output):** on a frozen copy of the lab's transcripts and claim files (the `--project`
  path, or another way that needs no change of `CLAUDE_CONFIG_DIR`), `lab_status.py` and
  `lab_status.py --spend` print byte-identical output under A and B, cold and warm, except for the
  lines change 2 is meant to change. The worktree list equals `git worktree list --porcelain`'s
  for this repository and for a scratch repository with a removed, a locked and a prunable
  worktree.
- **o2 (change 2 does what it says):** a synthetic transcript with one fast-mode message and one
  web-search message is priced by B as `message_usd` intends (factor 2, USD 0.01 a search), and by A
  without them. No record in the lab's transcripts has either today, so o1's output is unchanged
  by it on the real tree; say so if that is not true.
- **o3 (failure):** with the git directory unreadable, with `gitdir` files pointing at missing
  paths, and in a folder that is not a repository, B gives the same worktree list as A (by its
  fallback or by the same empty answer), without an exception or a hang.
- **o4 (time):** 30 interleaved pairs of warm `--spend` calls on the live tree, wall time per call;
  B faster in at least 20 of 30. Report the median per-pair saving, the spread and the load.

**Landing:** o1–o4 pass and reproducer-w07-4 supports them.
