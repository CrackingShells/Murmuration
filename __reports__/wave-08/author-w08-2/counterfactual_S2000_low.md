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
| 1000 | all | 180 | 178 | 402612 | 5.445 | 5.072 | 0.373 | 18.949 | -18.576 | -12.808 | 0.02 | 0.29 |
| 1000 | explorer | 23 | 23 | 99353 | 1.614 | 0.643 | 0.971 | 2.749 | -1.779 | -0.190 | 0.35 | 0.70 |
| 1000 | author | 95 | 93 | 188857 | 2.525 | 3.246 | -0.721 | 10.098 | -10.819 | -8.920 | -0.07 | 0.17 |
| 1000 | reproducer | 61 | 61 | 107477 | 1.212 | 1.173 | 0.039 | 6.050 | -6.011 | -3.730 | 0.01 | 0.33 |
| 1500 | all | 180 | 169 | 402612 | 5.445 | 4.831 | 0.614 | 18.099 | -17.485 | -11.909 | 0.03 | 0.30 |
| 1500 | explorer | 23 | 23 | 99353 | 1.614 | 0.643 | 0.971 | 2.749 | -1.779 | -0.190 | 0.35 | 0.70 |
| 1500 | author | 95 | 86 | 188857 | 2.525 | 3.038 | -0.512 | 9.377 | -9.889 | -8.182 | -0.05 | 0.17 |
| 1500 | reproducer | 61 | 59 | 107477 | 1.212 | 1.141 | 0.071 | 5.921 | -5.850 | -3.569 | 0.01 | 0.34 |
| 2000 | all | 180 | 150 | 402612 | 5.445 | 4.227 | 1.218 | 16.325 | -15.107 | -9.825 | 0.07 | 0.33 |
| 2000 | explorer | 23 | 23 | 99353 | 1.614 | 0.643 | 0.971 | 2.749 | -1.779 | -0.190 | 0.35 | 0.70 |
| 2000 | author | 95 | 70 | 188857 | 2.525 | 2.482 | 0.043 | 7.791 | -7.748 | -6.336 | 0.01 | 0.19 |
| 2000 | reproducer | 61 | 56 | 107477 | 1.212 | 1.092 | 0.120 | 5.732 | -5.612 | -3.332 | 0.02 | 0.36 |
| 2500 | all | 180 | 139 | 400200 | 5.418 | 3.896 | 1.521 | 15.040 | -13.519 | -8.710 | 0.10 | 0.33 |
| 2500 | explorer | 23 | 23 | 99353 | 1.614 | 0.643 | 0.971 | 2.749 | -1.779 | -0.190 | 0.35 | 0.70 |
| 2500 | author | 95 | 64 | 187765 | 2.510 | 2.254 | 0.256 | 7.098 | -6.842 | -5.737 | 0.04 | 0.17 |
| 2500 | reproducer | 61 | 51 | 106157 | 1.199 | 0.989 | 0.210 | 5.141 | -4.931 | -2.815 | 0.04 | 0.37 |
| 3000 | all | 180 | 124 | 388483 | 5.283 | 3.472 | 1.811 | 13.242 | -11.432 | -7.036 | 0.14 | 0.35 |
| 3000 | explorer | 23 | 23 | 99353 | 1.614 | 0.643 | 0.971 | 2.749 | -1.779 | -0.190 | 0.35 | 0.70 |
| 3000 | author | 95 | 54 | 179929 | 2.419 | 1.922 | 0.497 | 5.753 | -5.255 | -4.521 | 0.09 | 0.17 |
| 3000 | reproducer | 61 | 46 | 102276 | 1.155 | 0.897 | 0.258 | 4.688 | -4.430 | -2.358 | 0.05 | 0.39 |
| 3500 | all | 180 | 110 | 370966 | 5.114 | 3.171 | 1.943 | 11.739 | -9.796 | -6.144 | 0.17 | 0.34 |
| 3500 | explorer | 23 | 22 | 97909 | 1.584 | 0.624 | 0.961 | 2.606 | -1.646 | -0.200 | 0.37 | 0.68 |
| 3500 | author | 95 | 50 | 175137 | 2.367 | 1.789 | 0.578 | 5.257 | -4.679 | -3.944 | 0.11 | 0.18 |
| 3500 | reproducer | 61 | 37 | 90995 | 1.068 | 0.748 | 0.320 | 3.824 | -3.504 | -2.033 | 0.08 | 0.35 |
| 4000 | all | 180 | 88 | 332440 | 4.631 | 2.706 | 1.925 | 9.407 | -7.482 | -5.183 | 0.20 | 0.28 |
| 4000 | explorer | 23 | 17 | 88647 | 1.454 | 0.491 | 0.963 | 2.032 | -1.068 | 0.003 | 0.47 | 0.65 |
| 4000 | author | 95 | 45 | 166328 | 2.265 | 1.673 | 0.592 | 4.771 | -4.179 | -3.616 | 0.12 | 0.16 |
| 4000 | reproducer | 61 | 25 | 70540 | 0.817 | 0.532 | 0.285 | 2.552 | -2.267 | -1.602 | 0.11 | 0.28 |
| 5000 | all | 180 | 42 | 217633 | 3.205 | 1.404 | 1.801 | 4.573 | -2.772 | -1.591 | 0.39 | 0.31 |
| 5000 | explorer | 23 | 7 | 63879 | 1.119 | 0.219 | 0.900 | 0.998 | -0.098 | 0.334 | 0.90 | 0.43 |
| 5000 | author | 95 | 25 | 115088 | 1.610 | 0.947 | 0.663 | 2.791 | -2.128 | -1.633 | 0.24 | 0.24 |
| 5000 | reproducer | 61 | 9 | 31741 | 0.381 | 0.228 | 0.153 | 0.731 | -0.578 | -0.324 | 0.21 | 0.44 |
| 6000 | all | 180 | 21 | 145008 | 2.313 | 0.710 | 1.604 | 2.411 | -0.807 | -0.387 | 0.67 | 0.24 |
| 6000 | explorer | 23 | 5 | 56842 | 1.033 | 0.155 | 0.878 | 0.654 | 0.224 | 0.312 | 1.34 | 0.20 |
| 6000 | author | 95 | 13 | 72626 | 1.091 | 0.484 | 0.607 | 1.547 | -0.939 | -0.684 | 0.39 | 0.23 |
| 6000 | reproducer | 61 | 2 | 8615 | 0.094 | 0.061 | 0.033 | 0.158 | -0.125 | -0.047 | 0.21 | 0.50 |

Total USD the 180 hand-backs cost the PI over their lives: 12.37 (748097 characters of worker text; PI frame about 1276 characters each).
