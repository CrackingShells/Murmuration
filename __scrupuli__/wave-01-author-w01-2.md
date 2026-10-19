## S-w01-author-w01-2-1
The permission mode, not any Desktop flag, decides whether a subagent transcript keeps final output tokens, and no flag I tried explains why. With `--permission-mode auto` (and `plan`) the last record of every request keeps the start-of-stream `output_tokens` (2 to 20) and `stop_reason: null`; in `auto` the request that carries the essay is a `SubagentHandback` tool call. `bypassPermissions`, `default`, `acceptEdits`, `dontAsk` give final values. I cannot say if the cause is `auto` itself or the presence of `SubagentHandback` (they co-occur; I did not run auto with `SubagentHandback` disallowed). Plan mode truncates the first (tool_use) request instead of the last, so the mechanism is not "last request is cut".
refs: __reports__/reflective_run/w01/author-w01-2/summary.txt; final_stats.txt; runs/ins-fg-on-long-p-inh-p0-dfl-dfl-1/ (auto, snapshot in hooks/); runs/ins-pm-plan-fg-0/; runs/ins-pm-bypassPermissions-fg-0/

## S-w01-author-w01-2-2
A rare permanent truncation outside `auto` and `plan`: 4 of 156 other-non-auto cells (both binaries), all background subagent + short final message + thinking off; the last request keeps 2 to 9 output tokens and `stop_reason: null`, and polling for 4 s never changes it. Twenty background long cells and twenty foreground short cells in the same set had none. Why background plus a short last message?
refs: runs/des-bg-off-short-p-inh-p0-dfl-dfl-0-r1-pk/, runs/des-bg-off-short-p-inh-p0-dfl-dfl-0-r6-pk/, runs/ins-bg-off-short-p-inh-p0-dfl-dfl-0-r7-pk/, runs/ins-bg-off-short-p-inh-p0-dfl-dfl-0 ; summary.txt

## S-w01-author-w01-2-3
SubagentStop sometimes fires before the last request's final usage is in the file (17 of 156 non-auto cells, both binaries; 2.1.302 settled in 0.056 s in four polled cases). Explorer-f's "the transcript route is exact (run1)" was a case where it did settle, so the hook-time sum can be right by luck. Does the hook fire on the agent's last assistant message or on its record flush? I did not read the binary.
refs: runs/des-fg-on-long-p-inh-p0-dfl-dfl-0-r1-hr/hooks/hooks.jsonl; runs/ins-fg-on-long-p-inh-p0-dfl-dfl-0-r3-pk/hooks/hooks.jsonl (field poll)

## S-w01-author-w01-2-4
Cost outside the project: each `claude -p` run adds an entry to `~/.claude/plugins/installed_plugins.json` (PI's message). I ran 192 cells and 4 OTel cells plus 3 early ones before I was told, and I did not check the file before. Is that entry removable, and should any lab experiment with `claude -p` use a scratch HOME (not possible here, auth is in the keychain)?
refs: PI message to author-w01-2; __reports__/reflective_run/w01/author-w01-2/runs/ (about 200 folders; their `work/` folders also create project transcript folders under ~/.claude/projects)

## S-w01-author-w01-2-5
Plan-mode subagents cost about 10 times a normal haiku run (USD 0.17 to 0.18 against 0.006 to 0.009) with the same task; I did not look at why (12 cells, USD 1.9 of the 2.81 total). Also, `SubagentStop` input says `effort: {level: medium}` for a subagent whose parent ran `--effort=high` in the Desktop-like cells; I did not follow this up.
refs: runs/ins-pm-plan-fg-0-pk/; results.jsonl (cost_usd); runs/ins-fg-on-long-p-inh-p0-dfl-dfl-1/hooks/hooks.jsonl (SubagentStop input)

## S-w01-author-w01-2-6
The content-based estimate of output tokens fails by a factor 2.4 (454,849 against 1,075,475 for genesis Sonnet), even though thinking text is in the file. Either the thinking text in those files is a summary of the real thinking, or the main-thread calibration (Opus) does not transfer. Not resolved; the `thinking_tokens` detail in subagent records is also absent, so thinking cannot be recovered per run either.
refs: __reports__/reflective_run/w01/author-w01-2/estimate_out.py (run it on 566fa912)

## symbols
`output_final`: true when every request's last record in a transcript has a non-null `stop_reason` (test R4 of w01-c2).
