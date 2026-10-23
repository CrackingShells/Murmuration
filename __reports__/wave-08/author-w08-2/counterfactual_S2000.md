# Counterfactual price of the gate on past hand-backs (ESTIMATE)

Hand-backs priced: 180 of 183 (PI cost known); kept size after the gate S = 2000 characters (ASSUMPTION; the live test replaces it).

Formulas, per fired hand-back i (hb_i > N):
- PI saving = u_i x (hb_i - S): u_i = USD of the PI-context item / its characters (write once + later reads + re-writes, explorer-w08-d's model).
- worker cost w_i = the worker's own cache-read price x its context at the hand-back (one extra request) + (S + (hb_i - S)) x 0.4 tokens x USD 10 per M (the second message and a Write of all that was dropped, an upper bound: much of it is already in the file); with `low`, only S x 0.4 x 10 / 1e6 (the detail is already in the file).
- CF1 net = saving - w_i. PI keeps the short message only.
- opening cost o_i = u_i x section_i + the PI's next-request cache-read USD + USD 0.003 (a tool call's output). section_i = the worker's own report Result section (explorer), the claim's headline above `method:` (author) or the verdict and reason lines (reproducer); with `full`, the whole claim head and verdict section (median of the role when the worker's file is not in the lab).
- CF2-all net = CF1 net - o_i for every fired hand-back. CF2-new net = CF1 net - o_i for those after which the PI did not open the named file in the past (pi_read = 0); the others are assumed to be opened anyway.
- break-even p* = sum of (saving - w_i) / sum of o_i over the fired hand-backs: the share of them the PI may newly open before the net turns negative.

| N | role | hand-backs | fired | PI chars dropped | PI saving USD | worker cost USD | CF1 net | CF2-all net | CF2-new net | p* | share the PI opened in the past |
|--|--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1000 | all | 180 | 178 | 402612 | 5.445 | 6.635 | -1.190 | 18.949 | -20.138 | -14.371 | -0.06 | 0.29 |
| 1000 | explorer | 23 | 23 | 99353 | 1.614 | 1.041 | 0.573 | 2.749 | -2.176 | -0.587 | 0.21 | 0.70 |
| 1000 | author | 95 | 93 | 188857 | 2.525 | 3.963 | -1.437 | 10.098 | -11.535 | -9.637 | -0.14 | 0.17 |
| 1000 | reproducer | 61 | 61 | 107477 | 1.212 | 1.594 | -0.383 | 6.050 | -6.432 | -4.152 | -0.06 | 0.33 |
| 1500 | all | 180 | 169 | 402612 | 5.445 | 6.421 | -0.976 | 18.099 | -19.074 | -13.498 | -0.05 | 0.30 |
| 1500 | explorer | 23 | 23 | 99353 | 1.614 | 1.041 | 0.573 | 2.749 | -2.176 | -0.587 | 0.21 | 0.70 |
| 1500 | author | 95 | 86 | 188857 | 2.525 | 3.774 | -1.249 | 9.377 | -10.626 | -8.919 | -0.13 | 0.17 |
| 1500 | reproducer | 61 | 59 | 107477 | 1.212 | 1.568 | -0.357 | 5.921 | -6.277 | -3.997 | -0.06 | 0.34 |
| 2000 | all | 180 | 150 | 402612 | 5.445 | 5.838 | -0.393 | 16.325 | -16.717 | -11.435 | -0.02 | 0.33 |
| 2000 | explorer | 23 | 23 | 99353 | 1.614 | 1.041 | 0.573 | 2.749 | -2.176 | -0.587 | 0.21 | 0.70 |
| 2000 | author | 95 | 70 | 188857 | 2.525 | 3.238 | -0.713 | 7.791 | -8.504 | -7.091 | -0.09 | 0.19 |
| 2000 | reproducer | 61 | 56 | 107477 | 1.212 | 1.522 | -0.310 | 5.732 | -6.042 | -3.762 | -0.05 | 0.36 |
| 2500 | all | 180 | 139 | 400200 | 5.418 | 5.497 | -0.079 | 15.040 | -15.120 | -10.311 | -0.01 | 0.33 |
| 2500 | explorer | 23 | 23 | 99353 | 1.614 | 1.041 | 0.573 | 2.749 | -2.176 | -0.587 | 0.21 | 0.70 |
| 2500 | author | 95 | 64 | 187765 | 2.510 | 3.005 | -0.495 | 7.098 | -7.593 | -6.489 | -0.07 | 0.17 |
| 2500 | reproducer | 61 | 51 | 106157 | 1.199 | 1.414 | -0.215 | 5.141 | -5.355 | -3.240 | -0.04 | 0.37 |
| 3000 | all | 180 | 124 | 388483 | 5.283 | 5.026 | 0.257 | 13.242 | -12.986 | -8.589 | 0.02 | 0.35 |
| 3000 | explorer | 23 | 23 | 99353 | 1.614 | 1.041 | 0.573 | 2.749 | -2.176 | -0.587 | 0.21 | 0.70 |
| 3000 | author | 95 | 54 | 179929 | 2.419 | 2.642 | -0.222 | 5.753 | -5.975 | -5.241 | -0.04 | 0.17 |
| 3000 | reproducer | 61 | 46 | 102276 | 1.155 | 1.307 | -0.151 | 4.688 | -4.839 | -2.767 | -0.03 | 0.39 |
| 3500 | all | 180 | 110 | 370966 | 5.114 | 4.655 | 0.459 | 11.739 | -11.280 | -7.628 | 0.04 | 0.34 |
| 3500 | explorer | 23 | 22 | 97909 | 1.584 | 1.015 | 0.569 | 2.606 | -2.037 | -0.591 | 0.22 | 0.68 |
| 3500 | author | 95 | 50 | 175137 | 2.367 | 2.489 | -0.123 | 5.257 | -5.380 | -4.645 | -0.02 | 0.18 |
| 3500 | reproducer | 61 | 37 | 90995 | 1.068 | 1.112 | -0.044 | 3.824 | -3.868 | -2.397 | -0.01 | 0.35 |
| 4000 | all | 180 | 88 | 332440 | 4.631 | 4.036 | 0.595 | 9.407 | -8.812 | -6.513 | 0.06 | 0.28 |
| 4000 | explorer | 23 | 17 | 88647 | 1.454 | 0.845 | 0.609 | 2.032 | -1.423 | -0.352 | 0.30 | 0.65 |
| 4000 | author | 95 | 45 | 166328 | 2.265 | 2.339 | -0.073 | 4.771 | -4.844 | -4.281 | -0.02 | 0.16 |
| 4000 | reproducer | 61 | 25 | 70540 | 0.817 | 0.814 | 0.002 | 2.552 | -2.550 | -1.885 | 0.00 | 0.28 |
| 5000 | all | 180 | 42 | 217633 | 3.205 | 2.274 | 0.930 | 4.573 | -3.642 | -2.462 | 0.20 | 0.31 |
| 5000 | explorer | 23 | 7 | 63879 | 1.119 | 0.475 | 0.645 | 0.998 | -0.353 | 0.078 | 0.65 | 0.43 |
| 5000 | author | 95 | 25 | 115088 | 1.610 | 1.407 | 0.203 | 2.791 | -2.589 | -2.093 | 0.07 | 0.24 |
| 5000 | reproducer | 61 | 9 | 31741 | 0.381 | 0.355 | 0.026 | 0.731 | -0.705 | -0.451 | 0.04 | 0.44 |
| 6000 | all | 180 | 21 | 145008 | 2.313 | 1.290 | 1.024 | 2.411 | -1.387 | -0.967 | 0.42 | 0.24 |
| 6000 | explorer | 23 | 5 | 56842 | 1.033 | 0.383 | 0.651 | 0.654 | -0.003 | 0.084 | 1.00 | 0.20 |
| 6000 | author | 95 | 13 | 72626 | 1.091 | 0.774 | 0.317 | 1.547 | -1.230 | -0.975 | 0.20 | 0.23 |
| 6000 | reproducer | 61 | 2 | 8615 | 0.094 | 0.095 | -0.001 | 0.158 | -0.159 | -0.081 | -0.01 | 0.50 |

Total USD the 180 hand-backs cost the PI over their lives: 12.37 (748097 characters of worker text; PI frame about 1276 characters each).
