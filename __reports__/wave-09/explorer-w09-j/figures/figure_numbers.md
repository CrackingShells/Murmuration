# Numbers plotted in figures 1 to 5 (written by w09j_figures.py; no case text)

## Figure 1: block rate on refusals against block rate on natural allows

| judge, arm | refusals blocked | CP 95% | natural allows blocked, raw | CP 95% | weighted rate | session-cluster bootstrap 95% (1,000 draws, seed 20261026) |
|:--|--:|:--|--:|:--|--:|:--|
| qwen3.6-35b-a3b, full rules | 45 of 67 = 67.2% | 54.6 to 78.2% | 58 of 212 = 27.4% | 21.5 to 33.9% | 26.3% | 19.2 to 33.0% |
| qwen3.6-35b-a3b, short criterion | 24 of 67 = 35.8% | 24.5 to 48.5% | 36 of 212 = 17.0% | 12.2 to 22.7% | 13.8% | 9.7 to 18.2% |
| gemma-4-26b-a4b, full rules | 16 of 67 = 23.9% | 14.3 to 35.9% | 23 of 212 = 10.8% | 7.0 to 15.8% | 10.8% | 5.5 to 17.9% |
| gemma-4-26b-a4b, short criterion | 31 of 67 = 46.3% | 34.0 to 58.9% | 42 of 212 = 19.8% | 14.7 to 25.8% | 16.9% | 11.7 to 23.1% |
| Granite Guardian 4.1 8B, short criterion | 50 of 67 = 74.6% | 62.5 to 84.5% | 132 of 212 = 62.3% | 55.4 to 68.8% | 59.8% | 50.9 to 67.8% |
| gpt-oss-safeguard-20b, short criterion | 8 of 67 = 11.9% | 5.3 to 22.2% | 2 of 28 = 7.1% | 0.9 to 23.5% | 3.9% | 0.0 to 6.7% |
| Granite Guardian 4.1 8B, full rules (variant B) | 62 of 65 = 95.4% | 87.1 to 99.0% | not run | | | |
| gpt-oss-safeguard-20b, full rules | 2 of 28 = 7.1% | 0.9 to 23.5% | not run | | | |

## Figure 2: weighted ROC (refusals positive, natural allows weighted N_h/m_h)

| judge, arm | AUC weighted | 95% session-cluster bootstrap (1,000 draws, seed 20261026) | AUC unweighted | TPR at weighted FPR <= 10% | threshold | weighted FPR there | judge's own verdict: TPR / weighted FPR |
|:--|--:|:--|--:|--:|--:|--:|:--|
| qwen3.6-35b-a3b, full rules | 0.788 | 0.716 to 0.847 | 0.766 | 31 of 67 = 46.3% | 1.37 | 9.9% | 67.2% / 26.3% |
| qwen3.6-35b-a3b, short criterion | 0.734 | 0.653 to 0.804 | 0.697 | 21 of 67 = 31.3% | 0.32 | 9.4% | 35.8% / 13.8% |
| gemma-4-26b-a4b, full rules | 0.650 | 0.557 to 0.734 | 0.659 | 16 of 67 = 23.9% | 1.13 | 9.9% | 23.9% / 10.8% |
| gemma-4-26b-a4b, short criterion | 0.757 | 0.679 to 0.835 | 0.725 | 22 of 67 = 32.8% | 7.13 | 9.6% | 46.3% / 16.9% |
| Granite Guardian 4.1 8B, short criterion | 0.565 | 0.474 to 0.655 | 0.556 | 8 of 67 = 11.9% | 6.47 | 10.0% | 74.6% / 59.8% |
| gpt-oss-safeguard-20b, short criterion | no score | | | | | | 11.9% / 3.9% (28 allows) |

## Figure 3: wave 8's 22 hand-written cases against recorded decisions (balanced accuracy at the judge's own verdict)

| judge, arm | written cases: correct (CP 95%) | written: refuse-labelled blocked of 11 | allow-labelled blocked of 11 | recorded: balanced accuracy (weighted allows) | bootstrap 95% (1,000 draws) | AUC (weighted) |
|:--|:--|--:|--:|--:|:--|--:|
| qwen3.6-35b-a3b, full rules | 22 of 22 | 11 of 11 | 0 of 11 | 0.704 | 0.633 to 0.777 | 0.788 |
| qwen3.6-35b-a3b, short criterion | 22 of 22 | 11 of 11 | 0 of 11 | 0.610 | 0.554 to 0.666 | 0.734 |
| gemma-4-26b-a4b, full rules | 22 of 22 | 11 of 11 | 0 of 11 | 0.565 | 0.500 to 0.633 | 0.650 |
| gemma-4-26b-a4b, short criterion | 22 of 22 | 11 of 11 | 0 of 11 | 0.647 | 0.582 to 0.708 | 0.757 |
| Granite Guardian 4.1 8B, short criterion | 20 of 22 | 10 of 11 | 1 of 11 | 0.574 | 0.504 to 0.644 | 0.565 |
| gpt-oss-safeguard-20b, short criterion | 22 of 22 | 11 of 11 | 0 of 11 | 0.540 | 0.503 to 0.587 | no score |

## Figure 4: latency on unique cases (one row per case id; first call apart from the rest)

| judge, arm (backend) | first call (s) | first call kind | steady p50 (s) | steady p90 (s) | steady n |
|:--|--:|:--|--:|:--|--:|
| qwen3.6-35b-a3b, full rules (llama-server) | 38.5 | test call, rules prefix uncached | 0.72 | 1.74 | 384 |
| gemma-4-26b-a4b, full rules (llama-server) | 46.7 | test call, rules prefix uncached | 0.92 | 2.25 | 384 |
| qwen3.6-35b-a3b, short criterion (llama-server) | 0.6 | cache already warm | 0.54 | 1.14 | 384 |
| gemma-4-26b-a4b, short criterion (llama-server) | 0.7 | cache already warm | 0.59 | 1.28 | 384 |
| Granite Guardian 4.1 8B, short criterion (llama-server) | 0.6 | cache already warm (llama-server rerun) | 1.59 | 2.87 | 384 |
| gpt-oss-safeguard-20b, short criterion (LM Studio) | 3.7 | short prefix | 4.14 | 8.24 | 195 |
| Granite Guardian 4.1 8B, full rules (variant B) (LM Studio) | 97.5; 117.6; 11.8 | main run (resumed), prefix partly cached; two probe runs, prefix uncached | 2.73 | 5.91 | 125 |
| gpt-oss-safeguard-20b, full rules (LM Studio) | 50.6 | prefix uncached | 15.19 | 27.06 | 37 |
| Granite Guardian 4.1 8B, short criterion (LM Studio) | 6.2 | ran beside a second model | 1.71 | 2.88 | 395 |

## Figure 5: the 19 refusal-then-allowed pairs (verdict of the refusal member, verdict of the retry)

| judge, arm | pairs scored | separated (blocks refusal, allows retry) | both blocked | both allowed | reversed (allows refusal, blocks retry) | separated, CP 95% of scored |
|:--|--:|--:|--:|--:|--:|:--|
| qwen3.6-35b-a3b, full rules | 19 | 8 | 4 | 6 | 1 | 20.3 to 66.5% |
| qwen3.6-35b-a3b, short criterion | 19 | 9 | 0 | 7 | 3 | 24.4 to 71.1% |
| gemma-4-26b-a4b, full rules | 19 | 3 | 0 | 15 | 1 | 3.4 to 39.6% |
| gemma-4-26b-a4b, short criterion | 19 | 7 | 0 | 8 | 4 | 16.3 to 61.6% |
| Granite Guardian 4.1 8B, short criterion | 19 | 7 | 9 | 3 | 0 | 16.3 to 61.6% |
| gpt-oss-safeguard-20b, short criterion | 19 | 3 | 0 | 16 | 0 | 3.4 to 39.6% |
| Granite Guardian 4.1 8B, full rules (variant B) | 17 | 0 | 16 | 0 | 1 | 0.0 to 19.5% |
| gpt-oss-safeguard-20b, full rules | 5 | 0 | 0 | 5 | 0 | 0.0 to 52.2% |
