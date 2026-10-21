---
type: findings
wave: wave-07
author: explorer-w07-d
date: 2026-10-22
version: v0
decision-required: none
---

# Serial loops and algorithms in the lab's code (lab_status.py first): findings (v0)

No departure from the brief, except two things: (1) the brief says "the replays and drivers run serially"; the E3 drivers already shard 5-way (`w06c10_e3v2_full.sh`), so the one serial CPU-bound loop I found beyond `lab_status.py` is `w06c13_v7_diff_two_guards.py`; (2) end-to-end diffs against the original script were done on the live tree (it grows while I run); the equality that carries weight is at parse level on a frozen APFS clone (see Method).

Helper code is at commit b1df940 (`__instrumenta__/w07d_*`, Rust crate `__instrumenta__/w07d_rs/`). Prototypes replace nothing in `scripts/`.

## Method (one paragraph)

Frozen input: an APFS clone (`cp -cR`) of the 235 project folders `lab_status.py` reads, under `/private/tmp/murmuration-w07/explorer-w07-d/cfg/projects` (669 transcript files, 274.2 MB, 309 main + 360 subagent files; not committed; to be deleted). `CLAUDE_CONFIG_DIR` was NOT set (the permission guard G2 refused it; I did not retry in another form): the frozen tree is consumed only by parse-level drivers that take a file list. "Identical output" is therefore checked as: the canonical dump (one line per file and message id: model, 4 token counts, 1h/5m cache split, timestamp, sessionId, final flag, plus `totalCostUSD` and agent setting) of every variant is byte-identical to the dump of the unmodified `lab_status.parse_transcript` over the same 669 files (9,147 lines). Everything downstream in `report_spend` is a pure function of these results. End-to-end `--spend` diffs on the live tree were identical in one back-to-back run and differed in the open sessions' USD in another (this session's own growth: 4.94 vs 4.87); that is drift, not a variant error. Machine: Apple M3 Pro, 6 P + 6 E cores, shared with the other explorers; the load average (1-minute) is 3-15 across batches and is recorded per row in the raw logs. Every point is repeated (n = 5 to 11), min / median / max given.

## Result

1. **The cold parse is not the cost that matters; the fixed cost is.** Cold `lab_status.py --spend` takes 0.90 s (median, n = 9-11) and its warm-cache run 0.39-0.42 s; of the cold 0.90 s, parsing 274 MB in Python is 0.62-0.74 s, i.e. about 70-80 % [MEASURED, `raw/tables_bench.txt`, `raw/stages.txt`]. Python startup (0.08 s), `git worktree list` (0.054 s as a subprocess, 0.0003 s read from `.git` files), `find_sessions` (0.023 s) and the cache's own handling (0.08 s) are about 0.2 s, and they are what a warm run pays.
2. **The cheapest win is not parallelism or Rust but dropping the `git` subprocess: `cache + no git` = 0.231 s median against 0.386 s for the shipped cache (n = 11, same batch)** [MEASURED, `raw/tables_bench.txt`, `t_e2e3`; paths identical to `git worktree list` in this repo: 8 of 8, `raw/stages.txt`]. Robustness of the `.git` reading across bare repos, packed refs, submodules is CONJECTURE (not tested).
3. **Parallel Python and Rust both cut the cold path to about 0.33 s (from 0.90) and neither beats a warm cache** [MEASURED]: `par` with 12 forked workers 0.322 s (no-git), Rust helper on 6 threads 0.329 s (no-git), warm cache 0.231 s. So the cache (the thing open item 24 doubts) is worth its 147 lines in the warm case *only together* with removing the fixed costs, and parallelism is a cold-path (first call, or after many sessions changed) tool.
4. **Scaling is real but far from linear, and the knee is at the P-core count.** Compute-bound probe: aggregate throughput 1.00, 2.01, 3.99, 5.56 at 1, 2, 4, 6 processes, then 6.27, 7.11 at 8, 10 and 6.57 at 12 (the 11-12 point dips because two cores are taken by other agents' load) [MEASURED, `raw/spin_scaling.txt`]. The six E-cores add roughly 0.3-0.5 of a P-core each here.
5. **Rust, same parse, 274 MB: 87 ms on one thread, 16-17 ms on 10-12 threads (speedup 5.0-5.3, efficiency 0.42-0.53)** against 620-635 ms in Python on one core: 7x single-threaded, 38x at 10 threads [MEASURED, in-process, `raw/table_rust_item.txt`]. As a process (file list, 669 stats, exec) the same run is 0.14 s at 6-12 threads (median) with a floor of 0.06 s for a no-op Rust binary on this machine.
6. **A scheduling mistake worth knowing:** with the file list sorted largest-first, rayon's default `par_iter()` (recursive halving) gave plateaus at 2-3 / 4-6 / 8-12 threads (57 / 48 / 37 ms) because the first half held the large files; `with_max_len(1)` (one task per file) gave 49 / 27 / 22 / 19 ms at 2 / 4 / 6 / 8 threads, about 2x better at 6-12 threads [MEASURED, `raw/table_rust_split.txt` against `raw/table_rust_item.txt`]. This is the "scaling is not linear" the user expects, and part of it was my own imbalance.
7. **A better algorithm in Python helps little**: byte prefilter 0.61 s vs 0.635 s original; whole-file read + one regex over the buffer 0.44 s (1.4x); the floor of Python is `json.loads` of the 15,227 lines that pass (57.5 MB, 21 % of bytes) = 0.18 s plus the scan [MEASURED, `raw/table_py_parse.txt`, `raw/profile.txt`]. The 3-substring prefilter is already tight: 15,227 of 57,541 lines pass; 13,476 are assistant records, 900 are `api-request-blob` records that contain the word and are discarded after parsing, 307 cost-state, 544 agent-setting.
8. **Other serial loops:** the only large CPU-bound serial loop besides `lab_status.py` is `w06c13_v7_diff_two_guards.py` (replays all 5,560 recorded Bash/Write/Edit calls through two guards): 8.7 s serial; my parallel copy gives 8.6 s (1 worker) / 4.5 s (2) / 2.5 s (4) / 1.7 s (6) / 1.55 s (8) / 1.7 s (12) with byte-identical stdout and JSON at W = 1 and 6 [MEASURED, `raw/t_diffguards.jsonl`; row in the table "Other loops"]. Headless `claude -p` cells (231 serial Bash calls, 2,856 s in total, mean 12 s; plus 72 fan-out calls) are API-bound, not CPU-bound: they gain nothing from cores, and the lab already runs E3 in 5 shards (the file says "about 12 min").
9. **How often it matters:** `lab_status.py` was called by agents in 317 Bash tool calls over the whole lab (70 main thread, 247 subagents) [MEASURED, count over the 669 files]. At 0.5 s saved per call that is about 160 s over the lab's life [ESTIMATE: 317 x 0.5 s], against thousands of model requests of seconds each.

## Table

### Where the 0.90 s of a cold `lab_status.py --spend` goes (in-process, 677 transcript files on the live tree)

| Stage | median s | min / max | Label | Source |
|:--|:--|:--|:--|:--|
| Python startup, `python3 -c pass` | 0.079-0.127 (loaded) | 0.066 / 0.313 | MEASURED | `raw/t_floor.jsonl`, `raw/t_e2e2.jsonl` |
| `git worktree list --porcelain` (subprocess) | 0.0535 | 0.051 / 0.055 | MEASURED | `raw/stages.txt` |
| same paths from `.git/worktrees/*/gitdir` | 0.0003 | 0.0003 / 0.0006 | MEASURED | `raw/stages.txt` |
| `find_sessions` (listdir, glob, `first_cwd` of 309 files) | 0.023 | 0.022 / 0.070 | MEASURED | `raw/stages.txt` |
| `Cache()` JSON load, 3.1 MB | 0.015 | 0.014 / 0.019 | MEASURED | `raw/stages.txt` |
| `load_sessions`, warm cache (incl. cache load, 676 stats, subagent globs) | 0.096 | 0.095 / 0.109 | MEASURED | `raw/stages.txt` |
| `load_sessions`, no cache (parse everything) | 0.739 | 0.728 / 1.304 | MEASURED | `raw/stages.txt` |
| `report_spend` total, no cache / warm | 0.778 / 0.202 | | MEASURED | `raw/stages.txt` |
| Whole process, CLI, no cache / warm cache | 0.897-0.909 / 0.386-0.420 | 0.83 / 1.41 ; 0.27 / 0.74 | MEASURED | `raw/tables_bench.txt` |

### Parse alone, 669 files, 274.2 MB, 58,210 lines (in-process, frozen clone)

| Step | s | Label | Source |
|:--|:--|:--|:--|
| read all files into memory (`rb`) | 0.044 (6.2 GB/s, warm page cache) | MEASURED | `raw/profile.txt` |
| iterate lines in `rb` | 0.247 | MEASURED | same |
| iterate + 3-substring prefilter | 0.492 (26 % of lines, 21 % of bytes pass) | MEASURED | same |
| `json.loads` of the passing lines only | 0.179 | MEASURED | same |
| original `parse_transcript`, all files | 0.670 | MEASURED | same |
| Rust, 1 thread: read 35 ms, scan 24 ms, serde 29 ms (thread sums) | 0.087 wall | MEASURED | `raw/table_rust_item.txt` |

### Scaling curves, parse only, same 669 files (medians; spread in the raw files)

Python = forked `multiprocessing.Pool`, one file per task, largest first; Rust = rayon, one task per file, in-process (excludes exec and file-list cost).

| Workers / threads | Python orig, s | speedup | Python whole-file+regex (`buf_find`), s | Rust, ms | Rust speedup | Rust efficiency |
|:--|:--|:--|:--|:--|:--|:--|
| 1 | 0.635 | 1.00 | 0.513 (`buf_re` 0.439) | 87.4 | 1.00 | 1.00 |
| 2 | 0.338 | 1.88 | 0.280 | 49.1 | 1.78 | 0.89 |
| 3 | 0.226 | 2.81 | 0.195 | 34.8 | 2.52 | 0.84 |
| 4 | 0.175 | 3.63 | 0.159 | 26.5 | 3.29 | 0.82 |
| 5 | | | | 21.9 | 3.99 | 0.80 |
| 6 | 0.133 | 4.77 | 0.121 | 22.4 | 3.91 | 0.65 |
| 7 | | | | 18.8 | 4.65 | 0.66 |
| 8 | 0.115 | 5.52 | 0.109 | 19.1 | 4.59 | 0.57 |
| 9 | | | | 16.7 | 5.23 | 0.58 |
| 10 | | | | 16.4 | 5.31 | 0.53 |
| 12 | 0.106 | 5.99 | 0.110 | 17.4 | 5.01 | 0.42 |

[MEASURED; `raw/table_py_parse.txt`, `raw/table_rust_item.txt`; load average at the Rust batch 7.2-7.6, at the Python batch 4.8-5.4]. Reading: both flatten after 6 (the P-cores); the Rust sum of thread time grows from 82 to 184 ms at 12 threads (read 35 to 70 ms: the kernel's copy from the page cache and memory bandwidth, not the parse, is what stops scaling).

### Whole script (process wall, includes Python start, git, find_sessions), cache off unless stated

| Variant | median s | min / max | CPU median | Label | Source |
|:--|:--|:--|:--|:--|:--|
| shipped, no cache | 0.897 | 0.831 / 1.414 | 0.79 | MEASURED | `raw/t_e2e2.jsonl` |
| shipped, warm cache | 0.420 | 0.362 / 0.620 | 0.29 | MEASURED | same |
| shipped, warm cache, same-batch repeat | 0.386 | 0.267 / 0.736 | 0.27 | MEASURED | `raw/t_e2e3.jsonl` |
| warm cache, no git process | 0.231 | 0.213 / 0.350 | 0.16 | MEASURED | `raw/t_e2e3.jsonl` |
| Python whole-file+regex, 1 process | 0.727 | 0.675 / 0.831 | 0.62 | MEASURED | `raw/t_e2e2.jsonl` |
| Python pool 2 / 4 / 6 / 8 / 12 workers | 0.530 / 0.433 / 0.414 / 0.398 / 0.372 | best 0.314 at 12 | 0.71 to 0.92 | MEASURED | same |
| same, no git: 6 / 12 workers | 0.350 / 0.322 | 0.295 / 0.277 | 0.77 / 0.89 | MEASURED | `raw/t_e2e3.jsonl` |
| Rust helper (called from Python, dump parsed back) 1 / 2 / 4 / 6 / 8 / 12 threads | 0.455 / 0.441 / 0.427 / 0.389 / 0.389 / 0.408 | best 0.326 | 0.34 to 0.41 | MEASURED | `raw/t_e2e2.jsonl` |
| same, no git, 6 threads | 0.329 | 0.296 / 0.382 | 0.35 | MEASURED | `raw/t_e2e3.jsonl` |
| Rust binary alone as a process, 1 / 4 / 6 / 12 threads | 0.249 / 0.231 / 0.144 / 0.136 | 0.178 / 0.093 best | 0.13 to 0.20 | MEASURED | `raw/t_e2e2.jsonl` |

Cost of the parallel plumbing [MEASURED, `raw/pool_start.txt`]: a forked `Pool(W)` costs 1.9 / 2.1 / 3.6 / 7.4 / 8.5 / 9.8 ms at W = 1 / 2 / 4 / 6 / 8 / 12; the `spawn` start method (macOS's default) costs 63-172 ms, which would cancel the gain. CPU time (user + sys) of the Python pool grows from 0.62 s (1 process) to 0.92 s (12): parallelism spends 1.5x the CPU to save wall time. Rust's serde_json needs `float_roundtrip` for the cost field: without it `totalCostUSD` came back 1 ulp off (`0.04032221` for `0.040322210000000004`) and the dump differed [MEASURED, first `check` run].

### Other loops

| Loop | Serial | Parallel (my copy) | Label | Source |
|:--|:--|:--|:--|:--|
| `w06c13_v7_diff_two_guards.py`, 5,560 calls, 669 files | 8.69 s (min 8.48, max 14.98 under load 13) | 1 / 2 / 4 / 6 / 8 / 12 workers: 8.61 / 4.47 / 2.46 / 1.73 / 1.55 / 1.71 s; CPU 8.4 to 11.3 s | MEASURED | `raw/t_diffguards.jsonl` |
| `w06c13_decide_diff.py` (offline, two revisions) | 2.2 s wall, 0.12 s CPU (git and process waits) | not tried | MEASURED | `/usr/bin/time` line in this session |
| `w06c4_replay.py`, `w06c9_replay.py`, `w05c4_replay_batched.py` | one process per transcript, serial over transcripts | not run (need plugin roots and fixtures from wave 6) | not measured | file docstrings |
| E3 drivers `w06c10_e3v2_full.sh`, `w06c11_e3v3_full.sh` | already 5 shards, "about 12 min" | n/a, API-bound | CITED (file header) | `__instrumenta__/w06c10_e3v2_full.sh` |
| headless `claude -p` Bash calls in subagent transcripts | 231 calls, 2,856 s, mean 12 s | 72 fan-out calls, 654 s | ESTIMATE (regex classification, see puzzle 3) | `raw/headless_cells.txt` |

## Worst-fitting case

- The story "parallel-first saves the lab's time" fits worst here: the end-to-end whole-script number. Parallel Python at 12 workers (0.37 s) and the Rust helper (0.39-0.41 s) are **no faster than the warm cache that exists already (0.39-0.42 s)**, and the process-level Rust curve is flat from 4 to 12 threads at 0.43-0.46 s through the Python wrapper, because exec, file list, dump text, and the parent's remaining 0.2 s dominate. The whole-script gain from 12 cores is 0.90 to 0.32 s, 2.8x, and from a cheaper fixed cost 0.39 to 0.23 s, 1.7x.
- Worst single point for the curve itself: the default rayon split (`par_iter` without `with_max_len(1)`) at 8-12 threads, speedup 2.5 at 12 threads against 5.0 for per-file tasks (above).
- Worst for "Rust is lean": the Rust binary alone as a process is 0.136-0.249 s while the parse inside it is 17-87 ms; the rest is the 0.05-0.06 s exec floor (a no-op Rust binary, `rs_empty`: median 0.061 s, same as `sh -c :` 0.066 s in this load) plus 669 `stat` calls and the sort. On this loaded machine no-op floors of 0.06 s are 3x the 18 ms of S-w06-explorer-w06-b-1: the floor is explorer-w07-a's question; here it only marks the limit.

## Not covered

- A cold-file-cache run: I cannot purge the page cache without privileges; the clone was read by Python once before the Rust and parallel curves. The first Rust run read 0.245 s of read time against 0.035 s later (a first-touch run), so a truly cold disk read is at least 7x slower than every number above. [MEASURED once, not repeated]
- Incremental reads by file offset: not built. Only an ESTIMATE: files modified in the last hour are 10 files, 14.9 MB, 0.062 s of original parsing, so a warm cache re-parses about 60 ms and offsets could save at most that [MEASURED, `raw/recent_files.txt`, from `__instrumenta__/w07d_recent_files.py`, run again after the first reading: the numbers move with the clock]. It would not fix the same-size-and-mtime limit of item 24, only a stored hash of the cached prefix could, which I did not build.
- `mmap` instead of `read` in Rust, `memmap2`, SIMD scanning (`simd-json`): not tried.
- `w06c4_replay.py`, `w06c9_replay.py`, `w05c4_replay_batched.py`: the fixtures (plugin roots, worker transcripts) were not rebuilt; only their structure was read (one subprocess per transcript step, serial over transcripts). The E3 drivers' own timing was taken from their headers, not re-run.
- Whether `lab_status.py` is reached by the user at an interactive pace: `/lab-status` is user-invoked (`skills/lab-status/SKILL.md`), agents call it 317 times in the lab's history; the user-visible value of 0.15-0.5 s is not measured.
- P-core versus E-core placement was inferred from throughput, not from thread affinity (macOS gives none).

## Steering questions

- [now] Item 24 (cache worth 147 lines?): the evidence says drop the `git worktree list` subprocess first (0.15 s of a 0.39 s warm call, 0 lines added), then ask whether the cache's remaining 0.15-0.19 s of saving per cold call is worth 147 lines. Do you want that stated as a claim for an author (the verifier checks `cache+nogit` against the shipped script on a frozen tree)?
- [now] Parallel Python (fork pool, about 25 lines, no dependency) or a Rust helper (needs a build per platform, shipped binary, JSON dump parser) for the cold path? The measured difference is 0.32 vs 0.33 s; the fork pool adds no dependency. I would not ship Rust for this.
- [later] The pre-registered rule for any such claim would be the paired difference per call, median, n >= 30, interleaved, load recorded; a per-pair noise from this report: min-to-median spread of 0.05-0.15 s at the whole-script level under load 5-7.

## Pointers

All under `__reports__/wave-07/explorer-w07-d/raw/` (copies of `/private/tmp/murmuration-w07/explorer-w07-d/`), generated by the scripts at commit b1df940:

| Artifact | Command |
|:--|:--|
| `profile.txt` | `python3 __instrumenta__/w07d_profile.py $PWD <scratch>` |
| `stages.txt` | `python3 __instrumenta__/w07d_stages.py $PWD 7` |
| `t_py_parse.jsonl`, `table_py_parse.txt` | `python3 __instrumenta__/w07d_parsers.py $PWD <scratch>/files.txt time VARIANT [W]`, then `w07d_table.py` |
| parse-level equality | `python3 __instrumenta__/w07d_parsers.py $PWD <scratch>/files.txt check --rust-dump <scratch>/rust_dump.txt` (prints: orig, bytes, buf_find, buf_re, buf_find x4 workers, rust: all True) |
| `t_rust_inproc.txt` (default split), `t_rust_item_inproc.txt` (per file), tables | `w07d_rs --files files.txt --threads T --reps 11 [--item]`; `cargo build --release --offline` in `__instrumenta__/w07d_rs` with `CARGO_TARGET_DIR` in scratch |
| `t_rust_scaling.jsonl` | `w07d_bench.py` with the default split schedule (older binary), process level |
| `t_e2e2.jsonl`, `t_e2e3.jsonl`, `tables_bench.txt` | `w07d_bench.py --n 9 / 11 ...` over `w07d_spend_variant.py <root> orig|alg|par W|rust W|cache|...+nogit` and the shipped script |
| `spin_scaling.txt` | `python3 __instrumenta__/w07d_spin_scaling.py 5` |
| `pool_start.txt` | `python3 __instrumenta__/w07d_pool_start.py` |
| `t_diffguards.jsonl`, `diff_serial.out` | `w07d_diff_two_guards_par.py W <guard@071fc53> scripts/permission_guard.py out.json <cfg/projects>`; serial `w06c13_v7_diff_two_guards.py` |
| `headless_cells.txt` | `python3 __instrumenta__/w07d_headless_cells.py files.txt 12` |
| `files.txt` | the 669 scratch paths of the frozen clone (no transcript content) |
| `t_orig.jsonl`, `t_floor.jsonl` | first timing of the shipped script; exec floors |
