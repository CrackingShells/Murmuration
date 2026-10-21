## S-w07-explorer-w07-d-1
Rust at 4-12 threads read the same 274 MB with the thread-summed read time doubling (35 ms to 70 ms) while the parse time barely moved. What is the parallel read bottleneck: page-cache copy bandwidth, APFS clone extent sharing (the files are `cp -c` clones), or the M3 Pro's P/E split? I could not separate them. Also the first Rust run on the freshly cloned files read in 0.245 s against 0.035 s later: a cold-cache number I can not reproduce without purging the cache.
refs: __reports__/wave-07/explorer-w07-d/raw/table_rust_item.txt, raw/t_rust_item_inproc.txt, raw/profile.txt

## S-w07-explorer-w07-d-2
`merge_usage` in `scripts/lab_status.py` copies only `USAGE_FIELDS` and `cache_creation` into the message's usage dict, so `message_usd` can never see `speed` or `server_tool_use`: the `FAST_FACTOR` and `WEB_SEARCH_USD` branches look unreachable on the report path. In the 669 files no record has `"speed":"fast"` or a web search, so today no figure is wrong; it is dead code that would silently under-count a fast-mode or web-search session at list price. Not verified by an exact run of a fast-mode record (none exists in the lab's transcripts).
refs: scripts/lab_status.py (message_usd, merge_usage), __instrumenta__/w07d_parsers.py (canonical keeps exactly the same fields)

## S-w07-explorer-w07-d-3
The headless-cell tally (231 serial Bash calls, 2,856 s) rests on a regex over commands (`claude -p`, `*_full.sh`, `w06c*_run*.py`); the per-agent "own wall" column (332,000 s summed) is dominated by gaps of days between resumed turns, so it cannot be used to say what share of an agent's time headless cells take. Active time per agent (what `budget.py` records) would be the right denominator; I did not join it. Wave 4's "critical path is one author's serial cells" is therefore neither confirmed nor refuted here.
refs: __reports__/wave-07/explorer-w07-d/raw/headless_cells.txt, __instrumenta__/w07d_headless_cells.py

## S-w07-explorer-w07-d-4
The warm-cache whole-script run (0.39-0.42 s) is 2x its in-process figure plus Python startup (0.20 + 0.08 = 0.28 s). Where do the other 0.1 s go (import of subprocess/tempfile/glob, interpreter shutdown with a 3 MB JSON object graph, other agents' load)? `cache+nogit` (0.23 s) shows part of it is the git child's wait, but the sum still does not close. Under load 5-7 the process-level spread (min 0.27, max 0.74) is wider than any of the algorithmic differences between Python variants.
refs: __reports__/wave-07/explorer-w07-d/raw/stages.txt, raw/tables_bench.txt
