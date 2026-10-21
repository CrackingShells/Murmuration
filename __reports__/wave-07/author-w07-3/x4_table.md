### guard PreToolUse: per-pair medians of the platform-recorded duration, ms

| pair | load avg start / end | A n | A median | B n | B median | A minus B | B lower |
|--:|:--|--:|--:|--:|--:|--:|:--|
| 1 | 5.29 / 3.94 | 7 | 101.0 | 6 | 38.0 | 63.0 | yes |
| 2 | 3.94 / 3.93 | 7 | 98.0 | 8 | 50.5 | 47.5 | yes |
| 3 | 3.93 / 3.75 | 8 | 147.0 | 7 | 34.0 | 113.0 | yes |
| 4 | 3.75 / 4.13 | 8 | 125.5 | 6 | 40.5 | 85.0 | yes |
| 5 | 4.13 / 3.86 | 6 | 120.5 | 6 | 39.5 | 81.0 | yes |
| 6 | 3.86 / 3.81 | 7 | 261.0 | 8 | 42.0 | 219.0 | yes |
| 7 | 3.81 / 3.45 | 7 | 157.0 | 8 | 52.5 | 104.5 | yes |
| 8 | 3.45 / 2.97 | 8 | 112.5 | 8 | 61.0 | 51.5 | yes |
| 9 | 2.97 / 3.74 | 7 | 102.0 | 9 | 34.0 | 68.0 | yes |
| 10 | 3.74 / 3.65 | 6 | 113.5 | 6 | 41.0 | 72.5 | yes |

B lower in 10 of 10 pairs; median saving 76.8 ms; min 47.5, max 219.0, quartiles 60.1 / 106.6; pooled over all starts: A 123.0 ms (n = 71), B 42.0 ms (n = 72)

### budget PostToolUse: per-pair medians of the platform-recorded duration, ms

| pair | load avg start / end | A n | A median | B n | B median | A minus B | B lower |
|--:|:--|--:|--:|--:|--:|--:|:--|
| 1 | 5.29 / 3.94 | 11 | 65.0 | 10 | 40.5 | 24.5 | yes |
| 2 | 3.94 / 3.93 | 9 | 96.0 | 11 | 43.0 | 53.0 | yes |
| 3 | 3.93 / 3.75 | 11 | 126.0 | 11 | 59.0 | 67.0 | yes |
| 4 | 3.75 / 4.13 | 11 | 142.0 | 10 | 38.0 | 104.0 | yes |
| 5 | 4.13 / 3.86 | 9 | 121.0 | 10 | 32.5 | 88.5 | yes |
| 6 | 3.86 / 3.81 | 11 | 127.0 | 11 | 49.0 | 78.0 | yes |
| 7 | 3.81 / 3.45 | 11 | 147.0 | 11 | 43.0 | 104.0 | yes |
| 8 | 3.45 / 2.97 | 11 | 113.0 | 11 | 38.0 | 75.0 | yes |
| 9 | 2.97 / 3.74 | 11 | 92.0 | 11 | 35.0 | 57.0 | yes |
| 10 | 3.74 / 3.65 | 9 | 74.0 | 10 | 36.0 | 38.0 | yes |

B lower in 10 of 10 pairs; median saving 71.0 ms; min 24.5, max 104.0, quartiles 49.2 / 92.4; pooled over all starts: A 104.5 ms (n = 104), B 41.0 ms (n = 106)

### budget PostToolUse (worker): per-pair medians of the platform-recorded duration, ms

| pair | load avg start / end | A n | A median | B n | B median | A minus B | B lower |
|--:|:--|--:|--:|--:|--:|--:|:--|
| 1 | 5.29 / 3.94 | 10 | 70.0 | 9 | 38.0 | 32.0 | yes |
| 2 | 3.94 / 3.93 | 8 | 98.0 | 10 | 43.5 | 54.5 | yes |
| 3 | 3.93 / 3.75 | 10 | 127.0 | 10 | 60.0 | 67.0 | yes |
| 4 | 3.75 / 4.13 | 10 | 127.5 | 9 | 36.0 | 91.5 | yes |
| 5 | 4.13 / 3.86 | 8 | 117.0 | 9 | 32.0 | 85.0 | yes |
| 6 | 3.86 / 3.81 | 10 | 115.0 | 10 | 48.5 | 66.5 | yes |
| 7 | 3.81 / 3.45 | 10 | 147.5 | 10 | 41.0 | 106.5 | yes |
| 8 | 3.45 / 2.97 | 10 | 98.0 | 10 | 37.5 | 60.5 | yes |
| 9 | 2.97 / 3.74 | 10 | 92.0 | 10 | 34.0 | 58.0 | yes |
| 10 | 3.74 / 3.65 | 8 | 71.5 | 9 | 38.0 | 33.5 | yes |

B lower in 10 of 10 pairs; median saving 63.5 ms; min 32.0, max 106.5, quartiles 49.2 / 86.6; pooled over all starts: A 104.5 ms (n = 94), B 40.5 ms (n = 96)

### every murmuration hook kind: pooled median ms over all pairs, and the number of pairs in which B's per-pair median is lower

| hook kind | A pooled median (n) | B pooled median (n) | pairs with both arms | B lower in |
|:--|:--|:--|--:|--:|
| budget PostToolBatch | 81.0 (90) | 36.0 (93) | 10 | 10 |
| budget PostToolUse | 104.5 (104) | 41.0 (106) | 10 | 10 |
| budget PostToolUse (worker) | 104.5 (94) | 40.5 (96) | 10 | 10 |
| budget PostToolUse:Agent | 99.0 (10) | 59.5 (10) | 10 | 9 |
| budget PreToolUse:Agent | 123.5 (10) | 40.0 (10) | 10 | 9 |
| budget SubagentStart | 195.5 (10) | 118.5 (10) | 10 | 9 |
| budget SubagentStop | 120.0 (10) | 96.0 (10) | 10 | 8 |
| guard PreToolUse | 123.0 (71) | 42.0 (72) | 10 | 10 |
| handback PostToolUse | 172.5 (10) | 78.0 (10) | 10 | 10 |
| handback PreToolUse | 115.5 (10) | 48.5 (10) | 10 | 10 |
| handback SubagentStop | 98.5 (10) | 64.0 (10) | 10 | 9 |
| user_words UserPromptSubmit | 238.5 (20) | 113.5 (20) | 10 | 9 |

### sum of the platform-recorded durations of every murmuration hook start in a session, ms (hooks run concurrently with siblings, so this is hook-time, not wall time)

| pair | A starts, sum ms | B starts, sum ms | A minus B |
|--:|--:|--:|--:|
| 1 | 4395 (37 starts) | 1868 (31 starts) | 2527 |
| 2 | 3607 (34 starts) | 2407 (38 starts) | 1200 |
| 3 | 4966 (35 starts) | 1930 (35 starts) | 3036 |
| 4 | 6048 (39 starts) | 1846 (35 starts) | 4202 |
| 5 | 5343 (33 starts) | 2092 (35 starts) | 3251 |
| 6 | 6100 (37 starts) | 2948 (39 starts) | 3152 |
| 7 | 5200 (33 starts) | 2194 (36 starts) | 3006 |
| 8 | 5042 (38 starts) | 1790 (39 starts) | 3252 |
| 9 | 4077 (36 starts) | 2051 (39 starts) | 2026 |
| 10 | 3637 (33 starts) | 1777 (34 starts) | 1860 |

median per-session difference 3021 ms; min 1200, max 4202
