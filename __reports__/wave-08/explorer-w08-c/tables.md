### (a) gamma-Poisson event model of P(1h saves USD > X) per life

| type | lives | requests | events (300-3600 s) | events per 100 requests (90% interval) | mean premium per life, USD | mean saving per event, USD | P(net>0) model | P(net>0.10) | P(net>0) observed lives | mean net per life, model | 5-95% |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:--|
| author | 14 | 1138 | 6 | 0.53 (0.26-1.00) | 0.32 | 0.70 | 0.30 | 0.29 | 5/14 | +0.02 | -0.65 to +1.09 |
| reproducer | 14 | 571 | 3 | 0.53 (0.19-1.25) | 0.16 | 0.31 | 0.19 | 0.13 | 3/14 | -0.08 | -0.25 to +0.32 |
| explorer | 9 | 424 | 3 | 0.71 (0.25-1.65) | 0.22 | 0.26 | 0.22 | 0.11 | 2/9 | -0.12 | -0.30 to +0.23 |
| PI | 3 | 443 | 31 | 7.00 (5.16-9.30) | 1.84 | 1.59 | 0.99 | 0.99 | 2/3 | +14.79 | +2.56 to +31.83 |

### (b) PI context jumps above 8,000 tokens after request 1 (waves 4-6), the reads the PI actually carried

| wave | request | jump tokens | later requests M | calls before |
|:--|--:|--:|--:|:--|
| w4 | 3 | 13348 | 110 | Bash:cat,Bash:cat,Bash:cat |
| w4 | 5 | 8562 | 108 | Bash:cd |
| w4 | 22 | 9904 | 91 | Bash:cd |
| w4 | 27 | 8771 | 86 | Agent,Agent,Agent,Agent |
| w4 | 35 | 12872 | 78 |  |
| w4 | 74 | 11204 | 39 | Bash:cd |
| w5 | 6 | 9913 | 146 | Bash:W4=/Users/hacker/Doc |
| w5 | 114 | 10900 | 38 | Bash:python3 |
| w6 | 181 | 14561 | 41 | mcp__ccd_turn__update_plan,Write |
| w6 | 190 | 8301 | 32 | ToolSearch |

PI sessions: w4 114 requests, w5 153 requests, w6 223 requests; no compaction drop in any (context falls under 0.6 of the previous: none).

### Break-even document size D* (tokens) at which delegating (q = 0) equals reading, by later requests M; worker overhead = median / 10th / 90th percentile of reproducer+explorer life cost (USD), n_w = median worker requests

worker lives n=23: cost5 USD median 0.62, p10 0.35, p90 1.23; requests median 39

| M | D* at overhead p10 | D* at median | D* at p90 |
|--:|--:|--:|--:|
| 10 | 106,000 | 181,389 | 352,000 |
| 30 | 51,263 | 86,974 | 167,789 |
| 100 | 19,333 | 31,898 | 60,333 |
| 200 | 11,000 | 17,524 | 32,288 |
| 400 | 6,588 | 9,914 | 17,441 |

### Monte Carlo: P(delegation cheaper than reading), M drawn from the PI's remaining requests at a random point of a session (n=487 positions), worker lives resampled; q = chance the summary fails, then the PI reads phi=0.5 of the document too

| D tokens | q | P(delegate cheaper) | mean saving USD (read - delegate) | 5-95% | mean read cost USD | CVaR90 of the extra cost of delegating, USD |
|--:|--:|--:|--:|:--|--:|--:|
| 10,000 | 0.0 | 0.01 | -0.62 | -1.31 to -0.12 | 0.25 | +1.63 |
| 10,000 | 0.2 | 0.00 | -0.64 | -1.32 to -0.13 | 0.25 | +1.62 |
| 10,000 | 0.4 | 0.00 | -0.67 | -1.34 to -0.15 | 0.25 | +1.68 |
| 25,000 | 0.0 | 0.27 | -0.34 | -1.29 to +0.41 | 0.64 | +1.49 |
| 25,000 | 0.2 | 0.22 | -0.40 | -1.31 to +0.37 | 0.64 | +1.53 |
| 25,000 | 0.4 | 0.16 | -0.47 | -1.38 to +0.32 | 0.64 | +1.62 |
| 50,000 | 0.0 | 0.57 | +0.12 | -1.13 to +1.37 | 1.27 | +1.30 |
| 50,000 | 0.2 | 0.49 | -0.02 | -1.23 to +1.24 | 1.26 | +1.41 |
| 50,000 | 0.4 | 0.41 | -0.13 | -1.31 to +1.16 | 1.28 | +1.50 |
| 100,000 | 0.0 | 0.79 | +1.06 | -0.86 to +3.35 | 2.55 | +1.00 |
| 100,000 | 0.2 | 0.71 | +0.79 | -1.07 to +3.18 | 2.53 | +1.21 |
| 100,000 | 0.4 | 0.63 | +0.53 | -1.29 to +2.90 | 2.52 | +1.46 |
| 200,000 | 0.0 | 0.91 | +2.97 | -0.42 to +7.39 | 5.15 | +0.60 |
| 200,000 | 0.2 | 0.85 | +2.39 | -0.96 to +7.09 | 5.06 | +1.13 |
| 200,000 | 0.4 | 0.79 | +1.92 | -1.21 to +6.67 | 5.14 | +1.39 |
