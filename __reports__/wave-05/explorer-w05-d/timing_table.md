# Timing table: machine-side cost of operating the lab (explorer-w05-d, 2026-10-21)

Machine: Apple M3 Pro, 12 cores, macOS 25.6, python3 3.12.12 (miniforge), load average 2.5 to 5 from other agents. Every "bare" figure is one process start as the platform makes it (`sh -c`, posix_spawn, payload on stdin), cells shuffled within rounds. "platform" figures are the `durationMs` the platform wrote into transcripts (hooks that print something only).

## A. One start, bare (n per cell in the source file)

| item | wall median ms | CPU median ms | n | source |
|:--|--:|--:|--:|:--|
| floor: `sh -c :` | 31.5 | 3.1 | 40 | timing_hooks_head_n40_summary.txt |
| floor: `python3 -S -I -c pass` | 53.7 | 10.7 | 40 | same |
| floor: `python3 -c pass` (editable finders + .pth at `site`: 9.8 ms of import time, 7.7 ms of it the hatchling finder) | 64.4 | 21.9 | 40 | same; `python3 -X importtime -c pass` |
| budget.py PostToolUse / PostToolBatch, main thread (does nothing) | 81.2 / 80.0 | 37.4 / 37.2 | 40 | same |
| budget.py PostToolUse, worker, 0.31 MB / 5.56 MB transcript | 83.3 / 110.1 | 39.5 / 66.9 | 40 | same |
| budget.py SubagentStart (bare) | 81.5 | 38.3 | 40 | same |
| handback.py PreToolUse (explorer, no report) | 81.6 | 37.8 | 40 | same |
| user_words.py (UserPromptSubmit) | 70.8 | 26.8 | 40 | same |
| colgrep-mcp `colgrep_policy.py` on PreToolUse Bash, as shipped (`uv run --no-project --quiet python`) | 118.8 | 58.4 | 30 | timing_colgrep_hook_n30.md |
| same, `python3` directly / `python3 -S -I` | 78.4 / 72.4 | 34.4 / 28.7 | 30 | same |
| `git worktree list` via `/usr/bin/git` (Xcode shim) / via the real binary in CommandLineTools | 56.0 / 24.2 | n/a | 25 | inline run, reproduced in the report's pointers |
| `zsh -c true` / `zsh -l -c true` / `zsh -i -c true` | 22 / 38 / 4368 | n/a | 8 | inline run; `.zshrc` runs brew, zsh-patina, conda, mamba, nvm |

## B. Starts at once (the real regime at a dispatch)

| N started at once | budget.py SubagentStart, per process ms | no-op python script (control), per process ms |
|--:|--:|--:|
| 1 | 79 | 63 |
| 3 | 140 | 125 |
| 5 | 192 | 175 |
| 8 | 259 | 233 |
Source: concurrent_subagentstart.md, concurrent_noop_control.md (8 reps each). The control scales the same, so the growth is the machine's, not a lock in budget.py.

## C. The platform's own record of hook durations (hooks that printed; all 306 sessions of this lab)

See hook_platform_durations_all_lab_sessions.md. SubagentStart: colgrep policy n=128 median 276 / p90 654 ms; the user's tool-routing policy n=128, 164 / 381; budget.py n=20, 605 / 1085 (bare: 82). One PreToolUse `uv run` colgrep hook was cancelled at its 10 s timeout (10238 ms).

## D. lab_status.py (whole process, interleaved, 12 reps, frozen copy of the transcripts; outputs of the four variants byte-identical)

| variant | wall median ms | CPU median ms | what changed |
|:--|--:|--:|:--|
| v0 shipped (306 sessions, 640 files, 228 MB) | 830 | 665 | |
| v1 | 706 | 631 | one `git worktree list` per run instead of three |
| v2 | 684 | 604 | v1 + bytes-level line filter |
| v3, cache warm | 306 | 228 | v2 + per-file parse cache keyed on (size, mtime_ns) |
Scaling, v0 against v3 (wall ms; sessions; MB read): 260/153 (25; 11), 305/168 (50; 29), 371/185 (100; 53), 635/256 (200; 151), 825/307 (306; 228) [timing_lab_status_scale_n10.md]. Floors inside the 306 ms of v3: python start 60, one git 78, imports 24, the rest cache load and stats.

## E. A trivial Bash call in a headless run (haiku, six `true` calls; first call excluded; n = 2 runs per cell)

| cell | median s | min s |
|:--|--:|--:|
| auto + user hooks (colgrep, tool routing) | 1.31 | 0.83 |
| auto, hooks disabled (`disableAllHooks`) | 0.93 | 0.72 |
| bypassPermissions + hooks | 0.24 | 0.22 |
| bypassPermissions, hooks disabled | 0.08 | 0.03 |
| (separate run) auto + hooks | about 1.2 | |
| (separate run) auto + `--allowedTools Bash` + hooks, n = 1 | about 1.3 | |
First Bash call of each session: 4.4 to 6.4 s in every cell. Source: bash_floor_probe_raw.jsonl (8 runs); the second probe (auto vs auto + allow) was killed by a 110 s timeout after 3 runs and wrote no file; its three printed rows are quoted in the report.

## F. Per wave, wave 4 (PI session c533f1c6, 88.1 min, 15 workers, 334 worker-minutes, 104 main + 739 worker tool calls, 721 Bash calls)

| item | count | price | total serial seconds | label |
|:--|--:|--:|--:|:--|
| Murmuration hook starts: 843 PostToolUse + 803 PostToolBatch + 29 + 29 handback + 15 dispatch + 3 x 23 start/stop + 0 prompts = 1788 (208 main, 1580 workers) | 1788 | 80 ms main, 88 ms workers (bare) | about 156 (CPU 71) | ESTIMATE |
| same at the lean version (w04-c5, not in this branch) | 1788 | 31 / 59 ms | about 100 (CPU 15) | ESTIMATE |
| colgrep PreToolUse hook on Bash | 721 | 119 ms | about 86 | ESTIMATE |
| Bash calls in auto mode, the per-call overhead beyond hooks | 721 | about 0.85 s | about 610 | CONJECTURE from n=2 probe |
| lab_status.py mentioned in a Bash command | at most 38 | 0.83 s | at most 31 | upper bound |
| git through the shim, commands containing `git ` | 205 | 32 ms extra | about 7 | ESTIMATE |
| interpreter `site` cost over all Murmuration starts | 1788 | 10 ms | about 18 | ESTIMATE |
| Bash calls of 60 s or more (waiting loops `until ... sleep`) | 48 | 177 s mean | 8482 | CHECKED (transcript timestamps) |
| worker tool time all told / worker span | | | 10626 of 20053 | CHECKED |
