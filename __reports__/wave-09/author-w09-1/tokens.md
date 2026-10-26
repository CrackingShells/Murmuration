## M1 PI request 0, resumed sessions counted once
murmuration-syste ab96c5ed before start 2026-10-19T01:56 version 2.1.299 requests 394 request-0 74457; request ids shared with an earlier session of the same folder: 0
murmuration-wave- c533f1c6 before start 2026-10-20T00:27 version 2.1.299 requests 114 request-0 74632; request ids shared with an earlier session of the same folder: 0
lab-system-optimi 6b0e1f2a before start 2026-10-21T05:29 version 2.1.304 requests 153 request-0 74966; request ids shared with an earlier session of the same folder: 0
blissful-villani- 74fa512e after start 2026-10-21T08:18 version 2.1.304 requests 233 request-0 46738; request ids shared with an earlier session of the same folder: 0
xenodochial-frank f023f552 after start 2026-10-21T15:22 version 2.1.304 requests 201 request-0 47867; request ids shared with an earlier session of the same folder: 0
murmuration-wave- ad75be4f after start 2026-10-23T15:11 version 2.1.308 requests 229 request-0 50223; request ids shared with an earlier session of the same folder: 0
murmuration-wave- 70daedf1 after start 2026-10-24T05:18 version 2.1.308 requests 255 request-0 50223; request ids shared with an earlier session of the same folder: 226 -> RESUME, dropped
independent sessions: before n=3 [74457, 74632, 74966] mean 74685; after n=3 [46738, 47867, 50223] mean 48276; difference 26409 (35.4%); min before 74457 > max after 50223: True
exact one-sided permutation p (all 3 before above all 3 after): 1/C(6,3) = 0.050

## M2 workers' request 0 (start before 2026-10-25; the 4 wave-9 live explorers excluded)
before n=44 median 24303 (min 23472 max 25242); after n=93 median 14464 (min 13322 max 15992); difference 9839 (40.5%), bootstrap 95% interval of the difference of medians [9642, 10012]
sessions in the before group: ['murmuration-system-optimiza']; its latest start 2026-10-19T11:32; first start of the after group 2026-10-20T00:34 (no worker between)
ceiling (difference x own requests x USD 0.10/M): USD 5.19 over 93 later workers

## M6 hand-back length (characters of the SubagentHandback message)
workers with no SubagentHandback call: 0 of 137; with 2 or more: 57
| group | hand-back | n | median | p25 | p75 | max |
|:--|:--|--:|--:|--:|--:|--:|
| all before | first | 125 | 4292 | 3582 | 5384 | 19661 |
| all after | first | 12 | 1457 | 1223 | 1988 | 2454 |
| before, excluding 10-23 (the wave whose own briefs were already treated) | first | 110 | 4452 | 3783 | 5545 | 19661 |
| 10-23 before merge | first | 15 | 2321 | 1809 | 4408 | 5873 |
  -> first: bootstrap 95% interval of before-minus-after median [2361, 3321]
| all before | last | 125 | 3562 | 1877 | 4413 | 19661 |
| all after | last | 12 | 986 | 763 | 1988 | 2454 |
| before, excluding 10-23 (the wave whose own briefs were already treated) | last | 110 | 3722 | 2021 | 4553 | 19661 |
| 10-23 before merge | last | 15 | 1859 | 1128 | 3514 | 5873 |
  -> last: bootstrap 95% interval of before-minus-after median [1649, 3019]
explorer before first n=33 median 4408
explorer after first n=5 median 1988
author before first n=35 median 5548
author after first n=3 median 1565
reproducer before first n=57 median 3959
reproducer after first n=4 median 1004
after the merge (first hand-back chars): [('explorer-w08-i', 2311), ('explorer-w08-j', 2454), ('author-w08-9', 1732), ('author-w08-10', 1565), ('reproducer-w08-5', 1092), ('reproducer-w08-9', 1350), ('reproducer-w08-10', 917), ('author-w08-14', 1223), ('explorer-w08-k', 1347), ('reproducer-w08-14', 856), ('explorer-w09-a', 1988), ('explorer-w09-b', 1741)]
