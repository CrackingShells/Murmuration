## S-w07-author-w07-4-1
The protocol's ceiling for dropping the git child was 0.155 s a call (explorer-w07-d: 0.386 s against 0.231 s). Measured here: 0.051 / 0.052 / 0.060 s median saving per pair at load 2.7-3.1, and 42.9 ms for the child alone in process. Two medians taken at different loads differ by more than a paired difference does, so the 0.155 s overstated the gain about 3x. Why is the whole-call saving (about 51-60 ms) larger than the child's in-process cost (43 ms)? Spawn from a process with its modules loaded, or the page cache, are guesses; not tested.
refs: __reports__/wave-07/author-w07-4/o4_seed1.txt, micro.txt, __reports__/wave-07/explorer-w07-d/raw/tables_bench.txt

## S-w07-author-w07-4-2
A bump of `CACHE_VERSION` (needed because cached usage dicts now hold `speed` and `server_tool_use`) makes an old and a new `lab_status.py` that share one cache file rewrite each other's file on every call (each ignores the other's version): a 0.8 s call instead of 0.2 s. It matters whenever two checkouts of the plugin run in one lab against the same `__statera__/.harness/lab_status_cache.json`. I gave each variant its own file (`LAB_STATUS_CACHE`) in o4; I did not measure the thrash itself.
refs: scripts/lab_status.py (`CACHE_VERSION`, `Cache.__init__`), __instrumenta__/w07c4_o4_pairs.py

## S-w07-author-w07-4-3
The first full run of o3 failed in two cases only because its scratch folder lay inside a repository by accident: git answered [] for a folder that does not exist and for a bare repository below a repository, B returned the enclosing repository's list. A checker that ran on a clean `/tmp` would have said PASS. How many of B's other guards (ownership, filesystem boundary, `GIT_CEILING_DIRECTORIES`) are tested only on a machine where they never trigger? The ownership test (uid) and the filesystem boundary were not exercised by any case: I cannot create a repository owned by another user or a second filesystem without privileges.
refs: __instrumenta__/w07c4_worktree_cases.py (cases "below a repo"), __pondus__/w07-c4.md ("What failed")

## S-w07-author-w07-4-4
Between 2 and 6 of every 30 pairs show B slower by 0.02-0.09 s (seed 2: 6 of 30, down to -0.094 s) while the CPU medians of A and B differ by 0.00-0.02 s. The negative pairs are probably load from other agents landing on one call of a pair, but I did not log which process was running; the rule (sign count) tolerates them, a threshold in seconds would not.
refs: __reports__/wave-07/author-w07-4/o4_seed2.txt (pairs with a negative saving), o4_seed2.jsonl

## S-w07-author-w07-4-5
The existing selftest asserted that with git missing from PATH, `git_worktrees(repo) == []` and the notice appears. With B that is false by design: the repository's worktrees are read without git. I rewrote the assertion (and the docstring) instead of keeping the old behaviour as a mode. Is "needs git" a documented property that other code or skills rely on? `report_spend` still prints the notice for a folder that is no repository. I read only this file and `skills/lab-status/SKILL.md`'s existence, not the skill text.
refs: scripts/lab_status.py (selftest, "git missing" block), `git diff 1c23e5c -- scripts/lab_status.py`

## S-w07-author-w07-4-6
The permission layer refused one `rm -rf <dir>/*` that came after a `cd` (the glob could not be resolved statically). I did not retry it in another form: stale first-run outputs in `__reports__/wave-07/author-w07-4/` were overwritten by the final run, whose files have the same names, so nothing is left from the first run there. A scratch folder `/private/tmp/murmuration-w07/author-w07-4/` holds `wt/` (the worktree on branch w07-p4-labstatus), `full.job.log` and `full.job.pid` (the job has ended); the transcript clone lived under a `mktemp` folder that `w07c4_run_all.sh` deletes.
refs: __instrumenta__/w07c4_run_all.sh
