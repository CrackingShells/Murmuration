You are an independent verifier in a research lab. One claim from a lab report is to be checked against the committed data and code of the study.

The author's report that makes the claim follows, complete and verbatim, between the two lines of equals signs.

==========
# Strided trellis (Q5) — Findings (v0)

Date: 2026-10-18

---
type: findings
topic: strided_trellis
date: 2026-10-18
version: v0
prior-version: none
key-metric: MSE above D(R) at 2 bits/value, N(0,1), identity reads vs random-table reads at ω = 16: 4.68 dB vs 0.38 dB (prior: N/A, delta: N/A)
decision-required: confirm
---

Notation is `__design__/problem_framing.md` (G, ω, k, r_i(G), regimes B and C). Added: **identity reads** = f is the
identity (regime B: the output is the raw window); **mapped reads** = f is a table over the 2^ω windows (regime C);
**c_x** = number of windows that contain bit x of G (≈ ω/k); **excess** = 10 log10(MSE / D(R)), D(R) = 2^(−2R).
Every G below is the **exact optimum for its target** (Viterbi over 2^(ω−k) states, checked against brute force
over all 2^n strings in 120 tiny cases), so every number is a property of the read rule, not of the search.
Provenance label (framing §3.1): G is *per-target optimized*; its n = ω + (m−1)k bits are the whole rate. Random
tables come from a seeded PRNG (cost ~0); trained tables are *side information* and are scored on a held-out target.
Code: `code/trellis/` (`viterbi.py --selftest`, `run_all.py [--quick]`, `figures.py`); data
`data/derived/trellis_rd.csv` (722 rows). Labels: **DERIVED** (closed form, checked numerically), **MEASURED**.

## Headline Result

metric: excess MSE over D(R) at 2 bits/value on i.i.d. N(0,1), Viterbi-optimal G, window width ω (k = 2)
value: identity reads 4.68 dB (MSE 0.1837, the same for every ω = 4…16); random Gaussian table 0.38 dB at ω = 16 (MSE 0.0682); trained table 0.67 dB at ω = 12 (0.0730); Lloyd–Max scalar 2.74 dB (0.1175)
unit: dB above D(R) = 0.0625
prior: N/A (first run)
direction: new

Binary companion (Bernoulli(1/2), Hamming): identity reads are a **repetition code**, D = 0.25 at rate 1/2 (R(D) = 0.110,
2.65× the bits) and never improve with ω; a random table at rate 1/4 reaches D = 0.2213 at ω = 16 against R(D) = 0.2145 (1.05× the bits).

```mermaid
graph LR
  G["G: n = ω+(m-1)k bits"] -->|window j = r_jk G, ω bits| W["window"]
  W -->|regime B: f = id| O1["output = the ω bits"]
  W -->|regime C: f = table of 2^ω entries| O2["output = f(window)"]
  O1 --> R["each bit of G sits in c_x ≈ ω/k outputs: a repetition code"]
  O2 --> D["decorrelated outputs: random-coding behaviour, gap to R(D) shrinks with ω"]
```

## Results Tables

### A. Binary targets: identity vs random table at fixed rate (3 seeds, N = 65 536 bits)

| rate k/ω | (ω, k) | R(D) distortion | identity D | exact identity D (DERIVED) | random-table D | rate / R(D_id) | rate / R(D_rand) |
|:--|:--|--:|--:|--:|--:|--:|--:|
| 1/2 | (2, 1) | 0.1100 | 0.2504 | 0.2500 | 0.2585 | 2.66 | 2.85 |
| 1/2 | (4, 2) | 0.1100 | 0.2512 | 0.2500 | 0.1767 | 2.68 | 1.53 |
| 1/2 | (8, 4) | 0.1100 | 0.2488 | 0.2500 | 0.1407 | 2.62 | 1.21 |
| 1/3 | (3, 1) | 0.1740 | 0.2507 | 0.2500 | 0.2412 | 1.78 | 1.64 |
| 1/3 | (6, 2) | 0.1740 | 0.2495 | 0.2500 | 0.2122 | 1.76 | 1.31 |
| 1/3 | (12, 4) | 0.1740 | 0.2495 | 0.2500 | 0.1873 | 1.76 | 1.10 |
| 1/4 | (4, 1) | 0.2145 | 0.3123 | 0.3125 | 0.2700 | 2.40 | 1.58 |
| 1/4 | (8, 2) | 0.2145 | 0.3122 | 0.3125 | 0.2369 | 2.40 | 1.19 |
| 1/4 | (16, 4) | 0.2145 | 0.3116 | 0.3124 | 0.2213 | 2.38 | 1.05 |

rate / R(D_x) = bits spent per bit that R(D) would need to reach the same measured D (1.00 = on the bound).

### B. Real targets, k = 2 bits/value, i.i.d. N(0,1): MSE (excess dB over D(R) = 0.0625), mean of 2 seeds

| ω | identity | monotone quantile levels | random table | trained table (held-out) |
|--:|--:|--:|--:|--:|
| 2 | 0.1903 (4.83) | 0.1444 (3.64) | 0.2805 (6.52) | 0.1173 (2.73) |
| 4 | 0.1834 (4.68) | 0.1475 (3.73) | 0.1433 (3.60) | 0.0969 (1.90) |
| 6 | 0.1837 (4.68) | 0.1479 (3.74) | 0.1115 (2.51) | 0.0864 (1.41) |
| 8 | 0.1837 (4.68) | 0.1480 (3.74) | 0.0904 (1.60) | 0.0817 (1.16) |
| 10 | 0.1837 (4.68) | 0.1480 (3.74) | 0.0787 (1.00) | 0.0768 (0.89) |
| 12 | 0.1837 (4.68) | 0.1480 (3.74) | 0.0735 (0.71) | 0.0730 (0.67) |
| 14 | 0.1837 (4.68) | 0.1480 (3.74) | 0.0700 (0.50) | not run |
| 16 | 0.1837 (4.68) | 0.1480 (3.74) | 0.0682 (0.38) | not run |

References at 2 bits: D(R) = 0.0625; Lloyd–Max scalar 0.1175 (2.74 dB); QTIP's TCQ, L = 16: 0.068–0.069 (0.4 dB) [source: literature findings, from QTIP Table 1].
ω = 2 = k is a scalar quantizer (one state): identity is the uniform 4-level quantizer, trained recovers Lloyd–Max.

### C. MiniLM-L6 weights (`encoder.layer.0.intermediate.dense.weight`, unit variance), k = 2, 10^5 values, 1 seed

| ω | identity | monotone quantile levels | random table | trained table (held-out) |
|--:|--:|--:|--:|--:|
| 2 | 0.2001 (5.05) | 0.1694 (4.33) | 0.3728 (7.76) | 0.1362 (3.38) |
| 4 | 0.1939 (4.92) | 0.1675 (4.28) | 0.1886 (4.80) | 0.1077 (2.36) |
| 8 | 0.1940 (4.92) | 0.1680 (4.29) | 0.1020 (2.13) | 0.0883 (1.50) |
| 12 | 0.1940 (4.92) | 0.1680 (4.29) | 0.0813 (1.14) | 0.0792 (1.03) |
| 14 | 0.1940 (4.92) | 0.1680 (4.29) | 0.0770 (0.90) | not run |
| bound rows | Lloyd–Max (empirical) 0.1362 (3.38) | Shannon lower bound (histogram estimate) 0.0615 (−0.07) | Gaussian D(R) 0.0625 | |

### D. Other rates, i.i.d. N(0,1): excess dB (identity is flat in ω from ω ≈ k+1)

| k | identity | Lloyd–Max | random table at ω = 12 | trained at ω = 10 (random at ω = 10) |
|--:|--:|--:|--:|--:|
| 1 | 4.65 | 1.62 | 0.49 | 0.53 (0.65) |
| 2 | 4.68 | 2.74 | 0.71 | 0.89 (1.00) |
| 3 | 4.86 | 3.45 | 0.98 | 1.31 (1.62) |

### E. Trained table: what it buys over a random table, and the train / test gap (k = 2, N(0,1))

| ω | random − trained (dB) | in-sample MSE | held-out MSE | held-out, 4× training data |
|--:|--:|--:|--:|--:|
| 4 | 1.70 | 0.0969 | 0.0969 | n/a |
| 8 | 0.44 | 0.0788 | 0.0817 | 0.0809 |
| 10 | 0.11 | 0.0709 | 0.0768 | 0.0766 |
| 12 | 0.04 | 0.0626 | 0.0730 | n/a |

## Observations

| Signal | Baseline / Expected | Observed [source] | Interpretation |
|:--|:--|:--|:--|
| Identity reads, binary | Closed form: bit x of G is compared with one target bit in each of its c_x windows, so the optimum is a majority vote and D = Σ_x E min(B, c_x − B) / (mω) | Viterbi minus formula: max 0.003 over 123 runs; in-run check passes at 5σ [source: `trellis_rd.csv`, `check()`] | The Viterbi search is not needed for identity+Hamming; the strided code of theorem T11 (injective, linear) is a repetition code with multiplicities c_x. Distortion depends on c = ω/k only: D = 0.25 at c = 2 for all (ω, k) |
| Identity at low rate | rate / R(D) → π ln 2 = 2.178 as c → ∞ (majority vote of c fair bits) | 2.178 at c = 1000 from the closed form; 2.66 → 2.40 at c = 2, 4 [source: `check()`, table A] | Identity reads waste about 2.2× the bits at every low rate; the shortfall is a constant, not a function of ω |
| Random table, binary, fixed rate | Random-coding behaviour: gap to R(D) closes as ω grows at fixed k/ω | rate/R(D): 2.85 → 1.53 → 1.21 (rate 1/2, ω = 2, 4, 8); 1.58 → 1.19 → 1.05 (rate 1/4, ω = 4, 8, 16) [source: table A] | Decorrelation is what lets longer windows pay off; the gap is still 5–21 % of the bits at the longest windows shown |
| Identity, real, k = 2 | 4-level uniform scalar over ±3σ: 0.1903 (the ω = 2 case) | 0.1834–0.1837 for every ω = 4…16, sd ≤ 0.0003 across seeds [source: table B] | A longer window adds no resolution: the Viterbi path can steer only the leading bits of each read, the trailing bits belong to later reads. The best identity code is about 4.7 dB above D(R), worse than a Lloyd–Max scalar by 1.9 dB |
| Random table, real, k = 2, ω = 16 | QTIP TCQ (L = 16, computed code) 0.068–0.069 | 0.0682 (0.38 dB), 2 seeds: 0.06809, 0.06826 [source: table B] | A seeded random Gaussian table reproduces the published TCQ figure at L = 16 on a window of the same width; no clever code is needed to get within 0.4 dB at this ω, only decorrelation |
| Trained table vs random | Training should help where random is far from D(R) | Gain 1.70 dB (ω = 4), 0.44 (8), 0.11 (10), 0.04 (12); 4× more training data moves held-out MSE by ≤ 0.0008 [source: table E] | Alternating Viterbi/centroid reaches a local optimum that the random table matches by ω ≈ 12; the limit is the optimum, not the data volume |
| MiniLM vs N(0,1) | Same trend if weights are near-Gaussian | Same ordering of maps; identity 4.92 dB, random ω = 14 0.90 dB; Lloyd–Max 3.38 dB (0.64 dB worse than on N(0,1)) [source: table C] | Heavier tails hurt the scalar quantizer most; the Shannon lower bound estimate (0.0615) is within 0.07 dB of Gaussian D(R), so the dB figures are meaningful for these weights |

## Charts & Visualizations

![Binary: distortion vs rate for identity and random reads, and fixed-rate ladders](00-findings_v0-binary_rd.png)

Caption: Hamming distortion vs rate k/ω on Bernoulli(1/2) targets (points labelled by ω; mean of 3 seeds) against R(D) = 1 − h(D); identity reads (left) sit on a repetition-code curve far above the bound, random-table reads (middle) approach it as ω grows; at fixed rate (right) only the random table improves with ω.

![Gaussian and MiniLM weights: MSE vs ω per map](00-findings_v0-gauss_weights_mse.png)

Caption: MSE per value at 2 bits vs ω (log scale; bars = range over 2 seeds, MiniLM one seed) for identity, monotone-quantile, random and trained maps against D(R), Lloyd–Max and the QTIP range; the identity curve is flat while mapped curves fall with ω.

![Excess dB over D(R) for k = 1, 2, 3](00-findings_v0-k_sweep.png)

Caption: Excess MSE in dB above D(R) = 2^(−2k) on N(0,1) at 1, 2, 3 bits per value; identity stays near 4.7 dB at every k, the random table crosses below Lloyd–Max at ω ≈ 6–8 and the trained table leads until ω ≈ 12.

## Contradictions & Surprises

- Identity MSE is the same to four decimals for every ω from 4 to 16 (0.1837): sixteen-fold more trellis states per step buys nothing, and the result is 1.9 dB worse than the scalar Lloyd–Max quantizer at the same 2 bits.
- A monotone map with the right marginal (equiprobable Gaussian levels) is no better in kind: it also plateaus (0.1480, 3.74 dB). Reordering window values is not decorrelation; the correlation structure of overlapping reads is what costs.
- For small windows a mapped read is worse than identity: the random table loses to identity for ω ≤ 3 (k = 2), with large seed variance (ω = 2: 0.28 ± 0.07), because 2^ω random entries do not cover the line.
- Bitwise-majority training of a binary table is a fixed point from a random start (identical to the random table in 46 of 51 runs; the 5 exceptions are all at ω ≤ 8), so no "trained binary" curve is reported.
- The in-sample MSE of a trained table at ω = 12 (0.0626) reaches D(R) because the 4096-entry table is side information that the rate does not count; only the held-out value (0.0730) is a rate-honest number.

## Steering Questions

- [now] Retire raw window reads for real-valued targets and carry regime C (seeded random table, cost ~0) into wave 3's shared-G experiments? Identity reads are 4.7 dB above D(R) at any ω and any tested k; a random table is within 0.4–1.0 dB at ω = 12–16.
- [next run] Which cheap structured f (XOR of window and a rotation, popcount-based, multiplicative hash) matches the random table? A computable f removes the table cost that a trained table carries and is what a kernel would implement.
- [next run] Do ω = 13–16 trained tables, with a structured parametrization so the table is not side information, beat the random table at equal bits? The measured gain was 0.04 dB at ω = 12 for free tables.
- [later] Real-model slices (gemma tensors, several layers) and k = 3–4: do the weight-specific heavy tails change which f wins, and does a shared G over a tensor class keep the 0.4–1 dB figure?
- [later] State the repetition-code result (identity + Hamming) to the theory track as a corollary of T11, and ask whether other distortion measures keep the separability.

## Pointers

- Code: `code/trellis/viterbi.py`, `code/trellis/run_all.py`, `code/trellis/figures.py`
- Data: `data/derived/trellis_rd.csv` (columns: experiment, source, map, omega, k, rate, seed, n_values, distortion, bound, excess_db, rate_gap_bits, closed_form, train_distortion)
- Reproduce: `python3 code/trellis/run_all.py` (full, about 3.5 minutes on 12 cores, 1 900 CPU-seconds; rewrites the CSV and these figures), `python3 code/trellis/run_all.py --quick` (2 s, no files written), `python3 code/trellis/viterbi.py --selftest`
- Task spec: `__roadmap__/swc/strided_trellis.md`; framing: `__design__/problem_framing.md`
- Injectivity of regime B (T11): `__reports__/foundations/00-findings_v0.md`
- TCQ / QTIP reference numbers: `__reports__/literature/00-findings_v0.md`
==========

THE CLAIM (verbatim from the report's "Contradictions & Surprises"):
"Bitwise-majority training of a binary table is a fixed point from a random start (identical to the random table in 46 of 51 runs; the 5 exceptions are all at ω ≤ 8), so no "trained binary" curve is reported."

THE STUDY is the repository /Users/hacker/Documents/explore/combinatorics_on_binary. It is READ ONLY: other sessions use it, so never write, commit, or run anything there that modifies files.
You may read exactly these paths in it: data/derived/trellis_rd.csv, code/trellis/*.py, __design__/problem_framing.md.
You must not read anything else in it: nothing under __reports__/, __roadmap__/, code/reproduction/, code/review/, and no git history (no git log, show, diff or blame).
Write your scratch files only under /private/tmp/claude-501/-Users-hacker-Documents-explore-combinatorics-on-binary/82e8a947-1a0c-441c-bc39-df8e2e5fa743/scratchpad/runs/run2/ . Run your own Python with python3 -I (system python3 has numpy and pandas).

WHAT TO DO: check the claim. Find which rows of the CSV are the trained binary rows and which are the random binary rows, how they pair up, how often the two distortions are equal, and which runs are the exceptions. Judge the numbers (46 of 51, 5 exceptions, ω ≤ 8) and the wording ("identical", "fixed point"). Log each command you run and its numeric output in run2/check_log.md as you go.

FINAL ANSWER, in exactly this format and nothing else:
VERDICT: SUPPORTED | OVERSTATED | UNSUPPORTED
NUMBERS: the counts you found (runs compared, equal, different) and how you defined "equal"
EXCEPTIONS: the runs that differ, with ω, k, seed and the size of the difference
RATIONALE: at most 150 words, in your own words
