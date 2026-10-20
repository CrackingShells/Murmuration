## S-w04-reproducer-w04-9-1
The analyser that scores items took the first line naming a file, so a prose sentence in a report ("Lowest overall: f058 total 317038 ...") counted as the f058 row and was scored wrong; the head carried "70 (69)" and "one wrong row in 369" until the author regenerated. Any metric that parses a free-text report against ground truth can be moved by prose that quotes an item. The earlier w04-c2/c3 numbers were checked unchanged by the author; w04-c8's E1b items were not part of my brief.
refs: /private/tmp/murmuration-w04/author-w04-2/runs/e2b-c2/lab/__reports__/wave-04/explorer-w04-e2bc2/00-findings_v0.md line 13; __instrumenta__/w04c9_verify_e2b.py; __reports__/reflective_run/w04/author-w04-2/derived2/results_e1b_e2b.tsv (e2b-c2 row, commit 1acb430)

## S-w04-reproducer-w04-9-2
In arm C the hook still logged `stop` and `halt` lines (e2b-c1: 3 stops, 7 halts; the other C runs none) although the wrapper dropped the answers. Those lines say that a ceiling block and a `continue:false` backstop would have fired in c1 and not in c2 and c3. The author's `stops` column therefore counts events in C that the worker never saw; a reader of derived2 who sums `stops` by arm would read C as "stopped 10 times". The head does not state that the column is the would-be count.
refs: runs/e2b-c1/lab/__statera__/harness.jsonl (events stop, halt); derived2/results_e1b_e2b.tsv columns `stops`, `notes_over` for e2b-c1

## S-w04-reproducer-w04-9-3
Same task, same price table, C runs cost 0.596, 0.465, 0.475 USD for 70 files. Cache reads (2.67M, 2.51M, 2.45M tokens) and cache writes (63k, 55k, 54k) differ by 9% and 17%, but cost differs by 28%; recorded output tokens are 1101, 1171 and 1151 over 71 to 76 requests (about 15 per request), which cannot be real output, so the hook's `max(recorded, chars/1.3)` rule is doing the work. I could not tell from the transcript whether c1's extra 0.12 USD is thinking output or a cache-tier difference; this is the spread that makes "full deliverable 1.49 to 1.98 B" a wide range for sizing.
refs: ~/.claude/projects/-private-tmp-murmuration-w04-author-w04-2-runs-e2b-c1-lab/*/subagents/agent-*.jsonl (usage fields), runs/e2b-c{1,2,3}/meta.json (model_usd)

## S-w04-reproducer-w04-9-4
The N-a2 run finished 70 of 70 by batching f046 to f070 in one call "because one call per file would have gone past the USD 0.30 budget" and wrote "I went over budget (106% at the last step)". It is the cheapest complete deliverable in the experiment (0.343 USD, 48 requests) and it violates the brief's explicit procedure. The note produced the outcome the PI would most want (full deliverable, near budget) through the behaviour the brief forbade. The E2b metrics do not score procedure adherence, so n2 and n3 rate this run best. Whether the notes should be allowed to move a worker off its stated method is a design question the claim cannot see.
refs: runs/e2b-a2/lab/__statera__/handbacks/*.md; runs/e2b-a2/lab/__reports__/wave-04/explorer-w04-e2ba2/00-findings_v0.md lines 12 and 97

## S-w04-reproducer-w04-9-5
N-a1 says finishing needs "roughly USD 0.35 more at the same rate"; N-a3 says "roughly USD 0.08 more" for 14 files; C runs finished all 70 at 0.465 to 0.596. N-a1's total would be about 0.64, above every C run, and N-a3's about 0.41, below every C run. The two hand-backs' resume estimates disagree by a factor of 2 in per-file cost for the same task, and the first one is 33 files at 0.285 USD (0.0086 per file) against C-c3's 0.0066: the early part of the context is not cheaper in N-a1. I did not find the cause.
refs: runs/e2b-a1/lab/__statera__/handbacks/*.md, runs/e2b-a3/lab/__statera__/handbacks/*.md, runs/e2b-*/meta.json (usd)
