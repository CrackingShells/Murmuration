## symbols
cold premium: cache-write tokens x (2.5 - 0.1) USD per million, for a request whose cache was lost (idle over 5 min, or a tool wait over 5 min); an ESTIMATE of what a warm cache would have saved.
strict / prefix / wide orientation: three bounds of the share of spend before real work, defined in `__reports__/wave-05/explorer-w05-c/w4/summary.md` ("Orientation, three bounds").

## S-w05-explorer-w05-c-1
A stale background loop resumed a finished author at full cache price. Author-w04-4 started a 600 s `until` wait, it was moved to the background, the author handed back, and the "failed" task notification reopened it 532 s later: 337,631 cache-write tokens (USD 0.85) for one turn saying nothing was needed. It never happened in waves 1 to 3 (0 of 22 resumes) and once in wave 4. What else can wake a stopped worker cold (a task notification from another agent's task reached reproducer-w04-10 as well)? And does the platform let a worker end its own background tasks before hand-back, or only the PI?
refs: `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-4-3417be/c533f1c6-c56e-4c8d-b6ff-e90c3ddea2f4/subagents/agent-ab28dda4375d2902b.jsonl` rows 575 to 594; `__reports__/wave-05/explorer-w05-c/w4/summary.md` cold table; reproducer-w04-10 rows 82 and 97 of `agent-a74cf750cfd8361b2.jsonl` (a task-notification naming task ab1d2adaab8976244, author-w04-3's id).

## S-w05-explorer-w05-c-2
The colgrep path instruction fails in one way in wave 4 and in another here. `paths: ["__instrumenta__"]` gave PATH_NOT_FOUND in two wave-4 workers (relative paths not accepted); in this session the same call returned hits from `/Users/hacker/Documents/src/CrackingShells/Murmuration/__instrumenta__`, the plugin source, so a worker would have searched for reusable scripts in a folder that does not contain this lab's or wave 4's helper files, and my own new `w05c_worker_phases.py` was missing from the hits. Is the server's working directory the first "additional working directory" in every session, and did wave 4's E3 and c4 measure script reuse with the right folder?
refs: this session's two `search` calls (relative, then absolute); `__reports__/wave-05/explorer-w05-c/w4/summary.md` failed-call list (reproducer-w04-2 req 7, reproducer-w04-4 req 6); `agents/author.md` lines 25 to 26 and the three sister files.

## S-w05-explorer-w05-c-3
Output is a third of the spend and I cannot see it. 683 of 716 transcript records hold the output-token count at start of stream (a few tokens), and `thinking_tokens` is only visible on the 33 final records (23% of their output). The harness estimates output as content characters / 1.3; on the 33 records that have both, the ratio is 1.73, which would lower the output share from 33% to about 25%. Both are consistent with the harness spend matching the sum I computed, because both use the same estimate. Is there any record of the true output tokens per request, and does `effort: high` with thinking on explain why a request that issues one `ls` still produces tokens?
refs: raw transcripts, `usage.iterations` records; `__reports__/wave-05/explorer-w05-c/00-findings_v0.md` table row "Output share is soft"; `scripts/budget.py` line 106 to 109 (CHARS_PER_TOKEN).

## S-w05-explorer-w05-c-4
The wave's wall time (88 min) is the three long authors, and I did not find out what set their length. Author-w04-2, -3, -4 worked 33, 49 and 54 minutes before their first hand-back, 73% of their seconds in `run` calls, 38% of all workers' seconds in 25 waits over 2 minutes (cells of `claude -p`). Were those cells run one after another because the protocol said so, or could they have run side by side? The speed question for the lab is in that answer, and orientation and exchange are 2% of seconds.
refs: `__reports__/wave-05/explorer-w05-c/w4/summary.md` "Tool waits over 120 s"; `__reports__/reflective_run/w04/00-experiment_protocol_v0.md` (in the wave-4 lab); harness `raise` events of author-w04-2, -3, -4.

## S-w05-explorer-w05-c-5
The four simultaneous authors' `start` lines in the harness are wrong. Two pairs of workers dispatched in the same second have each other's name in `harness.jsonl` (4 of 31 starts), and the first four authors' starts log B=3, T=20, source `unknown`, though their briefs say 4/30, 8/60, 12/60, 8/60. The limits were right later (the `raise` lines show `B_before` 8 and 12), so which of the early `note` lines were computed against the wrong B or T? And does `lab_status` use the `start` name anywhere?
refs: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417be/__statera__/harness.jsonl` lines 1 to 4 and the two `10:38:48` starts; `agent-*.meta.json` names; `scripts/budget.py` lines 440 to 454.

## S-w05-explorer-w05-c-6
The harness tells workers to use a tool they do not have. A bare `sleep 45` is answered "Blocked ... use Monitor with an until-loop", Monitor is in none of the four `tools:` lines, and a reproducer that tried it got "No such tool available". Ten blocked sleeps in 8 of 15 workers (25 in 23 of 44 before). Is the block coming from Claude Code itself (so a plugin cannot change it) or from a hook, and does adding `Monitor` to `tools:` make it work for a subagent?
refs: `__reports__/wave-05/explorer-w05-c/w4/summary.md` failed-call list (reproducer-w04-2 req 25, 22, 23); `agents/*.md` line 5.
