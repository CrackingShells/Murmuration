## S-w06-author-w06-4-1
After two runs in which the server failed to restart (`out_b0`, `out_b1`, restart that exits), the next two runs with the same plugin path and the same `.mcp.json` (`out_c0`, `out_a0`) never even started a connection to the server: no "Starting connection" line for `plugin:murmuration:hooks` in the debug log, every hook "not connected" from the first tool call, and `server.pid` pointing to a dead process. A fresh export directory per run fixed it. So the platform seems to remember a failed MCP server across sessions (a cache keyed by plugin path or config; I did not find its lifetime or where it is kept). If that holds for real use, a failed restart may keep the hooks down in the next sessions of the same project, not only in the run where it happened, and `outage.py` would say "hooks down" at each worker start until the cache expires.
refs: /private/tmp/murmuration-w06/author-w06-4/runs/out_c0/dbg.log and runs/out_a0/dbg.log (absence of the connection lines; first runs of the chain: `run_out.log`); `__instrumenta__/w06c4_run.py` (one export per wrapped run, comment)

## S-w06-author-w06-4-2
The platform accepts a server whose `tools/list` is empty and still calls its tool from an `mcp_tool` hook (6 hooks per event class, all runs). That keeps the tool out of every agent's request with no `disallowedTools` entry, but it is undocumented behaviour I found by trying. A later version that checks a hook's tool against the server's list would turn every hook into a failure at once, and the only visible sign would be the hook-failure text of `outage.py`. I did not test that failure (I have no way to make the platform do it).
refs: `scripts/hook_server.py` (`tools/list` answers an empty list); `__reports__/wave-06/author-w06-4/tables.md` (m3-style table)

## S-w06-author-w06-4-3
The hang test shows 6.0 s per boundary (3 s per hook at `timeout: 3`, PostToolUse then PostToolBatch, run one after the other), and the next boundaries 2.5 to 4.9 s, never the 7.4 to 7.9 s carry-over stage 1 saw with `timeout: 10`. I expected the platform's 30 s connection timeout to keep adding to each boundary; here it does not exceed the two hook timeouts. I do not know whether a connection attempt that was started by one hook and abandoned at its timeout is simply not waited for, or whether the carry-over only appears when the hook timeout is longer than the rest of the connection window.
refs: `__reports__/wave-06/author-w06-4/tables.md` (s3 table, column "boundaries over 1 s"); dbg.log lines `classic.PostToolUse settled in` of runs `g_c0`, `f_c0`, `f_c1`

## S-w06-author-w06-4-4
When the worker itself kills the server in the middle of its run and the restart fails (`mid` runs), the worker is told only at its hand-back (the first hand-back is denied once, asking for a `HOOKS DOWN:` line), and the PI is told by no hook at all within the run: 0 of 2 in the `f_mid` runs (the PI's later tool boundaries fail silently). The PI is told after the next Agent call returns (`PostToolUse` on `Agent|Task`) or by `/lab-status`. The only channel at the moment a worker ends is the worker's own hand-back text. I found no hook event that reaches the PI at a worker's end without the server.
refs: `__reports__/wave-06/author-w06-4/tables.md` (s3 rows `mid`); `scripts/outage.py`

## S-w06-author-w06-4-5
The s2 margin comes almost entirely from the safety net, not from the server: the 40 `mcp_tool` calls of a 2-worker run cost 100 to 120 ms in all, and the 6 `outage.py` starts (SubagentStart, PostToolUse on Agent, PreToolUse on SubagentHandback, per worker) cost 730 to 930 ms, 6 to 8 times as much, for 150 ms each even with `python3 -S -I` and lazy imports (main's `budget.py` starts cost 120 ms each on the same machine, with the user's other plugin hooks running beside). So the build lands at 18 to 19% of main's hook time because of three command starts per worker whose only job is to say something when the server is down.
refs: `__reports__/wave-06/author-w06-4/tables.md` (s2 table); `hooks/hooks.json`

## S-w06-author-w06-4-6
The hook payload fields reach the server as strings: an absent field is "" and an object a JSON string. The server drops "" to restore absence. That is exact for the scripts' reads (`permission_mode` stays absent on SubagentStart, as in the process version's log: `null`), but it would hide a field that is legitimately "" and means something different from absent. None of the fifteen fields the scripts read does (m1 list of w06-c3), checked by reading the code and by the 197-transcript replay, not by a platform probe of every field.
refs: `scripts/hook_server.py` (`clean`); `__reports__/wave-06/author-w06-4/s1_replay_final_seq.txt`

## S-w06-author-w06-4-7
Request 0 of the main thread and of workers differs between runs by up to about 430 tokens in both arms (31828 or 31862 for the main thread, 12648 to 13075 for workers, independent of arm), as in stage 1; the check that the hidden tool adds nothing therefore rests on the tool not being listed (the server's list is empty) and on the two arms' values interleaving, not on equal counts.
refs: `__reports__/wave-06/author-w06-4/tables.md` (m3-style table)
