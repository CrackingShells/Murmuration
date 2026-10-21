## S-w06-author-w06-3-1
Request 0 of a worker is not byte-for-byte reproducible: five identical-shape worker requests (same system, tools, brief) differ by up to 7 tokens (5938 to 5945), and the lead's request 0 by about 470 (46.4k and 46.85k clusters), independent of whether the server is installed. So the pre-registered "0 tokens" can only be tested as "no difference outside noise plus identical shape hash plus a control that shows an addition". I did not find the cause of the jitter (a guess: per-session ids; for the lead, MCP servers of the user's own configuration connecting before or after request 0).
refs: __reports__/wave-06/author-w06-3/tables.md (section m3)

## S-w06-author-w06-3-2
A plain `kill` of the server by its pid is not an outage: the platform restarts the server at the next hook (connected in 71 to 87 ms) and the hook succeeds, so the registered m4 scenario has no failure to show. The failures only appear if the restart also fails (exit or hang), which I had to simulate with a `refuse` file. What happens when a real server crashes on its own (a bug in a handler) is therefore "restart, lose memory": harmless for a server whose state is on disk, silent for one that keeps it in memory.
refs: __reports__/wave-06/author-w06-3/tables.md (section m4, rows m4a*); pilot `out_pilot-outage/server.starts` (two pids)

## S-w06-author-w06-3-3
In the hang variant the hook `timeout: 10` is honoured per hook, but PostToolUse and PostToolBatch each wait 10 s, so a tool boundary waits 20 s; the next boundary waits 7.4 to 7.9 s more, because the platform's own 30 s connection timeout is still running. The `timeout` of a hook does not shorten a connection attempt that another hook already started. Is a hung server (a stuck handler) more likely than a dead one? I did not test a hung handler on a live connection (the server answers but slowly).
refs: runs/m4c0 and runs/m4c1 dbg.log lines "classic.PostToolUse settled in 10005ms", "classic.PostToolBatch settled in 10011ms" (not committed: account identifiers); tables.md section m4

## S-w06-author-w06-3-4
A dead server leaves one `hook_non_blocking_error` record per hook in the transcript and nothing in the model's context: the lead's final answer said nothing stopped, while the DENYME Agent call went through. No script of the lab reads `hook_non_blocking_error` or `hook_cancelled`. If the lab moves its guard to a resident server, who would notice the guard has gone? This is a design input for stage 2's s3.
refs: tables.md section m4 (columns 4, 6, 7); `grep -l "hook_non_blocking_error" scripts/*.py skills/*/* agents/*` returns nothing

## S-w06-author-w06-3-5
SubagentStart's hook record in the transcript has no `durationMs` (the other six events do). The only timing for the one event where the injected context matters is the debug log, with 1 ms resolution and other hooks logging in between: median 6 ms (n = 25, max 15), higher than the 1 to 2 ms of the other classes. PostToolUse on the `Agent` tool (6 ms) and on `SubagentHandback` (5.5 ms) are also higher than on Bash (1 ms). I do not know why the events that end a worker or a dispatch cost more; the user's other command hooks run beside ours there.
refs: tables.md section m5

## S-w06-author-w06-3-6
The platform runs one command hook where two registrations carry the identical command text (the ground-truth log had one record per PostToolUse(SubagentHandback) where the server, with different inputs, got two calls). For the real hooks.json this means two registrations that call `python3 handback.py` and `python3 budget.py` are different command texts and both run, but two `mcp_tool` rows with identical `input` might merge. I did not test the mcp_tool case with identical inputs.
refs: runs/t_auto0 `truth.jsonl` (18 records) against `server.jsonl` (19 calls) in pilot `out_pilot`; not committed

## S-w06-author-w06-3-7
`SubagentStop` fires once per turn that ends in auto mode, not once per worker: one of 39 workers stopped twice (a draft turn, then the hand-back), and the server got both. `handback.py` already writes `draft` and `delivered` sections for this, so the registered behaviour is the same, but my m2 reference for SubagentStop is the platform's own hook record, not an independent count.
refs: runs/m3_on_1 `server.jsonl` (agent a10f22: SubagentStop at two times); tables.md section m2
