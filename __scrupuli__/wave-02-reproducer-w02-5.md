## S-w02-reproducer-w02-5-1
The platform tracker line ("USD budget used / total") shows the whole session's spend (the haiku parent included, 0.017 at the first read) against a total of 0.7 or 0.9, never against the worker's B = 0.06. So a worker that wants to self-limit by the tracker has to subtract and compare with the start note's B itself. The pilot workers that did this had B in the brief and a count instruction. Does the tracker really count as "in the worker's context" for the confound, or is it nearly inert unless the brief tells the worker to use it? q1/q2 (n = 2) cannot say.
refs: scratchpad w02/author-w02-3/runs/q1 and s1 subagent transcripts, `budget_usd` attachments (used 0.0288 to 0.177, total 0.7)

## S-w02-reproducer-w02-5-2
In every s cell the first hand-back after the stop is denied by the report check, so the worker writes the report, then gets the stop notice again (2 to 3 stop events), then hands back. The stop-obedience cell therefore also tests the deny. Would a stop notice alone, with a report already on disk, produce the same next-call-is-hand-back? l1 hints it does for the note, but l1 is a different B and a note.
refs: summary.tsv s1 to s5 `tool_calls_after_first_stop` (SubagentHandback,Write,Write,SubagentHandback)

## S-w02-reproducer-w02-5-3
Finishing cost after the first notice is mostly output and a few cache-reading requests; at the end of l1 the context is about 28k tokens, so a request costs about 0.003 USD for cache reads. At B = 3.0 on real files the context may be 10 to 50 times that. No cell gives the cost of finishing as a function of context size; arm B is the first chance. Could the 0.8 note's finishing share be read off per-request usage in arm B transcripts directly?
refs: `post_note_usd_est` column of summary.tsv (a1 0.0119, l1 0.0345, h1 0.051)

## S-w02-reproducer-w02-5-4
b1's `start` line logs B = 3.0 (the default) while later lines use 0.06 from the brief's `Budget:` line, so any reader of `harness.jsonl` that takes the first `start` for B (my own first script did) gets 0.03 as the end fraction. Is the start line written before the brief is parsed, or is `from_brief` simply false there by design? Not wrong, but a trap for the people who read the log.
refs: runs/b1/lab/__statera__/harness.jsonl line 1 (from_brief false, B 3.0), lines 3 to 5 (B 0.06)

## S-w02-reproducer-w02-5-5
The claim is verified at a state that is partly uncommitted (summary.tsv, analyze.py, run_all.sh modified; scripts pinned by sha256 prefix only). The label MEASURED asks for the commit. Should a verifier insist that the evidence be committed before SUPPORTED, or is a hash enough in a lab where the PI commits later?
refs: `git status` at the start of this run; head `evidence:` line
