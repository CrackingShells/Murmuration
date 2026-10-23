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
| 1000 | all | 180 | 178 | 533344 | 7.024 | 6.635 | 0.389 | 18.949 | -18.560 | -12.792 | 0.02 | 0.29 |
| 1000 | explorer | 23 | 23 | 117753 | 1.883 | 1.041 | 0.843 | 2.749 | -1.906 | -0.318 | 0.31 | 0.70 |
| 1000 | author | 95 | 93 | 253711 | 3.322 | 3.963 | -0.641 | 10.098 | -10.739 | -8.840 | -0.06 | 0.17 |
| 1000 | reproducer | 61 | 61 | 154155 | 1.713 | 1.594 | 0.119 | 6.050 | -5.930 | -3.650 | 0.02 | 0.33 |
| 1500 | all | 180 | 169 | 532590 | 7.015 | 6.421 | 0.594 | 18.099 | -17.505 | -11.928 | 0.03 | 0.30 |
| 1500 | explorer | 23 | 23 | 117753 | 1.883 | 1.041 | 0.843 | 2.749 | -1.906 | -0.318 | 0.31 | 0.70 |
| 1500 | author | 95 | 86 | 252986 | 3.313 | 3.774 | -0.461 | 9.377 | -9.838 | -8.131 | -0.05 | 0.17 |
| 1500 | reproducer | 61 | 59 | 154126 | 1.713 | 1.568 | 0.145 | 5.921 | -5.776 | -3.496 | 0.02 | 0.34 |
| 2000 | all | 180 | 150 | 522612 | 6.911 | 5.838 | 1.074 | 16.325 | -15.251 | -9.969 | 0.07 | 0.33 |
| 2000 | explorer | 23 | 23 | 117753 | 1.883 | 1.041 | 0.843 | 2.749 | -1.906 | -0.318 | 0.31 | 0.70 |
| 2000 | author | 95 | 70 | 244857 | 3.228 | 3.238 | -0.010 | 7.791 | -7.801 | -6.389 | -0.00 | 0.19 |
| 2000 | reproducer | 61 | 56 | 152277 | 1.695 | 1.522 | 0.173 | 5.732 | -5.559 | -3.279 | 0.03 | 0.36 |
| 2500 | all | 180 | 139 | 511400 | 6.791 | 5.497 | 1.294 | 15.040 | -13.747 | -8.938 | 0.09 | 0.33 |
| 2500 | explorer | 23 | 23 | 117753 | 1.883 | 1.041 | 0.843 | 2.749 | -1.906 | -0.318 | 0.31 | 0.70 |
| 2500 | author | 95 | 64 | 238965 | 3.156 | 3.005 | 0.151 | 7.098 | -6.947 | -5.842 | 0.02 | 0.17 |
| 2500 | reproducer | 61 | 51 | 146957 | 1.646 | 1.414 | 0.232 | 5.141 | -4.909 | -2.793 | 0.05 | 0.37 |
| 3000 | all | 180 | 124 | 487683 | 6.519 | 5.026 | 1.493 | 13.242 | -11.749 | -7.353 | 0.11 | 0.35 |
| 3000 | explorer | 23 | 23 | 117753 | 1.883 | 1.041 | 0.843 | 2.749 | -1.906 | -0.318 | 0.31 | 0.70 |
| 3000 | author | 95 | 54 | 223129 | 2.975 | 2.642 | 0.333 | 5.753 | -5.420 | -4.685 | 0.06 | 0.17 |
| 3000 | reproducer | 61 | 46 | 139076 | 1.556 | 1.307 | 0.249 | 4.688 | -4.439 | -2.366 | 0.05 | 0.39 |
| 3500 | all | 180 | 110 | 458966 | 6.245 | 4.655 | 1.590 | 11.739 | -10.149 | -6.497 | 0.14 | 0.34 |
| 3500 | explorer | 23 | 22 | 115509 | 1.838 | 1.015 | 0.822 | 2.606 | -1.784 | -0.338 | 0.32 | 0.68 |
| 3500 | author | 95 | 50 | 215137 | 2.887 | 2.489 | 0.398 | 5.257 | -4.859 | -4.124 | 0.08 | 0.18 |
| 3500 | reproducer | 61 | 37 | 120595 | 1.414 | 1.112 | 0.302 | 3.824 | -3.522 | -2.050 | 0.08 | 0.35 |
| 4000 | all | 180 | 88 | 402840 | 5.543 | 4.036 | 1.507 | 9.407 | -7.900 | -5.601 | 0.16 | 0.28 |
| 4000 | explorer | 23 | 17 | 102247 | 1.651 | 0.845 | 0.805 | 2.032 | -1.226 | -0.155 | 0.40 | 0.65 |
| 4000 | author | 95 | 45 | 202328 | 2.741 | 2.339 | 0.402 | 4.771 | -4.369 | -3.806 | 0.08 | 0.16 |
| 4000 | reproducer | 61 | 25 | 90540 | 1.046 | 0.814 | 0.231 | 2.552 | -2.321 | -1.656 | 0.09 | 0.28 |
| 5000 | all | 180 | 42 | 251233 | 3.664 | 2.274 | 1.389 | 4.573 | -3.183 | -2.003 | 0.30 | 0.31 |
| 5000 | explorer | 23 | 7 | 69479 | 1.209 | 0.475 | 0.734 | 0.998 | -0.264 | 0.168 | 0.74 | 0.43 |
| 5000 | author | 95 | 25 | 135088 | 1.882 | 1.407 | 0.474 | 2.791 | -2.317 | -1.822 | 0.17 | 0.24 |
| 5000 | reproducer | 61 | 9 | 38941 | 0.468 | 0.355 | 0.113 | 0.731 | -0.619 | -0.365 | 0.15 | 0.44 |
| 6000 | all | 180 | 21 | 161808 | 2.565 | 1.290 | 1.275 | 2.411 | -1.136 | -0.715 | 0.53 | 0.24 |
| 6000 | explorer | 23 | 5 | 60842 | 1.103 | 0.383 | 0.720 | 0.654 | 0.066 | 0.154 | 1.10 | 0.20 |
| 6000 | author | 95 | 13 | 83026 | 1.245 | 0.774 | 0.470 | 1.547 | -1.076 | -0.821 | 0.30 | 0.23 |
| 6000 | reproducer | 61 | 2 | 10215 | 0.112 | 0.095 | 0.016 | 0.158 | -0.142 | -0.064 | 0.10 | 0.50 |

Total USD the 180 hand-backs cost the PI over their lives: 12.37 (748097 characters of worker text; PI frame about 1276 characters each).
