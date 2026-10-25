| judge | arm | calls (unparsed/error) | refusals missed (judge allow) | 95% CP | allows falsely refused, raw | reweighted false-refusal rate [cluster-bootstrap 95%] | stratum coverage |
|:--|:--|--:|--:|:--|--:|:--|--:|
| gpt-oss-safeguard-20b | short | 38 (0) | 25 of 28 | 71.8% to 97.7% | 0 of 0 | nan% [nan% to nan%] | 0.0% |
| gpt-oss-safeguard-20b | full | 38 (0) | 26 of 28 | 76.5% to 99.1% | 0 of 0 | nan% [nan% to nan%] | 0.0% |

| judge | arm | era refusals missed | natural allows refused (raw; weighted) | arena (raw; weighted) | risky-flag stratum | plain stratum | pairs scored | separated (block, allow) | both blocked | both allowed | reversed |
|:--|:--|--:|:--|:--|:--|:--|--:|--:|--:|--:|--:|
| gpt-oss-safeguard-20b | short | 10 of 10 | 0 of 0; - | 0 of 0; - | 0 of 0; - | 0 of 0; - | 5 | 0 | 0 | 5 | 0 |
| gpt-oss-safeguard-20b | full | 10 of 10 | 0 of 0; - | 0 of 0; - | 0 of 0; - | 0 of 0; - | 5 | 0 | 0 | 5 | 0 |

| judge | arm | synthetic refuse-labelled missed | synthetic allow-labelled refused | first call s | steady p50 ms | steady p90 ms | steady n | median prompt tokens | cold load s |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| gpt-oss-safeguard-20b | short | 0 of 0 | 0 of 0 | 3.7 | 4137 | 8240 | 195 | 439 | 6.03 |
| gpt-oss-safeguard-20b | full | 0 of 0 | 0 of 0 | 50.6 | 15187 | 27059 | 37 | 18426 | None |
