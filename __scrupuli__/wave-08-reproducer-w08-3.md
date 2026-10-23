## S-w08-reproducer-w08-3-1
The compact_boundary `post_tokens` (about 25k) is half the real context of the first request after compaction (7,532 read + 41-42k written, about 49k). The claim's "context before -> after: 120k -> 25k" and the "41.8k post-write" are both measured, but only the second is priced; the first understates the floor. I do not know whether the 41k write is fixed overhead (the real lab's 41,043 at a 91.5k floor says so) or scales with the floor.
refs: /private/tmp/murmuration-w08/reproducer-w08-3/runs/r3_op_B1_5 (stream.jsonl, first assistant record after compact_boundary); __instrumenta__/w08_v3_compaction_cost.py

## S-w08-reproducer-w08-3-2
My re-implementation of the net model gives USD 43.57 at a 150k threshold and 44.65 at 250k (R 2,500, OUT 3,000). The estimate does not discriminate thresholds, yet the landing step asks for a 283,000 window. The case for 250k over a lower window rests on summary quality at a larger context, which is the untested part.
refs: __instrumenta__/w08_v3_net_model.py

## S-w08-reproducer-w08-3-3
Haiku H seed 5: the compaction request had 12,900 uncached input tokens and 10.7k output (USD 0.287), against 2,068 and 5.8k for B1 on the same seed. The authors' haiku H runs showed no such input. Either the hook's text breaks the cached prefix or haiku summaries vary widely; compaction cost on haiku ranges 0.10-0.29.
refs: /private/tmp/murmuration-w08/reproducer-w08-3/runs/r3_hk_H5/debug.log (Forked agent line)

## S-w08-reproducer-w08-3-4
Four of the five questions can be answered by re-reading small files, and the scratch lab's files are 300-700 characters. A summary that lost everything would still pass Q3/Q4 after about 2k tokens of re-reads. The scenario therefore measures what the PI does after compaction more than what the summary keeps; the two Q2 failures are the only items that separate arms.
refs: __reports__/wave-08/author-w08-3/runs_scored.tsv (reread_tok, q2 columns)

## S-w08-reproducer-w08-3-5
`--project-config-root` redirects the settings folder: in my check the localSettings deny rule appears only when the flag points at the folder holding the file. The worktree's and the main checkout's `settings.local.json` are byte-identical, so a deny rule cannot tell which of the two was applied; only the watch-list paths (the author's) distinguish them, and a watch list is not a load. Whether the Desktop really passes the flag is CITED, not run.
refs: /private/tmp/murmuration-w08/reproducer-w08-3/m6/A.log, B.log
