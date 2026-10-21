## S-w07-reproducer-w07-4-1
The live lab cache `__statera__/.harness/lab_status_cache.json` (A, version 1) was cold on two consecutive A calls (0.958 s and 0.868 s) at the start of the author's default-name thrash script, then warm from the third call on and in three later A calls (0.38, 0.26, 0.24 s). Nothing of mine rewrote it between those two calls; some other caller or script version sharing the file may have. Which real callers write that file, and with which CACHE_VERSION, is unknown; this is the thrash the version-named file is meant to end.
refs: output of `w07c4_cache_thrash_default.py` (calls 0 and 1), session scratchpad; author split_thrash.out

## S-w07-reproducer-w07-4-2
A frozen clone of the transcripts could not be made in my session: both an APFS clone of `~/.claude/projects` and the author's `--clone` run were denied by the classifier (PII). The author's frozen-clone runs are therefore not independently reproduced, and my o1 is on the live tree, where A's output drifted within minutes (311.97 to 312.00 USD). A HOME-pointed config dir (`config_dir()` uses `expanduser("~")`) would allow process-level runs on a clone without CLAUDE_CONFIG_DIR, if the user allows the copy.
refs: `A_warm2.out` against `A_warm.out` in the scratchpad `o1/`; `w07c4_frozen_diff.py` `--clone`

## S-w07-reproducer-w07-4-3
The fast factor 2.0 and USD 0.01 a search rest on a pricing-page fetch of 2026-10-19 that no file in the repo preserves (the header cites the URL; a git grep finds only quoted code lines). The report the user reads for money prices fast mode by it, and no real record has either today. The first test will be the first real fast-mode session.
refs: `scripts/lab_status.py` lines 421-431; `__reports__/reflective_run/w01/author-w01-3/lab_spend.py` line 37 (says Opus 5.5 fast is $8/$40)

## S-w07-reproducer-w07-4-4
A merged usage dict is now `{... "speed": "fast", "server_tool_use": {"web_search_requests": n}}` only when present, so the cache holds a different shape from the transcript's (other keys such as `web_fetch_requests` are dropped, `speed: standard` is dropped). Harmless for price, but if the report ever shows web fetches or speed counts, the cache version must bump again.
refs: `scripts/lab_status.py` `merge_usage` at c473203
