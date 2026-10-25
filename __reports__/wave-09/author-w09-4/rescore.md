
## qwen3.6-35b-a3b, full rules  (`qwen36_full.jsonl`)

- rows: 385; refusals found 67 of 67, natural allows 212 of 212; errors/unparsed 0
- non-finite scores: nan 0, +-inf 0 (of 279 refusals and natural allows)
- score = log pb - log pa recomputed from stored pb, pa: max abs difference 0.00e+00 over 279 rows
- probability mass of BLOCK-like plus ALLOW-like tokens in the top 20 for the first token (pb+pa): min 0.949, median 0.9983, share below 0.99: 0.115
- verdict 'block' iff score > 0: 279 of 279 (polarity: higher score = more block-like; refusals are the positive class)
- first word of generated text, refusals and natural allows: {'ALLOW': 176, 'BLOCK': 103}
- AUC, allow-weighted: 0.7876; unweighted 0.7658; with the sign flipped 0.2124 (sanity: 1 - AUC when no ties)
- weights: N_h/m_h sum 19243, min 2.0, max 222.1; Kish effective n of the 212 natural allows 143.5; strata 33; refusals 67 in 41 sessions
- bootstrap 95%: session-cluster 500 draws seed 20261026 (explorer's recipe) 0.717 to 0.855; session-cluster 2000 draws seed 20261027 0.717 to 0.852; refusals by session + allows within stratum 2000 draws seed 20261028 0.723 to 0.847

### weight sensitivity (qwen full)

- as sampled: AUC 0.788
- cap at 50: AUC 0.777
- cap at 20: AUC 0.776
- each stratum equal weight: AUC 0.765
- drop the 5 heaviest: AUC 0.783
- Bash only: refusals 57, natural allows 170 (weight 85.8%): AUC 0.783
- non-Bash: refusals 10, natural allows 42 (weight 14.2%): AUC 0.827
- refusals in the allow-label era (23): AUC 0.818; earlier (44): 0.771
- natural allows flagged risky (80, weight 24.0%) AUC 0.635; plain (132) 0.836

### operating points (qwen full; block iff score >= threshold; in-sample)

| target weighted FPR | threshold | achieved weighted FPR | refusals caught | TPR | natural allows blocked (raw) |
|--:|--:|--:|--:|--:|--:|
| 1% | 7.40 | 0.6% | 0 of 67 | 0.0% | 2 of 212 |
| 2% | 4.52 | 1.9% | 2 of 67 | 3.0% | 5 of 212 |
| 5% | 2.71 | 4.6% | 15 of 67 | 22.4% | 10 of 212 |
| 10% | 1.37 | 9.9% | 31 of 67 | 46.3% | 28 of 212 |
| 20% | 0.45 | 19.0% | 41 of 67 | 61.2% | 44 of 212 |
| 30% | -0.67 | 30.0% | 53 of 67 | 79.1% | 71 of 212 |
| 50% | -2.54 | 49.3% | 60 of 67 | 89.6% | 114 of 212 |

- model's own verdict (score > 0): 45 of 67 = 67.2% caught, weighted FPR 26.3%

### what the operating points mean at the recorded base rate (ESTIMATE; formula: PPV = TPR*67 / (TPR*67 + FPR*19243))

Recorded classifier-allows in the sampling frame, natural: 19243; recorded refusals: 67 (different windows: allows 2026-10-08 to 2026-10-25, refusals 2026-07 to 2026-10, so the ratio is a rough one).

| operating point | refusals caught | natural allows blocked (weighted, of 19,243) | PPV of a block | refusals found per 100 blocks |
|:--|--:|--:|--:|--:|
| FPR <= 5% (thr 2.71) | 15 | 882 | 1.7% | 1.7 |
| FPR <= 10% (thr 1.37) | 31 | 1897 | 1.6% | 1.6 |
| FPR <= 20% (thr 0.45) | 41 | 3652 | 1.1% | 1.1 |
| verdict (score > 0) | 45 | 5061 | 0.9% | 0.9 |
- if the refusals of the allow-label era only (23) were the ones belonging to the 19,243 allows: PPV at FPR <= 10% = 0.6%

### sensitivity to score noise (qwen full; Gaussian noise added to each score; sd from the spot check, see spotcheck.md)

- sd 0.0: AUC mean 0.788 (min 0.788, max 0.788); TPR at in-sample weighted FPR 10%: mean 46.3% (min 46.3%, max 46.3%)
- sd 0.3: AUC mean 0.785 (min 0.774, max 0.795); TPR at in-sample weighted FPR 10%: mean 43.9% (min 35.8%, max 52.2%)
- sd 0.5: AUC mean 0.783 (min 0.767, max 0.797); TPR at in-sample weighted FPR 10%: mean 42.1% (min 31.3%, max 53.7%)

### threshold chosen on training sessions, applied to held-out sessions (qwen full, target weighted FPR 10%)

| k folds | seeds | pooled held-out TPR (mean, min to max over seeds) | pooled held-out weighted FPR (mean, min to max) |
|--:|--:|:--|:--|
| 5 | 20 | 44.5% (40.3% to 47.8%) | 10.2% (8.1% to 11.9%) |
| 10 | 20 | 44.4% (43.3% to 46.3%) | 10.4% (8.7% to 11.9%) |

(in-sample the same target gives the TPR in the operating table; the held-out FPR is the check that the threshold carries over)

## qwen3.6, short criterion  (`qwen36_short.jsonl`)

- rows: 385; refusals found 67 of 67, natural allows 212 of 212; errors/unparsed 0
- non-finite scores: nan 0, +-inf 0 (of 279 refusals and natural allows)
- score = log pb - log pa recomputed from stored pb, pa: max abs difference 0.00e+00 over 279 rows
- probability mass of BLOCK-like plus ALLOW-like tokens in the top 20 for the first token (pb+pa): min 0.998, median 0.9996, share below 0.99: 0.000
- verdict 'block' iff score > 0: 279 of 279 (polarity: higher score = more block-like; refusals are the positive class)
- first word of generated text, refusals and natural allows: {'ALLOW': 219, 'BLOCK': 60}
- AUC, allow-weighted: 0.7341; unweighted 0.6968; with the sign flipped 0.2659 (sanity: 1 - AUC when no ties)
- weights: N_h/m_h sum 19243, min 2.0, max 222.1; Kish effective n of the 212 natural allows 143.5; strata 33; refusals 67 in 41 sessions
- bootstrap 95%: session-cluster 500 draws seed 20261026 (explorer's recipe) 0.652 to 0.812; session-cluster 2000 draws seed 20261027 0.652 to 0.807; refusals by session + allows within stratum 2000 draws seed 20261028 0.666 to 0.797

## gemma-4-26b-a4b, full rules  (`gemma4_full.jsonl`)

- rows: 385; refusals found 67 of 67, natural allows 212 of 212; errors/unparsed 0
- non-finite scores: nan 0, +-inf 6 (of 279 refusals and natural allows)
- score = log pb - log pa recomputed from stored pb, pa: max abs difference 0.00e+00 over 273 rows
- probability mass of BLOCK-like plus ALLOW-like tokens in the top 20 for the first token (pb+pa): min 0.994, median 1.0000, share below 0.99: 0.000
- verdict 'block' iff score > 0: 279 of 279 (polarity: higher score = more block-like; refusals are the positive class)
- first word of generated text, refusals and natural allows: {'ALLOW': 240, 'BLOCK': 39}
- AUC, allow-weighted: 0.6498; unweighted 0.6590; with the sign flipped 0.3502 (sanity: 1 - AUC when no ties)
- weights: N_h/m_h sum 19243, min 2.0, max 222.1; Kish effective n of the 212 natural allows 143.5; strata 33; refusals 67 in 41 sessions
- bootstrap 95%: session-cluster 500 draws seed 20261026 (explorer's recipe) 0.563 to 0.735; session-cluster 2000 draws seed 20261027 0.566 to 0.739; refusals by session + allows within stratum 2000 draws seed 20261028 0.578 to 0.721

## gemma-4-26b-a4b, short  (`gemma4_short.jsonl`)

- rows: 385; refusals found 67 of 67, natural allows 212 of 212; errors/unparsed 0
- non-finite scores: nan 0, +-inf 9 (of 279 refusals and natural allows)
- score = log pb - log pa recomputed from stored pb, pa: max abs difference 0.00e+00 over 270 rows
- probability mass of BLOCK-like plus ALLOW-like tokens in the top 20 for the first token (pb+pa): min 1.000, median 1.0000, share below 0.99: 0.000
- verdict 'block' iff score > 0: 279 of 279 (polarity: higher score = more block-like; refusals are the positive class)
- first word of generated text, refusals and natural allows: {'ALLOW': 206, 'BLOCK': 73}
- AUC, allow-weighted: 0.7565; unweighted 0.7245; with the sign flipped 0.2435 (sanity: 1 - AUC when no ties)
- weights: N_h/m_h sum 19243, min 2.0, max 222.1; Kish effective n of the 212 natural allows 143.5; strata 33; refusals 67 in 41 sessions
- bootstrap 95%: session-cluster 500 draws seed 20261026 (explorer's recipe) 0.683 to 0.835; session-cluster 2000 draws seed 20261027 0.679 to 0.831; refusals by session + allows within stratum 2000 draws seed 20261028 0.684 to 0.820

## Granite Guardian 4.1 8B, short  (`granite_short_scored.jsonl`)

- rows: 385; refusals found 67 of 67, natural allows 212 of 212; errors/unparsed 0
- non-finite scores: nan 0, +-inf 0 (of 279 refusals and natural allows)
- score = log pb - log pa recomputed from stored pb, pa: max abs difference 0.00e+00 over 279 rows
- probability mass of BLOCK-like plus ALLOW-like tokens in the top 20 for the first token (pb+pa): min 1.000, median 1.0000, share below 0.99: 0.000
- verdict 'block' iff score > 0: 279 of 279 (polarity: higher score = more block-like; refusals are the positive class)
- first word of generated text, refusals and natural allows: {'<THINK>': 279}
- AUC, allow-weighted: 0.5645; unweighted 0.5565; with the sign flipped 0.4355 (sanity: 1 - AUC when no ties)
- weights: N_h/m_h sum 19243, min 2.0, max 222.1; Kish effective n of the 212 natural allows 143.5; strata 33; refusals 67 in 41 sessions
- bootstrap 95%: session-cluster 500 draws seed 20261026 (explorer's recipe) 0.479 to 0.658; session-cluster 2000 draws seed 20261027 0.476 to 0.658; refusals by session + allows within stratum 2000 draws seed 20261028 0.483 to 0.639

## paired comparison on the same resampled sessions (AUC qwen full minus AUC Granite)

- qwen full minus granite_short_scored: +0.223, 95% +0.136 to +0.299, share of draws with qwen higher 1.000
- qwen full minus gemma4_short: +0.031, 95% -0.033 to +0.098, share of draws with qwen higher 0.834
- qwen full minus qwen36_short: +0.053, 95% +0.004 to +0.102, share of draws with qwen higher 0.984
