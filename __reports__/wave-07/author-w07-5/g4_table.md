| pair | order | A median ms | B median ms | A-B ms | A calls | B calls | A max | B max | load before A/B |
|--:|:--|--:|--:|--:|--:|--:|--:|--:|:--|
| 0 | A,B | 66 | 47 | 20 | 8 | 8 | 76 | 49 | 1.84 / 2.00 |
| 1 | B,A | 63 | 40 | 23 | 8 | 8 | 79 | 50 | 2.14 / 2.07 |
| 2 | A,B | 56 | 44 | 12 | 8 | 8 | 76 | 51 | 2.76 / 2.73 |
| 3 | B,A | 69 | 37 | 32 | 8 | 8 | 71 | 52 | 2.78 / 2.57 |
| 4 | A,B | 68 | 44 | 24 | 8 | 8 | 79 | 61 | 2.94 / 2.89 |
| 5 | B,A | 64 | 36 | 28 | 8 | 8 | 73 | 52 | 3.22 / 2.85 |
| 6 | A,B | 53 | 42 | 11 | 8 | 8 | 75 | 52 | 2.96 / 2.89 |
| 7 | B,A | 69 | 42 | 28 | 8 | 8 | 82 | 48 | 2.94 / 2.65 |
| 8 | A,B | 65 | 37 | 28 | 8 | 8 | 77 | 49 | 2.69 / 2.67 |
| 9 | B,A | 69 | 48 | 22 | 8 | 8 | 80 | 52 | 2.57 / 2.50 |
| 10 | A,B | 58 | 40 | 17 | 8 | 8 | 77 | 54 | 2.30 / 2.63 |
| 11 | B,A | 56 | 46 | 11 | 8 | 8 | 72 | 57 | 2.53 / 2.70 |
| 12 | A,B | 72 | 47 | 24 | 8 | 8 | 77 | 53 | 3.94 / 3.67 |
| 13 | B,A | 68 | 28 | 40 | 8 | 8 | 78 | 54 | 2.92 / 3.11 |
| 14 | A,B | 69 | 42 | 26 | 8 | 8 | 88 | 53 | 3.33 / 2.89 |
| 15 | B,A | 70 | 47 | 24 | 8 | 8 | 75 | 53 | 2.85 / 2.60 |
| 16 | A,B | 73 | 46 | 27 | 8 | 8 | 84 | 53 | 3.18 / 2.94 |
| 17 | B,A | 68 | 46 | 22 | 8 | 8 | 74 | 53 | 2.38 / 2.62 |
| 18 | A,B | 70 | 46 | 24 | 8 | 8 | 75 | 53 | 2.58 / 2.25 |

per-session median of all guard calls: pairs 19, B lower in 19, equal in 0; median saving (A-B) 23.5 ms [p10 11.8, p90 28.8, min 11.0, max 40.5]

per-session median without the first call: pairs 19, B lower in 19, equal in 0; median saving (A-B) 25.0 ms [p10 15.8, p90 31.4, min 9.0, max 37.0]

per-session mean of all guard calls: pairs 19, B lower in 19, equal in 0; median saving (A-B) 23.4 ms [p10 14.4, p90 26.9, min 10.4, max 32.4]

all calls pooled: A n 152 median 67 ms (p10 38, p90 75); B n 152 median 42 ms (p10 19, p90 52)
sessions: wall A median 19.4 s, B 19.5 s; load1 before, median 2.72; all statuses zero: True; cost USD total 0.437 over 38 sessions
