# check_log (run2)
Note: pandas unavailable under python3 -I; used csv module. Scripts a.py, b.py, c.py in this dir.
1. a.py: rows per (experiment,source,map): binary identity 123, binary random 123, binary trained 51 (51 unique (omega,k,seed) keys, omega 2..8, 17 (omega,k) pairs x 3 seeds); random rows have no duplicate keys.
2. b.py: pair trained with random on (omega,k,seed): 51 paired, 0 missing. Exact equality of distortion: 40 equal, 11 differ.
   Tolerance sweep (|diff| <= tol): 1e-12:40, 1e-9:40, 1e-6:40, 1e-4:41, 1e-3:46.
   Differing runs (omega,k,seed: trained - random): (2,1,2) -0.1060; (3,2,1) -0.0261; (3,2,2) -0.0238; (5,4,1) -0.00171; (7,1,1) -0.000275; (8,1,0) -0.00111; (8,1,1) -0.000305; (8,1,2) +0.000168; (8,2,0) -0.0000458; (8,2,1) -0.000168; (8,2,2) +0.000137.
3. c.py: by omega [equal, differ]: 2:[2,1] 3:[4,2] 4:[6,0] 5:[8,1] 6:[9,0] 7:[8,1] 8:[3,6]. Differing with |d|>1e-3: exactly 5, (2,1,2),(3,2,1),(3,2,2),(5,4,1),(8,1,0), all omega<=8. Trained better than random 9, worse 2.
4. Code (run_all.py train_hamming/task_binary): trained = bitwise-majority update, bin_iters iterations from the random table rtab, evaluated on held-out T; ties and unvisited entries keep current bits. Trained only run for omega <= bin_trained_max (8 full, 6 quick).
