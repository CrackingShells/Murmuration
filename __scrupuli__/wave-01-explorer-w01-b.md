## symbols
none new.

## S-w01-explorer-w01-b-1
The only real "pair" on a research question is the PI relaying a verifier to two authors (9 s, about 460 tokens, and the PI added conventions the verifier did not know). No author-verifier conversation exists in any transcript, only six synthetic pings. SA4 is judged on zero real cases, and the relay looks cheap and useful. Which of the two is the design supposed to improve on?
refs: `__reports__/reflective_run/w01/explorer-w01-b/pair_threads.csv`; genesis transcript lines 671 (report), 677, 678 (relay messages); `followups.csv`

## S-w01-explorer-w01-b-2
In the report at genesis line 674 the first line says "Gates: all three pass" while item 4(a) says OVERSTATED. A status header would have been right for the process and wrong for the claim. What should "status" mean in a return: the run (done/blocked) or the outcome of the checked claim? The platform's own `<status>completed</status>` already means the first.
refs: `__reports__/reflective_run/w01/explorer-w01-b/handbacks_coded.csv` (delivery_line 674); transcript `566fa912...jsonl` line 671

## S-w01-explorer-w01-b-3
The harness prepends `[harness: ... instruction-shaped pattern(s) ...]` to 8 of 17 design-session hand-backs (0 of 13 genesis) and rewrites control tags in their bodies. The PI never mentioned it in any of the 8 cases, so it has no visible effect, and it fires on exactly this lab's subject matter (settings.json, bypassPermissions). Does the flag cost anything beyond a parse hazard, and will it fire on every explorer return of this wave?
refs: `__reports__/reflective_run/w01/explorer-w01-b/handbacks.csv` (columns harness_flag, harness_patterns); `82e8a947...jsonl` line 1248

## S-w01-explorer-w01-b-4
A message to a still-running agent is recorded in the receiver's transcript as a bare `queued_command` with no sender; a message to a finished agent carries `from=` or "The coordinator". The user's own mid-run messages use the same bare form. For peer messages to running agents (untested) a transcript-only reconstruction would then have no recorded sender, and the PI could not tell a user message from a peer message there.
refs: `pair_threads.csv` column `form`; `pair_orphans.txt` (the user's messages at 03:22, 03:24, 15:46); `82e8a947/subagents/agent-a04ebecba85274ac9.jsonl` lines 66, 97

## S-w01-explorer-w01-b-5
Eighteen of 20 hand-backs exceeded their brief's word limit (median 1.27x), yet 10 of 30 PI follow-ups were independent checks and none complained about length. Without a limit the median return was 1135 words against 283 with one. Is the limit doing work, or only moving words from the return into the report file?
refs: `__reports__/reflective_run/w01/explorer-w01-b/handbacks.csv` (brief_limit, words, ratio); `summary.txt`

## S-w01-explorer-w01-b-6
What used my 60 turns: I spent roughly the first half on exploration and on re-running extraction after fixing my own bugs (queue-operation lines without uuid duplicated the design session's returns; each tool_use appears on two transcript lines; three receipt forms for messages). Several bash-heavy turns printed long outputs (a harness skill-listing block was appended after some tool results, hundreds of lines each). Another run on the same brief would not need most of those corrections if the extraction script were reused. The limit hit before I wrote the report, so the report was written on the coordinator's request, not at the end of a planned step. The brief asked for a report and puzzles but did not say to write the report before the last extraction.
refs: `__reports__/reflective_run/w01/explorer-w01-b/extract_comm.py` (the dedupe filters), `pair_thread.py` (seen_ids); this explorer's transcript `agent-ac6c27171353e66ed.jsonl`
