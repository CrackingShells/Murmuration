# w07-c4 tables: `lab_status.py` without the git child (B) against the shipped script (A = 1c23e5c)

All numbers come from `__instrumenta__/w07c4_run_all.sh` at ddbdecf (full mode), raw files beside this one. Machine: Apple M3 Pro, load average at start 3.29 (`load_at_start.txt`), shared with other agents. Labels: MEASURED.

## o1 same output (`o1_frozen.out`, `cases.out`, `selftest.out`)

| Check | Result |
|:--|:--|
| frozen APFS clone of the 235 project folders `find_sessions` opens: 682 files, 289 MB | `--spend` text (2,985 bytes) A == B byte for byte, cold and warm; full report (14,983 bytes) A == B, cold and warm; A cold == A warm, B cold == B warm; A run twice gives the same full report (the live puzzle and claim files did not move in the window) |
| records with `usage.speed == "fast"` / with `web_search_requests` > 0 in those files | 0 / 0 (the pattern matches: 14,734 `"speed":"standard"` and 4,185 `"web_search_requests":0` records in the first clone), so change 2 cannot alter the real tree's output today |
| `git_worktrees` A against B, 37 scratch cases (removed, locked, locked and removed, detached, name with a space and an accent, far folder, symlinked path, subfolder, call from each linked worktree, bare, submodule, separate git dir, below a repository) plus the live repository (13 worktrees) | 37 of 37 equal as lists, order included |
| `scripts/lab_status.py --selftest` on B | PASS (one assertion rewritten, see claim) |

## o2 change 2 (`o2.out`)

| Synthetic session (model opus-5-5, no cost-state) | A | B | intended |
|:--|:--|:--|:--|
| 1M output plain (20.00) + 1M output fast (40.00) + 3 web searches (0.03) + one message streamed over 3 records, fast on the middle one, searches 0/1/2 (40.00 + 0.02) + 1M input (4.00) | 64.00 | 104.05 | 104.05 |
| B through its cache: first run, second run from the cache | 104.05, 104.05 | | |
| B reads a cache file of version 1 | ignored (files = {}) | | |

## o3 failure (`cases.out`, `o3_cli.out`)

In `cases.out` (in process, 20 s alarm per call): unreadable `.git`, unreadable `.git/worktrees`, unreadable admin dir, `gitdir` missing path, empty, garbage, relative, without `/.git`, a directory, absent; stray file in `worktrees/`; HEAD missing; linked worktree's `.git` garbage; admin dir gone; `commondir` pointing nowhere; `core.worktree`; `GIT_DIR` set; bare; separate git dir; submodule; not a repository; folder that does not exist; empty string; and five cases below a repository. B equals A in all 37, no exception, no hang. B answered from the files in 15 of them (under 5 ms) and asked git in the rest (the rest show about 40-60 ms in the B column). `o3_cli.out`: 13 folders run as `lab_status.py --spend --project DIR` under both scripts: exit 0, stdout identical, stderr empty in all 13.

## o4 time (`o4_seed1.txt` is the registered batch; seeds 2 and 3 are repeats, same code)

| Batch | pairs B faster | median saving per pair (A - B) | quartiles | min / max | A wall median | B wall median | load1 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| seed 1 (registered) | 28 of 30 | 0.051 s | 0.038 / 0.074 | -0.048 / +0.142 | 0.245 s | 0.192 s | 2.81 - 3.07 |
| seed 2 | 24 of 30 | 0.052 s | 0.028 / 0.074 | -0.094 / +0.161 | 0.255 s | 0.211 s | 2.96 - 3.14 |
| seed 3 | 29 of 30 | 0.060 s | 0.042 / 0.087 | -0.058 / +0.179 | 0.298 s | 0.199 s | 2.68 - 2.96 |

Rule: at least 20 of 30 in the registered batch: 28. Under no true saving 28 of 30 has probability 4e-7. In-process cost of the child alone (`micro.txt`, n = 200 alternating calls, 13 worktrees): A 42.9 ms median (40.8 - 119.5), B 0.52 ms (0.34 - 0.79).

Not the 0.155 s the protocol takes as the ceiling: the median saving is 0.05-0.06 s (about 20 % of a 0.25 s warm call). The 0.155 s of explorer-w07-d is the difference of two medians taken at load 3-15; the pair differences here reach 0.14-0.18 s only in the upper tail.
