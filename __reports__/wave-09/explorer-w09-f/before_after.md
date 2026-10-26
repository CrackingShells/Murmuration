## M1: the PI's request 0 before and after the denylist line (w05-c7, merged fed7a08 at 2026-10-21T08:08Z)
| session | start (UTC) | version | requests | request-0 tokens | PI main-thread USD (list) | rel. to merge |
|:--|:--|:--|--:|--:|--:|:--|
| murmuration-system-opt ab96c5ed | 2026-10-19T01:56 | 2.1.299 | 394 | 74457 | 63.23 | before |
| murmuration-wave-4-341 c533f1c6 | 2026-10-20T00:27 | 2.1.299 | 114 | 74632 | 10.50 | before |
| lab-system-optimizatio 6b0e1f2a | 2026-10-21T05:29 | 2.1.304 | 153 | 74966 | 18.08 | before |
| blissful-villani-34edd 74fa512e | 2026-10-21T08:18 | 2.1.304 | 233 | 46738 | 23.08 | after |
| xenodochial-franklin-b f023f552 | 2026-10-21T15:22 | 2.1.304 | 201 | 47867 | 27.14 | after |
| murmuration-wave-8-928 ad75be4f | 2026-10-23T15:11 | 2.1.308 | 229 | 50223 | 26.02 | after |
| murmuration-wave-8-928 70daedf1 | 2026-10-24T05:18 | 2.1.308 | 255 | 50223 | 29.82 | after |
| murmuration-research-w a75de3b4 | 2026-10-25T14:23 | 2.1.308 | 41 | 51100 | 3.01 | after |

mean request 0 before 74685 (n=3), after 49230 (n=5), difference 25455 (34.1%)
  after-session: 233 requests x 27947 tokens x USD 0.20/M cache read = USD 1.30 ceiling of saving (+ one write at 8/M: 0.22) vs session USD 23.08 = 5.6%
  after-session: 201 requests x 26818 tokens x USD 0.20/M cache read = USD 1.08 ceiling of saving (+ one write at 8/M: 0.21) vs session USD 27.14 = 4.0%
  after-session: 229 requests x 24462 tokens x USD 0.20/M cache read = USD 1.12 ceiling of saving (+ one write at 8/M: 0.20) vs session USD 26.02 = 4.3%
  after-session: 255 requests x 24462 tokens x USD 0.20/M cache read = USD 1.25 ceiling of saving (+ one write at 8/M: 0.20) vs session USD 29.82 = 4.2%
  after-session: 41 requests x 23585 tokens x USD 0.20/M cache read = USD 0.19 ceiling of saving (+ one write at 8/M: 0.19) vs session USD 3.01 = 6.4%

## M2: workers' request 0 by type and day (w02-c4, merged 84ff038 at 2026-10-19T14:53Z)
| type | day (UTC) | n | median request 0 | min | max | median requests | max start |
|:--|:--|--:|--:|--:|--:|--:|:--|
| author | 2026-10-19 | 12 | 24431 | 24105 | 25109 | 65 | 11:06 |
| author | 2026-10-20 | 5 | 14170 | 13730 | 14358 | 107 | 00:35 |
| author | 2026-10-21 | 14 | 14746 | 14042 | 15401 | 68 | 16:00 |
| author | 2026-10-23 | 7 | 15153 | 14980 | 15737 | 83 | 18:58 |
| explorer | 2026-10-19 | 9 | 23596 | 23472 | 24175 | 62 | 06:10 |
| explorer | 2026-10-21 | 16 | 14537 | 13680 | 15409 | 48 | 15:43 |
| explorer | 2026-10-23 | 11 | 14646 | 14516 | 15274 | 57 | 18:58 |
| explorer | 2026-10-24 | 2 | 15909 | 15827 | 15992 | 40 | 05:22 |
| explorer | 2026-10-25 | 4 | 16181 | 15337 | 16491 | 20 | 14:29 |
| reproducer | 2026-10-19 | 23 | 24309 | 23859 | 25242 | 29 | 11:32 |
| reproducer | 2026-10-20 | 10 | 13619 | 13322 | 14020 | 30 | 01:38 |
| reproducer | 2026-10-21 | 21 | 14163 | 13560 | 14644 | 34 | 17:18 |
| reproducer | 2026-10-23 | 7 | 14540 | 14249 | 14600 | 38 | 19:32 |

before the merge n=44 median 24303; after n=97 median 14480; difference 9823 (40.4%)
ceiling of saving over the 97 later workers: sum of (difference x requests) x USD 0.10/M (Sonnet cache read) = USD 5.26

## M3: hand-back length (characters of the SubagentHandback message) by start time (w08-c6, merged 16b05a8 at 2026-10-23T16:30Z)
| period | n | median chars | p25 | p75 | max |
|:--|--:|--:|--:|--:|--:|
| explorer before | 33 | 4265 | 3514 | 5596 | 19661 |
| explorer after | 5 | 1988 | 1741 | 2311 | 2454 |
| author before | 35 | 1645 | 1332 | 2915 | 6490 |
| author after | 3 | 861 | 556 | 970 | 970 |
| reproducer before | 57 | 3670 | 2690 | 4233 | 5545 |
| reproducer after | 4 | 704 | 645 | 1003 | 1003 |
| all before | 125 | 3562 | 1877 | 4413 | 19661 |
| all after | 12 | 986 | 763 | 1988 | 2454 |

after the merge, one row per worker (name, start, chars):
   explorer-w08-i 2026-10-23T16:31 2311
   explorer-w08-j 2026-10-23T16:31 2454
   author-w08-9 2026-10-23T16:49 970
   author-w08-10 2026-10-23T16:55 861
   reproducer-w08-5 2026-10-23T17:01 763
   reproducer-w08-9 2026-10-23T17:02 645
   reproducer-w08-10 2026-10-23T17:44 1003
   author-w08-14 2026-10-23T18:58 556
   explorer-w08-k 2026-10-23T18:58 1347
   reproducer-w08-14 2026-10-23T19:32 411
   explorer-w09-a 2026-10-24T05:22 1988
   explorer-w09-b 2026-10-24T05:22 1741
   explorer-w09-c 2026-10-25T14:29 0
   explorer-w09-d 2026-10-25T14:29 0
   explorer-w09-e 2026-10-25T14:29 0
   explorer-w09-f 2026-10-25T14:29 0

by wave day before the merge (median chars, n):
   2026-10-19 3899 44
   2026-10-20 2905 15
   2026-10-21 3866 51
   2026-10-23 1859 15
