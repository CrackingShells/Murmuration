## S-w05-reproducer-w05-1-1
B2 and B3 ran side by side and both wrote /private/tmp/claude-501/job.pid and job9.log; the shared pid file holds B3's pid and B3's last log call shows B2's `time` line. The paragraph's own example (`echo $! > job.pid`) invites a shared-path collision; a `kill` by that file would have killed another run's job. Worth a wording that names a per-run path.
refs: /private/tmp/murmuration-w05/author-w05-1/e5/runs/B3 (subagent transcript, call at 06:54:26 UTC), /private/tmp/claude-501/job.pid, /private/tmp/claude-501/job9.log

## S-w05-reproducer-w05-1-2
The same paragraph produces waits of 240, 241, 250.7, 271 s in the same experiment (workers copy 240, 250 or 270 from the paragraph); the 4-minute rule is a request, not a bound, and a 270000 ms Bash timeout plus a model turn leaves under 30 s of margin to the 5-minute cache lifetime. B3's gap was 277 s.
refs: __reports__/wave-05/author-w05-1/requests_B3.csv row 4 (gap 277.0 s); /private/tmp/murmuration-w05/reproducer-w05-1/e5/runs/B1 (250.7 s call)

## S-w05-reproducer-w05-1-2b
The main-thread-to-subagent switch was decided after a pilot in which A did not show the cache problem (1-hour entries on the main thread). The reason is sound and matches wave 4, but the registered rule would literally have proposed B in main-thread mode. If Desktop PI/main-thread sessions also get 1-hour entries, the paragraph's reason "a longer call loses the prompt cache" applies to subagent workers only; nobody checked what interactive main-thread TTL is on the Desktop.
refs: __reports__/wave-05/author-w05-1/pilot1_mainthread/requests_pilot-A1.csv row 6

## S-w05-reproducer-w05-1-3
Cost in A varies with worker choices that the paragraph does not control: my A1 made 12 quick requests before the 485 s wait (1.459) against 5 in the author's A1 (1.327); the cold rewrite (about USD 0.57) is the stable part. B1 of mine is 0.769 against 0.762.
refs: /private/tmp/murmuration-w05/reproducer-w05-1/e5/runs/A1, __instrumenta__/w05c1_rederive_requests.py output

## S-w05-reproducer-w05-1-4
In my own session the loaded reproducer agent text still says paths: ["__instrumenta__"], and that relative path resolves to the main checkout, not this worktree: a worker following the shipped text would have missed the author's runner, which exists only in the worktree. The working-directory ambiguity (primary directory vs additional working directory) is not tested for a worker that has both.
refs: colgrep search echo, `paths` field, this session; __reports__/wave-05/author-w05-1/c2_colgrep_path.md
