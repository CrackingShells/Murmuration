---
type: findings
wave: wave-05
author: explorer-w05-d
date: 2026-10-21
version: v0
decision-required: confirm
---

# Machine-side cost of operating the lab: findings (v0)

Left the brief once: I also measured the cost of a plain Bash tool call and of the platform's own hook records, because the brief's list (hooks, lab_status, init, python, git) accounts for about 5 of the 88 minutes of a wave and a per-call overhead outside the plugin was larger.

## Result

- The machine side of wave 4 is small beside waiting. Of 334 worker-minutes, 141 sat in 48 Bash calls of 60 s or more (waiting loops for headless runs); all hook starts of the plugin add up to about 156 s serial (1788 starts), the colgrep hook to about 86 s, `lab_status.py` to at most 31 s. [source: `timing_table.md` F; `tool_time_wave4_pi_session.json`; `bash_time_buckets_wave4.txt`] ESTIMATE for the sums, CHECKED for the waits.
- Per tool call, the biggest machine-side piece is not a Murmuration script. A trivial Bash call in a headless run costs about 1.3 s with auto permission mode and the user's hooks, 0.93 s with hooks disabled, 0.24 s in bypassPermissions with hooks, 0.08 s with neither (n = 2 runs per cell, six calls each). So auto mode adds about 0.85 s per Bash call and hooks about 0.16 to 0.38 s. [source: `bash_floor_probe_raw.jsonl`, `__instrumenta__/bash_floor_probe.py`] CHECKED at n = 2 per cell; the cause of the auto-mode cost is CONJECTURE (an `--allowedTools Bash` rule did not remove it in 1 run).
- `lab_status.py` takes 830 ms here (306 sessions, 640 files, 228 MB) and grows with bytes read (260 ms at 11 MB, 825 at 228 MB). Three `git worktree list` calls cost 125 ms of it (the macOS git shim makes each 56 ms against 24 ms for the real binary). A per-file parse cache (key: size and mtime) brings it to 306 ms, with output byte-identical on a frozen copy of the transcripts. [source: `timing_lab_status_variants_n12.md`, `timing_lab_status_scale_n10.md`, `__instrumenta__/lab_status_variants.py`] MEASURED on a patched copy (not in the plugin); the cache's design (where it lives, invalidation across machines) is CONJECTURE.
- Simplest changes, ranked by seconds saved per wave: (1) drop the second budget start per tool call and gate the main thread (w04-c5's lean version already does the gate: about 56 s of 156 s, CPU 71 to 15 s) [ESTIMATE from w04-c5 ratios]; (2) the lab_status cache (about 20 s per wave if it runs 38 times, but a human waits 0.8 s each time); (3) one git call in lab_status (125 ms per run, trivially safe); (4) outside the plugin: the auto-mode cost of 0.85 s per Bash call, about 10 minutes of worker time per wave, dwarfs all the plugin items put together. Nothing in the plugin removes "most" of the machine side, because most of it is not in the plugin.

## Table

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| One Murmuration hook start, bare | main 80 ms, short worker 84, 5.56 MB worker 110; floors `sh` 31.5, `python3 -S -I` 53.7, `python3` 64.4 (n = 40) | MEASURED | `timing_hooks_head_n40_summary.txt`; `__instrumenta__/hook_cost_time.py@4a6a533`; reproduces w04-c5 (90 / 126) |
| Same hook as the platform records it | SubagentStart budget.py median 605 ms, p90 1085 (n = 20) against 82 bare; colgrep policy 276 / 654 (n = 128) | MEASURED | `hook_platform_durations_all_lab_sessions.md` |
| Cause of the 7x | N starts at once cost 79 / 140 / 192 / 259 ms at N = 1 / 3 / 5 / 8; a no-op Python script costs 63 / 125 / 175 / 233, so no lock in budget.py; process starts do not parallelise on this machine | MEASURED (8 reps) | `concurrent_subagentstart.md`, `concurrent_noop_control.md`; `__instrumenta__/hook_concurrent_start.py` |
| Starts per wave 4 (PI session) | 1788 (843 PostToolUse, 803 PostToolBatch, 29 + 29 handback, 15 dispatch, 69 start/stop); headless probe runs of wave 4: 10 982 more across 137 runs | ESTIMATE (transcript rules of `hook_count_invocations.py`; the transcript does not record silent hook runs) | `starts_wave4_pi_session.json`, `starts_wave4_headless.json`; `__instrumenta__/hook_starts_per_wave.py` |
| Share of 1646 PostToolUse/PostToolBatch starts that print anything | 10 PostToolBatch records with output in the whole PI session (0.6 %) | MEASURED (lower bound, silent runs are not recorded) | `hook_platform_durations_wave4.md` |
| colgrep-mcp's PreToolUse hook on every Bash call | 118.8 ms bare (`uv run --no-project --quiet python`) against 78.4 with `python3`, 72.4 with `python3 -S -I`; 721 Bash calls in wave 4 give about 86 s; one run was cancelled at its 10 s timeout | MEASURED / ESTIMATE | `timing_colgrep_hook_n30.md`; `hook_platform_durations_wave4.md` |
| Python start: editable install | `site` 9.8 ms of import time, 7.7 ms of it the hatchling finder; `python3 -c pass` 64.4 vs 53.7 ms with `-S -I` | MEASURED | `python3 -X importtime -c pass`; same table |
| git through the shim | `/usr/bin/git worktree list` 56.0 ms median, the CommandLineTools binary 24.2, Xcode's 25.1 (n = 25, interleaved) | MEASURED | inline run in this session (no file; rerun: 25 rounds of the three binaries) |
| lab_status.py wall | 830 ms shipped; 706 one git call; 684 + bytes filter; 306 + parse cache; identical output | MEASURED on patched copies | `timing_lab_status_variants_n12.md` |
| lab_status.py scaling | 260 / 305 / 371 / 635 / 825 ms at 25 / 50 / 100 / 200 / 306 sessions (11 to 228 MB); the cache variant 153 to 307 ms | MEASURED (n = 10) | `timing_lab_status_scale_n10.md` |
| lab_init.py | 0.60 to 0.68 s to initialise a fresh lab with its 4-file colgrep index; 0.10 s to add a question; `colgrep init` on this lab: 8.0 s once (68 files added), 0.10 to 0.12 s when up to date | MEASURED (n = 2, 1, 1, 3 single runs) | inline runs in `/private/tmp/murmuration-w05/explorer-w05-d/li1, li2` |
| First Bash call of a session | 4.4 to 6.4 s in all 12 probe runs; `zsh -i -c true` alone is 4.37 s (`.zshrc` loads brew, zsh-patina, conda, mamba, nvm); a login non-interactive shell is 38 ms | MEASURED; link between the two is CONJECTURE | `bash_floor_probe_raw.jsonl` |
| Worker time by kind, wave 4 | span 20 053 s; tool time 10 626 s; Bash 653 calls 10 578 s of which 8482 s in 48 calls of 60 s or more (80 %); 432 calls of 0.5 to 2 s sum to 537 s | MEASURED | `tool_time_wave4_pi_session.json`, `bash_time_buckets_wave4.txt` |

## Worst-fitting case

The story "the machine side is small" fits worst here: a probe cell, n = 2 runs. Auto permission mode adds about 0.85 s to every Bash call. At 721 Bash calls that is 10 minutes of worker time in wave 4, more than the plugin's hooks (2.6 min serial) and the colgrep hook (1.4 min) together. I could not tie it to anything (the classifier's model call is a guess; an allow rule did not shorten it in one run), and 0.85 s is 4.4 times the 0.19 s that two hook starts add. It also belongs to the Desktop's choice of mode, which this lab does not set. Next to it, the typical case: a hook start (80 ms) that does nothing 99 % of the time.

Second misfit: the platform records budget.py's SubagentStart at 605 ms median, 7 times my bare 82 ms; the concurrency test explains a factor of 3 to 4 at N = 8, not all of it (the platform also starts two other hooks per worker, and the load was higher).

Prior work: nothing fetched; the wave-4 claim w04-c5 is in this repository (`__pondus__/w04-c5.md`), CITED as the lab's own record.

## Not covered

- Model time (what the PI main thread spends USD 75 on; waits between author, verifier and exchange): other explorers.
- The lean hooks (66a0902) were not re-measured here: this checkout runs the old `scripts/budget.py` (863 lines); the lean figures are quoted from w04-c5 and are ESTIMATES applied to wave 4's counts.
- Not tested: whether an allow-list or another permission mode removes the auto-mode cost; the headless probe ran haiku without the Murmuration plugin, so Murmuration's own 2 starts per tool call were not in those cells (its cost is added from table A).
- The cache for lab_status was only built on a copy and checked for equal output on one frozen state; no selftest of it, no concurrent-writer test, no cold-versus-warm comparison on a second machine.
- lab_init timings are single runs. Wave 4's headless runs (137 sessions, 10 982 starts, each paying a first Bash call of about 4.4 s) were counted, not priced.
- `PostToolUse` and `PreToolUse` runs are not recorded by the platform when silent, so real per-call hook latency in a live wave is unmeasured; only the noisy ones (SubagentStart, PostToolBatch notes) have platform durations.

## Steering questions

- [now] Is the 0.85 s per Bash call in auto mode (n = 2) worth a proper probe (a dozen cells: mode, allow rule, sandbox on/off) before any further plugin work on speed? It is the largest item I found and it is outside `scripts/`.
- [now] Does the PI want the lean hooks (4c46fe4 / 66a0902) landed, given that their saving is about 56 s of an 88 minute wave (ESTIMATE) and the one E4 criterion that missed was long-worker wall at 0.516 against 0.5?
- [now] The `lab_status.py` cache and the single git call: file as a claim (cheap, equal output on a frozen state), or leave, since `/lab-status` runs a few times per wave?
- [later] Tell the colgrep-mcp plugin owner (the user) that its Bash hook costs 119 ms through `uv run` against 72 ms through `python3 -S -I`, and was once cancelled at the 10 s timeout.

## Pointers

All files in `__reports__/wave-05/explorer-w05-d/` unless noted; scratch in `/private/tmp/murmuration-w05/explorer-w05-d/` (patched `lab_status` copies in `ls/`, frozen transcripts in `cfg/`, scaled configs `cfgk*`).
- `timing_table.md`: the timing table (all of A to F).
- `timing_hooks_head_n40.jsonl`, `timing_hooks_head_n40_summary.txt`: `python3 __instrumenta__/hook_cost_time.py --variant head=<git archive HEAD> --payloads __reports__/reflective_run/w04/author-w04-4/derived/recorded_payloads_rec1.jsonl --transcripts short=<agent-a3ca5291991a08315.jsonl>,long=<agent-a50b3982ac2a64503.jsonl> --reports-src <head>/__reports__ --fx <S>/fx --n 40 --spawn posix --out ...` (77 s; dangling symlink `work_link` removed from the archive copy first), then `hook_cost_summary.py`.
- `timing_colgrep_hook_n30.*`: `python3 __instrumenta__/cmd_cost_interleaved.py cases_colgrep.json --n 30`.
- `timing_lab_status_variants_n12.*`, `timing_lab_status_scale_n10.*`: `python3 __instrumenta__/lab_status_variants.py <repo> <S>/ls`, then `cmd_cost_interleaved.py` over `cases_variants.json` / `cases_scale.json` (CLAUDE_CONFIG_DIR = frozen copy; equality: `cmp fout_v0.txt fout_v1.txt` and v2, v3, v3warm).
- `concurrent_subagentstart.md`, `concurrent_noop_control.md`: `python3 __instrumenta__/hook_concurrent_start.py <head> <fx lab> <payloads> --n 1,3,5,8 --reps 8 [--script noop.py]`.
- `counts_wave4_pi_session.json`, `starts_wave4_*.json`: `hook_count_invocations.py`, `hook_starts_per_wave.py --ms-wall 90 --ms-cpu 40`.
- `tool_time_wave4_pi_session.json`, `bash_time_buckets_wave4.txt`, `tool_median_by_session_class.txt`: `tool_time_split.py`, `bash_time_buckets.py --top 10` on the wave-4 PI session `c533f1c6` (in `-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-4-3417be`), and an inline comparison against 137 headless runs.
- `hook_platform_durations_*.md`: `hook_platform_durations.py <mains>`.
- `bash_floor_probe_raw.jsonl`: `python3 __instrumenta__/bash_floor_probe.py /private/tmp/murmuration-w05/explorer-w05-d/probe --reps 2` (haiku, 8 runs, about USD 0.08 in all).
- Scripts, all `__instrumenta__/<file>@<commit of this report's commit>`: `cmd_cost_interleaved.py`, `lab_status_variants.py`, `hook_concurrent_start.py`, `hook_starts_per_wave.py`, `tool_time_split.py`, `bash_time_buckets.py`, `hook_platform_durations.py`, `bash_floor_probe.py`.
