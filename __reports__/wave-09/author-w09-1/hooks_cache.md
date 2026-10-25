## M3 hook durations, each record once by uuid (0 duplicate records removed)
| event | form | n | median ms | p90 ms | first to last (UTC) |
|:--|:--|--:|--:|--:|:--|
| PostToolBatch | budget.py, string form | 44 | 105 | 316 | 2026-10-20T01:04 to 2026-10-21T13:04 |
| PostToolBatch | lean, string form (run_hook.py quoted) | 30 | 103 | 163 | 2026-10-21T15:34 to 2026-10-21T17:27 |
| PostToolBatch | exec form (run_hook.py) | 35 | 51 | 70 | 2026-10-23T15:28 to 2026-10-23T20:03 |
| PostToolBatch | binary | 1 | 24 | 24 | 2026-10-24T05:45 to 2026-10-24T05:45 |
| SubagentStart | budget.py, string form | 47 | 467 | 1010 | 2026-10-20T00:34 to 2026-10-21T13:13 |
| SubagentStart | lean, string form (run_hook.py quoted) | 20 | 247 | 847 | 2026-10-21T15:27 to 2026-10-21T17:18 |
| SubagentStart | exec form (run_hook.py) | 25 | 166 | 306 | 2026-10-23T15:16 to 2026-10-23T19:32 |
| SubagentStart | binary | 2 | 226 | 197 | 2026-10-24T05:22 to 2026-10-24T05:22 |
PostToolBatch budget.py, -> lean, stri: median 105 -> 103, difference 1 ms, bootstrap 95% interval [-28, 38]
PostToolBatch lean, stri -> exec form : median 103 -> 51, difference 52 ms, bootstrap 95% interval [29, 83]
PostToolBatch budget.py, -> exec form : median 105 -> 51, difference 54 ms, bootstrap 95% interval [39, 84]
SubagentStart budget.py, -> lean, stri: median 467 -> 247, difference 220 ms, bootstrap 95% interval [-35, 360]
SubagentStart lean, stri -> exec form : median 247 -> 166, difference 81 ms, bootstrap 95% interval [-3, 321]
SubagentStart budget.py, -> exec form : median 467 -> 166, difference 301 ms, bootstrap 95% interval [169, 441]

## M4 pauses over 300 s per author (gap between the last record of one request and the next request)
a before w05-c1: authors 20, pauses 32, per author 1.60, authors with at least one pause 16, max pauses by one author 6
   top: [('author-w04-2', 6, 9.092350002129873, 'murmuration-wave-'), ('author-w02-3', 5, 71.61496666669845, 'murmuration-syste'), ('author-w03-1', 4, 14.574399999777476, 'murmuration-syste')]
b w05-c1..w07-c7: authors 11, pauses 9, per author 0.82, authors with at least one pause 8, max pauses by one author 2
   top: [('author-w06-5', 2, 11.207333334287007, 'blissful-villani-'), ('author-w06-6', 1, 21.11851666768392, 'blissful-villani-'), ('author-w06-3', 1, 69.80038333336512, 'blissful-villani-')]
c after w07-c7: authors 7, pauses 6, per author 0.86, authors with at least one pause 6, max pauses by one author 1
   top: [('author-w08-3', 1, 6.437233332792918, 'murmuration-wave-'), ('author-w08-10', 1, 22.29074999888738, 'murmuration-wave-'), ('author-w08-1', 1, 8.13903333346049, 'murmuration-wave-')]
pauses per author a - b: 0.78, one-sided permutation p 0.095; b - c: -0.04, p 0.730; a - c: 0.74, p 0.191
era a without its top author: 1.37 pauses per author (n=19) vs b 0.82; permutation p 0.154
