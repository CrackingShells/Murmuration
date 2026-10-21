## S-w05-explorer-w05-d-1
A trivial Bash call costs about 1.3 s in auto permission mode with hooks, 0.93 s with hooks disabled, 0.24 s in bypassPermissions with hooks and 0.08 s with neither. Hooks account for 0.16 to 0.38 s, so about 0.85 s per call is something auto mode does, and I could not name it: an `--allowedTools Bash` rule gave about 1.3 s in the one run that finished. At 721 Bash calls in wave 4 this is about 10 worker-minutes, more than every hook of the plugin. n = 2 runs per cell; the cause (a classifier call, a sandbox, something else) is a guess. Nobody has looked at it because every earlier speed measurement was of hooks.
refs: __reports__/wave-05/explorer-w05-d/bash_floor_probe_raw.jsonl; __instrumenta__/bash_floor_probe.py; __reports__/wave-05/explorer-w05-d/timing_table.md (E)

## S-w05-explorer-w05-d-2
The platform records budget.py's SubagentStart at a median of 605 ms (p90 1085, n = 20) and colgrep's at 276 ms (n = 128); bare, budget.py takes 82 ms and 259 ms when 8 start together (a no-op Python script does 233 ms, so not a lock). The concurrent test explains part of the 7x, not all. Whether PostToolUse and PostToolBatch, which the platform does not record when they print nothing, are also 3 to 7 times their bare cost during a live wave is unknown, and that sum (1646 starts per wave) is the number that decides whether the lean hooks matter.
refs: __reports__/wave-05/explorer-w05-d/hook_platform_durations_all_lab_sessions.md; __reports__/wave-05/explorer-w05-d/concurrent_subagentstart.md; __reports__/wave-05/explorer-w05-d/concurrent_noop_control.md

## S-w05-explorer-w05-d-3
The first Bash call of every headless run took 4.4 to 6.4 s in all 12 probe runs, and `zsh -i -c true` alone takes 4.37 s on this machine (`.zshrc` loads brew, zsh-patina, conda, mamba and nvm), while `zsh -l -c true` takes 38 ms and sourcing a shell snapshot 25 ms. I did not show that the first call pays the interactive-shell cost. If it does, every headless probe run of the lab (137 in wave 4, 10 982 hook starts) pays about 4.4 s that no plugin file controls. Subagents of a session did not show it (their first Bash was about 1 s).
refs: __reports__/wave-05/explorer-w05-d/bash_floor_probe_raw.jsonl; timing_table.md (A, E)

## S-w05-explorer-w05-d-4
The colgrep-mcp hook on PreToolUse Bash was cancelled once at its 10 s timeout (10 238 ms, a `uv run` start) in the wave-4 PI session, and `uv run` costs 119 ms against 72 ms for `python3 -S -I`. The hook's own comment says "uv run 0.09 s". A hook that can hang for 10 s on a Bash call is a risk to a run that works alone; I do not know what made it hang (a lock on uv's cache from parallel starts is my guess).
refs: __reports__/wave-05/explorer-w05-d/hook_platform_durations_wave4.md; __reports__/wave-05/explorer-w05-d/timing_colgrep_hook_n30.md

## S-w05-explorer-w05-d-5
80 % of the worker Bash time of wave 4 (8482 of 10 578 s) is 48 calls of 60 s or more, mostly `until ... sleep 10` loops that wait for headless runs, and the PI has no message path into a worker that sits in one (see S-w05-explorer-w05-a-4). Whether those waits shorten if the workers launch the runs in the background and hand back, rather than polling, is untested; `waiting-on-processes@cracking-shells` is enabled on this machine and I did not look at what it does.
refs: __reports__/wave-05/explorer-w05-d/bash_time_buckets_wave4.txt; __reports__/wave-05/explorer-w05-d/tool_time_wave4_pi_session.json
