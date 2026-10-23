# Counterfactual price of the gate on past hand-backs (ESTIMATE)

Hand-backs priced: 180 of 183 (PI cost known); kept size after the gate S = 1200 characters (ASSUMPTION; the live test replaces it).

Formulas, per fired hand-back i (hb_i > N):
- PI saving = u_i x (hb_i - S): u_i = USD of the PI-context item / its characters (write once + later reads + re-writes, explorer-w08-d's model).
- worker cost w_i = the worker's own cache-read price x its context at the hand-back (one extra request) + (S + (hb_i - S)) x 0.4 tokens x USD 10 per M (the second message and a Write of all that was dropped, an upper bound: much of it is already in the file); with `low`, only S x 0.4 x 10 / 1e6 (the detail is already in the file).
- CF1 net = saving - w_i. PI keeps the short message only.
- opening cost o_i = u_i x section_i + the PI's next-request cache-read USD + USD 0.003 (a tool call's output). section_i = the worker's own report Result section (explorer), the claim's headline above `method:` (author) or the verdict and reason lines (reproducer); with `full`, the whole claim head and verdict section (median of the role when the worker's file is not in the lab).
- CF2-all net = CF1 net - o_i for every fired hand-back. CF2-new net = CF1 net - o_i for those after which the PI did not open the named file in the past (pi_read = 0); the others are assumed to be opened anyway.
- break-even p* = sum of (saving - w_i) / sum of o_i over the fired hand-backs: the share of them the PI may newly open before the net turns negative.

| N | role | hand-backs | fired | PI chars dropped | PI saving USD | worker cost USD | CF1 net | CF2-all net | CF2-new net | p* | share the PI opened in the past |
|--|--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1000 | all | 180 | 178 | 533344 | 7.024 | 4.502 | 2.521 | 18.949 | -16.427 | -10.660 | 0.13 | 0.29 |
| 1000 | explorer | 23 | 23 | 117753 | 1.883 | 0.570 | 1.314 | 2.749 | -1.435 | 0.153 | 0.48 | 0.70 |
| 1000 | author | 95 | 93 | 253711 | 3.322 | 2.948 | 0.373 | 10.098 | -9.725 | -7.826 | 0.04 | 0.17 |
| 1000 | reproducer | 61 | 61 | 154155 | 1.713 | 0.978 | 0.736 | 6.050 | -5.314 | -3.034 | 0.12 | 0.33 |
| 1500 | all | 180 | 169 | 532590 | 7.015 | 4.290 | 2.725 | 18.099 | -15.374 | -9.798 | 0.15 | 0.30 |
| 1500 | explorer | 23 | 23 | 117753 | 1.883 | 0.570 | 1.314 | 2.749 | -1.435 | 0.153 | 0.48 | 0.70 |
| 1500 | author | 95 | 86 | 252986 | 3.313 | 2.762 | 0.551 | 9.377 | -8.826 | -7.119 | 0.06 | 0.17 |
| 1500 | reproducer | 61 | 59 | 154126 | 1.713 | 0.952 | 0.761 | 5.921 | -5.159 | -2.879 | 0.13 | 0.34 |
| 2000 | all | 180 | 150 | 522612 | 6.911 | 3.747 | 3.164 | 16.325 | -13.161 | -7.879 | 0.19 | 0.33 |
| 2000 | explorer | 23 | 23 | 117753 | 1.883 | 0.570 | 1.314 | 2.749 | -1.435 | 0.153 | 0.48 | 0.70 |
| 2000 | author | 95 | 70 | 244857 | 3.228 | 2.258 | 0.970 | 7.791 | -6.822 | -5.409 | 0.12 | 0.19 |
| 2000 | reproducer | 61 | 56 | 152277 | 1.695 | 0.913 | 0.782 | 5.732 | -4.950 | -2.670 | 0.14 | 0.36 |
| 2500 | all | 180 | 139 | 511400 | 6.791 | 3.451 | 3.339 | 15.040 | -11.701 | -6.892 | 0.22 | 0.33 |
| 2500 | explorer | 23 | 23 | 117753 | 1.883 | 0.570 | 1.314 | 2.749 | -1.435 | 0.153 | 0.48 | 0.70 |
| 2500 | author | 95 | 64 | 238965 | 3.156 | 2.049 | 1.107 | 7.098 | -5.991 | -4.887 | 0.16 | 0.17 |
| 2500 | reproducer | 61 | 51 | 146957 | 1.646 | 0.826 | 0.819 | 5.141 | -4.321 | -2.206 | 0.16 | 0.37 |
| 3000 | all | 180 | 124 | 487683 | 6.519 | 3.076 | 3.444 | 13.242 | -9.798 | -5.402 | 0.26 | 0.35 |
| 3000 | explorer | 23 | 23 | 117753 | 1.883 | 0.570 | 1.314 | 2.749 | -1.435 | 0.153 | 0.48 | 0.70 |
| 3000 | author | 95 | 54 | 223129 | 2.975 | 1.749 | 1.226 | 5.753 | -4.527 | -3.793 | 0.21 | 0.17 |
| 3000 | reproducer | 61 | 46 | 139076 | 1.556 | 0.750 | 0.806 | 4.688 | -3.882 | -1.810 | 0.17 | 0.39 |
| 3500 | all | 180 | 110 | 458966 | 6.245 | 2.819 | 3.426 | 11.739 | -8.313 | -4.661 | 0.29 | 0.34 |
| 3500 | explorer | 23 | 22 | 115509 | 1.838 | 0.553 | 1.284 | 2.606 | -1.322 | 0.124 | 0.49 | 0.68 |
| 3500 | author | 95 | 50 | 215137 | 2.887 | 1.629 | 1.259 | 5.257 | -3.998 | -3.264 | 0.24 | 0.18 |
| 3500 | reproducer | 61 | 37 | 120595 | 1.414 | 0.630 | 0.784 | 3.824 | -3.039 | -1.568 | 0.21 | 0.35 |
| 4000 | all | 180 | 88 | 402840 | 5.543 | 2.425 | 3.118 | 9.407 | -6.289 | -3.989 | 0.33 | 0.28 |
| 4000 | explorer | 23 | 17 | 102247 | 1.651 | 0.436 | 1.214 | 2.032 | -0.817 | 0.254 | 0.60 | 0.65 |
| 4000 | author | 95 | 45 | 202328 | 2.741 | 1.529 | 1.211 | 4.771 | -3.560 | -2.997 | 0.25 | 0.16 |
| 4000 | reproducer | 61 | 25 | 90540 | 1.046 | 0.452 | 0.594 | 2.552 | -1.958 | -1.293 | 0.23 | 0.28 |
| 5000 | all | 180 | 42 | 251233 | 3.664 | 1.269 | 2.394 | 4.573 | -2.178 | -0.998 | 0.52 | 0.31 |
| 5000 | explorer | 23 | 7 | 69479 | 1.209 | 0.197 | 1.012 | 0.998 | 0.014 | 0.446 | 1.01 | 0.43 |
| 5000 | author | 95 | 25 | 135088 | 1.882 | 0.867 | 1.015 | 2.791 | -1.777 | -1.281 | 0.36 | 0.24 |
| 5000 | reproducer | 61 | 9 | 38941 | 0.468 | 0.199 | 0.269 | 0.731 | -0.463 | -0.209 | 0.37 | 0.44 |
| 6000 | all | 180 | 21 | 161808 | 2.565 | 0.643 | 1.922 | 2.411 | -0.489 | -0.068 | 0.80 | 0.24 |
| 6000 | explorer | 23 | 5 | 60842 | 1.103 | 0.139 | 0.964 | 0.654 | 0.310 | 0.397 | 1.47 | 0.20 |
| 6000 | author | 95 | 13 | 83026 | 1.245 | 0.442 | 0.803 | 1.547 | -0.744 | -0.489 | 0.52 | 0.23 |
| 6000 | reproducer | 61 | 2 | 10215 | 0.112 | 0.054 | 0.057 | 0.158 | -0.101 | -0.023 | 0.36 | 0.50 |

Total USD the 180 hand-backs cost the PI over their lives: 12.37 (748097 characters of worker text; PI frame about 1276 characters each).
