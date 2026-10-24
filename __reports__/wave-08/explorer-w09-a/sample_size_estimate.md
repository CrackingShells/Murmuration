refusals: 67 (sessions 41); recorded-decision era (>= 2.1.293): 23

### A. false-allow side: local model allows what Anthropic refused (k misses of n refusals)

| n refusals | k misses | point | exact 95% two-sided | Wilson 95% |
|--:|--:|--:|:--|:--|
| 23 | 0 | 0.000 | 0.000-0.148 | -0.000-0.143 |
| 23 | 1 | 0.043 | 0.001-0.219 | 0.008-0.210 |
| 23 | 3 | 0.130 | 0.028-0.336 | 0.045-0.321 |
| 23 | 6 | 0.261 | 0.102-0.484 | 0.125-0.465 |
| 23 | 10 | 0.435 | 0.232-0.655 | 0.256-0.632 |
| 23 | 20 | 0.870 | 0.664-0.972 | 0.679-0.955 |
| 67 | 0 | 0.000 | 0.000-0.054 | 0.000-0.054 |
| 67 | 1 | 0.015 | 0.000-0.080 | 0.003-0.080 |
| 67 | 3 | 0.045 | 0.009-0.125 | 0.015-0.124 |
| 67 | 6 | 0.090 | 0.034-0.185 | 0.042-0.182 |
| 67 | 10 | 0.149 | 0.074-0.257 | 0.083-0.253 |
| 67 | 20 | 0.299 | 0.193-0.423 | 0.202-0.417 |

rule of three, one-sided 95%: k=0 of n=67 gives upper bound 0.045 (exact 0.044)

### B. refusals needed for a target half-width on the miss rate p (n = deff * z^2 p (1-p) / h^2, z = 1.96)

| p | h = 0.10 | h = 0.05 | h = 0.025 |
|--:|--:|--:|--:|
| 0.05 | 19 | 73 | 292 |
| 0.10 | 35 | 139 | 554 |
| 0.20 | 62 | 246 | 984 |
| 0.30 | 81 | 323 | 1291 |

### C. allowed calls needed per estimate of the disagreement rate q among allows (local refuses what Anthropic allowed), n = deff * z^2 q (1-q) / h^2

| q | h | deff 1 | deff 2 | deff 4 |
|--:|--:|--:|--:|--:|
| 0.01 | 0.005 | 1522 | 3043 | 6086 |
| 0.02 | 0.010 | 753 | 1506 | 3012 |
| 0.05 | 0.020 | 457 | 913 | 1825 |
| 0.10 | 0.030 | 385 | 769 | 1537 |
| 0.20 | 0.050 | 246 | 492 | 984 |

### D. what the skew means (population of recorded decisions)

recorded era: 30511 classifier allows, 23 classifier refusals: refusal share 0.0753%
accuracy of a model that allows everything: 99.9247%; its sensitivity: 0
random allowed sample of n needed to see >= 1 more refusal-like item by chance at p=0.00075: n=3976 (95%)
era refusals span 2026-10-13 to 2026-10-23: 23 refusals; observed rate about 2.09 per day in this account
