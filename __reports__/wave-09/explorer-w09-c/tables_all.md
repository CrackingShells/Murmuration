| judge | arm | calls (unparsed/error) | refusals missed (judge allow) | 95% CP | allows falsely refused, raw | reweighted false-refusal rate [cluster-bootstrap 95%] | stratum coverage |
|:--|:--|--:|--:|:--|--:|:--|--:|
| granite-guardian-4.1-8b | short | 462 (0) | 17 of 67 | 15.5% to 37.5% | 172 of 311 | 48.6% [41.3% to 55.6%] | 100.0% |
| granite-guardian-4.1-8b | full | 148 (0) | 3 of 65 | 1.0% to 12.9% | 0 of 0 | nan% [nan% to nan%] | 0.0% |
| gpt-oss-safeguard-20b | short | 196 (0) | 59 of 67 | 77.8% to 94.7% | 3 of 45 | 2.5% [0.0% to 3.4%] | 93.9% |
| gpt-oss-safeguard-20b | full | 38 (0) | 26 of 28 | 76.5% to 99.1% | 0 of 0 | nan% [nan% to nan%] | 0.0% |

| judge | arm | era refusals missed | natural allows refused (raw; weighted) | arena (raw; weighted) | risky-flag stratum | plain stratum | pairs scored | separated (block, allow) | both blocked | both allowed | reversed |
|:--|:--|--:|:--|:--|:--|:--|--:|--:|--:|--:|--:|
| granite-guardian-4.1-8b | short | 4 of 23 | 132 of 212; 59.8% | 40 of 99; 29.8% | 83 of 96; 87.5% | 89 of 215; 41.5% | 19 | 7 | 9 | 3 | 0 |
| granite-guardian-4.1-8b | full | 1 of 22 | 0 of 0; - | 0 of 0; - | 0 of 0; - | 0 of 0; - | 17 | 0 | 16 | 0 | 1 |
| gpt-oss-safeguard-20b | short | 20 of 23 | 2 of 28; 3.9% | 1 of 17; 0.0% | 2 of 11; 3.1% | 1 of 34; 2.4% | 19 | 3 | 0 | 16 | 0 |
| gpt-oss-safeguard-20b | full | 10 of 10 | 0 of 0; - | 0 of 0; - | 0 of 0; - | 0 of 0; - | 5 | 0 | 0 | 5 | 0 |

| judge | arm | synthetic refuse-labelled missed | synthetic allow-labelled refused | first call s | steady p50 ms | steady p90 ms | steady n | median prompt tokens | cold load s |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| granite-guardian-4.1-8b | short | 9 of 39 | 7 of 26 | 6.2 | 1712 | 2880 | 395 | 370 | None |
| granite-guardian-4.1-8b | full | 1 of 39 | 16 of 26 | 11.8 | 2729 | 5905 | 125 | 18412 | None |
| gpt-oss-safeguard-20b | short | 15 of 39 | 1 of 26 | 3.7 | 4137 | 8240 | 195 | 318 | 6.03 |
| gpt-oss-safeguard-20b | full | 0 of 0 | 0 of 0 | 50.6 | 15187 | 27059 | 37 | 18426 | None |
