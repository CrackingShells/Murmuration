## audit: stored verdict vs verdict re-parsed from raw; missing rows
- granite-guardian-4.1-8b short: rows 462, meta lines 2, stored != re-parsed 0, unparsed 0, label/group mismatch vs cases 0, duplicate cids 0, not run by group {}
- granite-guardian-4.1-8b full: rows 148, meta lines 2, stored != re-parsed 0, unparsed 0, label/group mismatch vs cases 0, duplicate cids 0, not run by group {'refusal': 2, 'pair_allow': 1, 'allow': 311}
- gpt-oss-safeguard-20b short: rows 196, meta lines 1, stored != re-parsed 0, unparsed 0, label/group mismatch vs cases 0, duplicate cids 0, not run by group {'allow': 266}
- gpt-oss-safeguard-20b full: rows 38, meta lines 1, stored != re-parsed 0, unparsed 0, label/group mismatch vs cases 0, duplicate cids 0, not run by group {'refusal': 39, 'pair_allow': 9, 'synthetic': 65, 'allow': 311}

## refusal side: judge blocks what auto mode refused (agreement = blocked / n)
| judge | arm | blocked / refusals | agreement | 95% CP | session-cluster bootstrap 95% | recorded era (23) | before era (44) | sessions |
|:--|:--|--:|--:|:--|:--|--:|--:|--:|
| granite-guardian-4.1-8b | short | 50 of 67 | 74.6% | 62.5% to 84.5% | 62.3% to 85.7% | 19 of 23 | 31 of 44 | 41 |
| granite-guardian-4.1-8b | full | 62 of 65 | 95.4% | 87.1% to 99.0% | 87.0% to 100.0% | 21 of 22 | 41 of 43 | 41 |
| gpt-oss-safeguard-20b | short | 8 of 67 | 11.9% | 5.3% to 22.2% | 5.0% to 19.7% | 3 of 23 | 5 of 44 | 41 |
| gpt-oss-safeguard-20b | full | 2 of 28 | 7.1% | 0.9% to 23.5% | 0.0% to 16.7% | 0 of 10 | 2 of 18 | 21 |

## allow side: judge allows what auto mode allowed (agreement = 1 - blocked share)
| judge | arm | blocked / allows (raw) | raw CP on blocked | post-stratified blocked share, all | [cluster bootstrap] | natural only (user's own sessions) | [bootstrap] | arena only (lab probe runs) | strata covered of 53 |
|:--|:--|--:|:--|:--|:--|:--|:--|:--|--:|
| granite-guardian-4.1-8b | short | 172 of 311 | 49.6% to 60.9% | 48.6% | 41.1% to 55.8% | 59.8% (132 of 212) | 50.6% to 66.5% | 29.8% (40 of 99) | 53 |
| granite-guardian-4.1-8b | full | not run | | | | | | | 0 |
| gpt-oss-safeguard-20b | short | 3 of 45 | 1.4% to 18.3% | 2.5% | 0.0% to 3.3% | 3.9% (2 of 28) | 0.0% to 6.0% | 0.0% (1 of 17) | 28 |
| gpt-oss-safeguard-20b | full | not run | | | | | | | 0 |

## allow-side sample composition: safeguard short 45 vs the 311, and the population N
- 311 (Granite short): natural 212, arena 99, risky 96, strata 53, sessions 130
- 45 (safeguard short): natural 28, arena 17, risky 11, strata 28, sessions 35
- population: sum N_h 30663, natural 19243, arena 11420; per-stratum m_h check (cases per stratum == m_h): True

## rewrite pairs (refusal -> allowed retry); block member = verdict on the refusal row
| judge | arm | pairs scored | separated (block, allow) | both blocked | both allowed | reversed | refusal member blocked | retry member blocked |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| granite-guardian-4.1-8b | short | 19 | 7 | 9 | 3 | 0 | 16 | 9 |
| granite-guardian-4.1-8b | full | 17 | 0 | 16 | 0 | 1 | 16 | 17 |
| gpt-oss-safeguard-20b | short | 19 | 3 | 0 | 16 | 0 | 3 | 0 |
| gpt-oss-safeguard-20b | full | 5 | 0 | 0 | 5 | 0 | 0 | 0 |

## pairs: are all 19 refusal members among the 67 refusal rows; sessions
- all ref_id in refusals: True ; retry rows are classifier allows picked after a refusal (not random)

## latency (ms) on unique cases; segments = runs between meta lines; steady = last segment without its first call
| judge | arm | rows | segments (rows) | steady n | p50 | p90 | first-call of file | p50 by thirds of the steady segment | p50 refusal-group | p50 / p90 allow-group (n) | median completion tokens |
|:--|:--|--:|:--|--:|--:|--:|--:|:--|--:|:--|--:|
| granite-guardian-4.1-8b | short | 462 | [66, 396] | 395 | 1712 | 2880 | 6224 | 1481, 1862, 1767 | 1912 | 1844 / 2940 (267) | 12 |
| granite-guardian-4.1-8b | full | 148 | [22, 126] | 125 | 2729 | 5905 | 11770 | 2705, 2746, 3001 | 4303 | - | 12 |
| gpt-oss-safeguard-20b | short | 196 | [196] | 195 | 4137 | 8240 | 3682 | 4395, 4300, 3869 | 5251 | 3548 / 7080 (45) | 146 |
| gpt-oss-safeguard-20b | full | 38 | [38] | 37 | 15187 | 27059 | 50626 | 16773, 13834, 15837 | 15668 | - | 499 |
