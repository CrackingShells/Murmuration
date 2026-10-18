# check_log (run1)

Reading: data/derived/trellis_rd.csv (722 rows), code/trellis/run_all.py (listing of code/trellis/ showed figures.py, run_all.py, viterbi.py; only run_all.py read), __design__/problem_framing.md. python3 -I (no pandas available under -I; used csv module). Script: run1/an.py.

## Cmd 1: head/wc
header: experiment,source,map,omega,k,rate,seed,n_values,distortion,bound,excess_db,rate_gap_bits,closed_form,train_distortion ; 723 lines.

## Cmd 2: python3 -I an.py
- binary maps: identity 123, random 123, trained 51. (train_distortion non-empty also on real/trained 87 and real/trained_big 2, not binary.)
- trained 51, random 123, paired on (omega,k,seed) = 51; n_values equal for all pairs.
- Code (run_all.py task_binary): trained rows only for omega<=bin_trained_max=8, ks (1,2,4) with k<omega, seeds 0,1,2 -> 17 (omega,k) x 3 = 51. Trained table starts from the random table rtab of the same (omega,k,seed), 4 iters of Viterbi / bitwise-majority on a separate training target (Ttr), evaluated on the held-out eval target T.
- equal (exact float ==): 40 ; different: 11. Equal within 1e-12 or 1e-9: also 40 (no near-ties).
- Different runs (omega,k,seed: trained, random, trained-random):
  (2,1,2) 0.19568 vs 0.30167 diff -0.105988
  (3,2,1) 0.21245 vs 0.23853 diff -0.026078
  (3,2,2) 0.16228 vs 0.18611 diff -0.023835
  (5,4,1) 0.10832 vs 0.11003 diff -0.001709
  (7,1,1) 0.30380 vs 0.30407 diff -0.000275
  (8,1,0) 0.310852 vs 0.311966 diff -0.001114
  (8,1,1) 0.311279 vs 0.311584 diff -0.000305
  (8,1,2) 0.310928 vs 0.310760 diff +0.000168
  (8,2,0) 0.236969 vs 0.237015 diff -0.0000458
  (8,2,1) 0.236450 vs 0.236618 diff -0.000168
  (8,2,2) 0.237061 vs 0.236923 diff +0.000137
- omega distribution of the 51 pairs: 2:3, 3:6, 4:6, 5:9, 6:9, 7:9, 8:9. Max omega among equal runs = 8.

## Cmd 3: breakdown
(see output summarised in report) differences by omega: 2:1, 3:2, 5:1, 7:1, 8:6 ; by k: see below.
Cmd 3 output: equal by omega {2:2,3:4,4:6,5:8,6:9,7:8,8:3}; different by omega {2:1,3:2,5:1,7:1,8:6}; different by k {1:5,2:5,4:1}; trained rows with omega>8: 0; different with omega<=7: 5 runs [(2,1,2),(3,2,1),(3,2,2),(5,4,1),(7,1,1)]; train_distortion == eval distortion in 0 of 51 (expected, held-out target).
Observation: 5 differences at omega<=7 and 6 at omega=8; all 11 at omega<=8 only because no trained rows exist above 8. Note the CSV compares distortions only, not tables; equal distortion is necessary, not sufficient, for an identical table.
