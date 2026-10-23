## S-w08-explorer-w08-g-1
Fresh Sonnet 5.5 subagents send every independent Read in one message without being told (8 of 8 files in 4 of 4 runs, 16 of 16 in 3 of 4), yet 92% of lab worker requests carry one call. The token test finds only 95 of 4,239 requests with an independent partner, and 65% of the 2,542 single-call pairs are Bash-exec then Bash-exec. What do those pairs do? If they are "run, look at the output, run the next thing", the request count is set by the work, not by a habit a line can change; but the token test cannot see semantic dependence in either direction, and I did not read those 1,643 pairs.
refs: __reports__/wave-08/explorer-w08-g/pairs_why_not.tsv; __reports__/wave-08/explorer-w08-g/arms_task4_readonly_8.tsv; __reports__/wave-08/explorer-w08-g/arms_task5_readonly_16.tsv

## S-w08-explorer-w08-g-2
In the read-only 16-shard task, 2 of 8 runs (one base, one with the line) did not read the 16 files at all: they counted lines with two Grep calls, 6 calls instead of 20, USD 0.0251 and 0.0267 against 0.034-0.044, and answered right. Nothing in the prompt suggests it. Is "fewer calls by another tool" a larger lever than batching (a cheaper tool route) and does it appear in lab workers (they have Grep, colgrep, Bash)? I did not look for such substitutions in the lab transcripts.
refs: __reports__/wave-08/explorer-w08-g/arms_task5_readonly_16.tsv rows V-base-4 and V-lever1-2 (calls_by_request 2,1,2,1 and 2,1,2,0,1); raw runs in /private/tmp/murmuration-w08/explorer-w08-g/t5/runs/

## S-w08-explorer-w08-g-3
The one wrong answer in 41 measured runs is in the arm with the line (task 4, run lever1-2): it sent the 8 reads in a batch right after the first two calls, finished in 3 requests, and named all eight files as wrong (verdict UNSUPPORTED). The other 7 runs of that task got the two wrong files right. One run is not an effect, but it is the only run of 41 where a request was saved by finishing early and it was wrong; would a bigger sample show that "fewer requests" costs correctness on counting tasks?
refs: __reports__/wave-08/explorer-w08-g/arms_task4_readonly_8.tsv row V-lever1-2

## S-w08-explorer-w08-g-4
The thinking part of the saving (USD 1.31 of the loose upper bound 2.25) rests on five requests (USD 0.79): the largest is a thinking block of 46,900 signature characters (about 15,000 estimated tokens, USD 0.37, author-w06-4 request 5), far above the 6,560 characters of the fit's range. Is a 15,000-token thinking block in a worker's fifth request real, and why does it sit in a request that a read-only call follows? If real, effort control of that one turn is worth more than any batching.
refs: __reports__/wave-08/explorer-w08-g/pairs_think_sensitivity.txt; __reports__/wave-08/explorer-w08-g/pairs_per_worker.tsv row author-w06-4

## S-w08-explorer-w08-g-5
The token test misses numeric dependence: audit sample 24 is `wc -l` and `sed` of the script, then `sed -n 60,248p` of the same script, where 248 is the line count from the first result; no 12-character or path-like token carries it, so the strict rule counted it as independent. How many strict pairs depend on a number in the result (line counts, pids, byte offsets)? The audit found 5 dependent and 9 doubtful of 32 by reading 120 characters of each call, which is too little to tell.
refs: __reports__/wave-08/explorer-w08-g/audit_judgments.tsv (sample 24, 27, 21, 30, 37 are N); `/private/tmp/murmuration-w08/explorer-w08-g/audit_sample.txt` (call heads, not committed)
