| heredoc prose 30 KB, 389 bare `$(` | 30028 | allow 0.05 s | allow 0.02 s | allow 0.05 s | allow 0.03 s |
| heredoc prose 78 KB, 52 bare `$(` | 78034 | allow 0.08 s | allow 0.02 s | allow 0.11 s | allow 0.03 s |
| heredoc prose 200 KB, 800 bare `$(` | 200082 | allow 0.13 s | allow 0.04 s | allow 0.17 s | allow 0.04 s |
| heredoc script body 200 KB | 200011 | allow 0.25 s | allow 0.06 s | allow 0.53 s | allow 0.09 s |
| python3 -c write + 30 KB word | 30017 | allow 6.36 s | allow 0.03 s | allow 6.34 s | allow 0.03 s |
| python3 -c write + 100 KB word | 100017 | cut off >25 |  | cut off >25 |  |
| 30,000 unmatched `$(` | 60005 | allow 0.21 s | allow 0.05 s | allow 0.23 s | allow 0.05 s |
| nested `$(` depth 100 | 306 | allow 0.04 s | allow 0.02 s | allow 0.04 s | allow 0.02 s |
| nested `$(` depth 1000 | 3006 | allow 0.04 s | allow 0.02 s | allow 0.43 s | allow 0.04 s |
| nested `$(` depth 2500 | 7506 | allow 0.05 s | allow 0.02 s | allow 2.42 s | allow 0.10 s |
| nested `$(` depth 3500 | 10506 | allow 0.07 s | allow 0.02 s | deny G? 2.72 s | deny G? 0.09 s |
| 30,000 matched `$(echo a)` | 300005 | allow 0.47 s | allow 0.09 s | allow 0.98 s | allow 0.13 s |
