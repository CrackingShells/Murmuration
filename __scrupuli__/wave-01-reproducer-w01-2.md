## S-w01-reproducer-w01-2-1
The detector "every request's last record has a non-null stop_reason" agrees with output exactness in 199 of 199 cells, but it may be close to tautological. A null last record means an early streaming value was kept, and an early value is by construction below the final. Is there any cell where the detector is true and the sum is still off, from a different cause? A different cause cannot be seen here, because no such cell exists in the sample.
refs: __reports__/reflective_run/w01/reproducer-w01-2/all.py (199 of 199 agree)

## S-w01-reproducer-w01-2-2
The 4 rare non-auto inexact cells are all "background, thinking off, short". The fraction (4 of 22 cells of that type) is far above 0 of 20 in the neighbouring cell types, but the cause is unknown. Could the subagent finish before the final usage record is rewritten, so that it is a race rather than a permission-mode effect? If so, the same race could appear in auto and be hidden by the permission-mode effect there.
refs: __reports__/reflective_run/w01/author-w01-2/runs/ins-bg-off-short-p-inh-p0-dfl-dfl-0, __reports__/reflective_run/w01/reproducer-w01-2/all.py

## S-w01-reproducer-w01-2-3
The OTel `subagent_completed` event carries `total_tokens` (35,322 in `otel-ins-auto`), which looks like the footprint of the last request and not spend. Is that the same quantity as the Agent result's `subagent_tokens`? If so, three different places expose the same non-spend number, and a ledger might be tempted to use any of them.
refs: __reports__/reflective_run/w01/author-w01-2/runs/otel-ins-auto/otel_events.json

## S-w01-reproducer-w01-2-4
`otel_events.json` in the repo tree carries user.email, account uuid and organization id. The same file could be committed by accident. A ledger design that relies on OTel must say where the receiver stores events, and whether the email is stripped.
refs: __reports__/reflective_run/w01/author-w01-2/runs/otel-ins-auto/otel_events.json

## S-w01-reproducer-w01-2-5
My 4 new runs added entries to ~/.claude/plugins/installed_plugins.json (not edited by me). Across the author's 199 runs and the other agents' runs this file may have grown by hundreds of entries. Is that bookkeeping pollution measured by anyone? It is a hidden cost of the headless-probe method.
refs: ~/.claude/plugins/installed_plugins.json
