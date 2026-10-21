| run index (0 = first exec of a new binary) | n binaries | median ms | p90 ms | max ms |
|--:|--:|--:|--:|--:|
| 0 | 24 | 329.69 | 369.80 | 389.92 |
| 1 | 24 | 26.92 | 42.61 | 103.41 |
| 2 | 24 | 26.45 | 42.36 | 102.42 |
| 3 | 24 | 26.47 | 45.25 | 102.84 |
| control (known binary) | 24 | 26.44 | 51.36 | 90.63 |

first run minus median of the same binary's later runs, ms: median 294.83, p10 278.40, p90 342.48, n=24; first slower by >3 ms in 24 of 24
