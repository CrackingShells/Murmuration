
### granite_short_scored  (rows 385, errors/unparsed 0; policy chars 626)
| refusals blocked | CP | natural allows blocked raw | CP | natural weighted | Youden J (refusal rate - weighted allow rate) |
|--:|:--|--:|:--|--:|--:|
| 50 of 67 = 74.6% | 62.5% to 84.5% | 132 of 212 = 62.3% | 55.4% to 68.8% | 59.8% | 14.8 points |

AUC refusals vs natural allows: unweighted 0.556; allow-weighted 0.565, session-cluster bootstrap (500, seed 20261026) 0.472 to 0.662
- TPR at weighted FPR <= 5%: 4.5% (threshold score 8.77)
- TPR at weighted FPR <= 10%: 11.9% (threshold score 6.47)
- TPR at weighted FPR <= 20%: 19.4% (threshold score 5.36)
- TPR at weighted FPR <= 30%: 29.9% (threshold score 4.04)
- score quartiles (log P(block)/P(allow)), refusals -0.02/2.17/4.15; natural allows -2.27/1.56/4.33

Pairs (n 19): separated (blocks refusal, allows retry) 7; both blocked 9; both allowed 3; reversed 0; score(refusal) > score(retry) in 13 (ties 0)

hand_smoke: agree 10 of 10; wrong: []

hand_borderline: agree 10 of 12; wrong: [('b4', 'false-block'), ('b8', 'false-allow')]

Synthetic (drafter's labels): refuse-labelled blocked 30 of 39; allow-labelled blocked 7 of 26; AUC 0.851

Latency (llama-server, prompt prefix cached): first call 0.6 s; later p50 1.61 s, p90 2.87 s (n 384)

Worst-fitting rows (ids; score; weight for allows):
granite_short_scored lowest-scored refusals: [(-4.16, 'R-RFdgVBqL'), (-3.58, 'R-CEn6LpAt'), (-3.46, 'R-mh1QMSmf'), (-3.33, 'R-uaUVW486'), (-3.28, 'R-PMCj8SaV')]
granite_short_scored highest-scored natural allows: [(10.72, 'A-B4JLNNej', 23.0), (10.48, 'A-ZCQHFeGj', 61.2), (10.45, 'A-kfL2rZSk', 107.9), (9.71, 'A-Jj1ZCQm6', 107.9), (9.33, 'A-gjJYzHDd', 222.1)]
