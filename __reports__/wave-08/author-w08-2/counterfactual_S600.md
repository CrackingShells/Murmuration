# Counterfactual price of the gate on past hand-backs (ESTIMATE)

Hand-backs priced: 180 of 183 (PI cost known); kept size after the gate S = 600 characters (ASSUMPTION; the live test replaces it).

Formulas, per fired hand-back i (hb_i > N):
- PI saving = u_i x (hb_i - S): u_i = USD of the PI-context item / its characters (write once + later reads + re-writes, explorer-w08-d's model).
- worker cost w_i = the worker's own cache-read price x its context at the hand-back (one extra request) + (S + (hb_i - S)) x 0.4 tokens x USD 10 per M (the second message and a Write of all that was dropped, an upper bound: much of it is already in the file); with `low`, only S x 0.4 x 10 / 1e6 (the detail is already in the file).
- CF1 net = saving - w_i. PI keeps the short message only.
- opening cost o_i = u_i x section_i + the PI's next-request cache-read USD + USD 0.003 (a tool call's output). section_i = the worker's own report Result section (explorer), the claim's headline above `method:` (author) or the verdict and reason lines (reproducer); with `full`, the whole claim head and verdict section (median of the role when the worker's file is not in the lab).
- CF2-all net = CF1 net - o_i for every fired hand-back. CF2-new net = CF1 net - o_i for those after which the PI did not open the named file in the past (pi_read = 0); the others are assumed to be opened anyway.
- break-even p* = sum of (saving - w_i) / sum of o_i over the fired hand-backs: the share of them the PI may newly open before the net turns negative.

| N | role | hand-backs | fired | PI chars dropped | PI saving USD | worker cost USD | CF1 net | CF2-all net | CF2-new net | p* | share the PI opened in the past |
|--|--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1000 | all | 180 | 178 | 639926 | 8.301 | 6.635 | 1.667 | 18.949 | -17.282 | -11.514 | 0.09 | 0.29 |
| 1000 | explorer | 23 | 23 | 131553 | 2.085 | 1.041 | 1.045 | 2.749 | -1.704 | -0.115 | 0.38 | 0.70 |
| 1000 | author | 95 | 93 | 309336 | 3.996 | 3.963 | 0.034 | 10.098 | -10.064 | -8.166 | 0.00 | 0.17 |
| 1000 | reproducer | 61 | 61 | 190712 | 2.106 | 1.594 | 0.512 | 6.050 | -5.537 | -3.257 | 0.08 | 0.33 |
| 1500 | all | 180 | 169 | 633990 | 8.233 | 6.421 | 1.812 | 18.099 | -16.287 | -10.710 | 0.10 | 0.30 |
| 1500 | explorer | 23 | 23 | 131553 | 2.085 | 1.041 | 1.045 | 2.749 | -1.704 | -0.115 | 0.38 | 0.70 |
| 1500 | author | 95 | 86 | 304586 | 3.941 | 3.774 | 0.167 | 9.377 | -9.210 | -7.503 | 0.02 | 0.17 |
| 1500 | reproducer | 61 | 59 | 189526 | 2.093 | 1.568 | 0.525 | 5.921 | -5.396 | -3.116 | 0.09 | 0.34 |
| 2000 | all | 180 | 150 | 612612 | 8.011 | 5.838 | 2.173 | 16.325 | -14.152 | -8.870 | 0.13 | 0.33 |
| 2000 | explorer | 23 | 23 | 131553 | 2.085 | 1.041 | 1.045 | 2.749 | -1.704 | -0.115 | 0.38 | 0.70 |
| 2000 | author | 95 | 70 | 286857 | 3.755 | 3.238 | 0.517 | 7.791 | -7.274 | -5.862 | 0.07 | 0.19 |
| 2000 | reproducer | 61 | 56 | 185877 | 2.057 | 1.522 | 0.535 | 5.732 | -5.197 | -2.917 | 0.09 | 0.36 |
| 2500 | all | 180 | 139 | 594800 | 7.820 | 5.497 | 2.323 | 15.040 | -12.717 | -7.908 | 0.15 | 0.33 |
| 2500 | explorer | 23 | 23 | 131553 | 2.085 | 1.041 | 1.045 | 2.749 | -1.704 | -0.115 | 0.38 | 0.70 |
| 2500 | author | 95 | 64 | 277365 | 3.641 | 3.005 | 0.636 | 7.098 | -6.462 | -5.358 | 0.09 | 0.17 |
| 2500 | reproducer | 61 | 51 | 177557 | 1.981 | 1.414 | 0.566 | 5.141 | -4.574 | -2.459 | 0.11 | 0.37 |
| 3000 | all | 180 | 124 | 562083 | 7.447 | 5.026 | 2.421 | 13.242 | -10.822 | -6.425 | 0.18 | 0.35 |
| 3000 | explorer | 23 | 23 | 131553 | 2.085 | 1.041 | 1.045 | 2.749 | -1.704 | -0.115 | 0.38 | 0.70 |
| 3000 | author | 95 | 54 | 255529 | 3.391 | 2.642 | 0.750 | 5.753 | -5.003 | -4.269 | 0.13 | 0.17 |
| 3000 | reproducer | 61 | 46 | 166676 | 1.857 | 1.307 | 0.550 | 4.688 | -4.138 | -2.065 | 0.12 | 0.39 |
| 3500 | all | 180 | 110 | 524966 | 7.093 | 4.655 | 2.438 | 11.739 | -9.301 | -5.649 | 0.21 | 0.34 |
| 3500 | explorer | 23 | 22 | 128709 | 2.027 | 1.015 | 1.012 | 2.606 | -1.594 | -0.148 | 0.39 | 0.68 |
| 3500 | author | 95 | 50 | 245137 | 3.278 | 2.489 | 0.789 | 5.257 | -4.468 | -3.734 | 0.15 | 0.18 |
| 3500 | reproducer | 61 | 37 | 142795 | 1.674 | 1.112 | 0.561 | 3.824 | -3.262 | -1.791 | 0.15 | 0.35 |
| 4000 | all | 180 | 88 | 455640 | 6.227 | 4.036 | 2.191 | 9.407 | -7.216 | -4.917 | 0.23 | 0.28 |
| 4000 | explorer | 23 | 17 | 112447 | 1.798 | 0.845 | 0.953 | 2.032 | -1.079 | -0.008 | 0.47 | 0.65 |
| 4000 | author | 95 | 45 | 229328 | 3.097 | 2.339 | 0.759 | 4.771 | -4.012 | -3.449 | 0.16 | 0.16 |
| 4000 | reproducer | 61 | 25 | 105540 | 1.218 | 0.814 | 0.403 | 2.552 | -2.149 | -1.484 | 0.16 | 0.28 |
| 5000 | all | 180 | 42 | 276433 | 4.008 | 2.274 | 1.734 | 4.573 | -2.839 | -1.658 | 0.38 | 0.31 |
| 5000 | explorer | 23 | 7 | 73679 | 1.276 | 0.475 | 0.801 | 0.998 | -0.196 | 0.235 | 0.80 | 0.43 |
| 5000 | author | 95 | 25 | 150088 | 2.085 | 1.407 | 0.678 | 2.791 | -2.113 | -1.618 | 0.24 | 0.24 |
| 5000 | reproducer | 61 | 9 | 44341 | 0.533 | 0.355 | 0.178 | 0.731 | -0.554 | -0.300 | 0.24 | 0.44 |
| 6000 | all | 180 | 21 | 174408 | 2.753 | 1.290 | 1.464 | 2.411 | -0.947 | -0.527 | 0.61 | 0.24 |
| 6000 | explorer | 23 | 5 | 63842 | 1.155 | 0.383 | 0.772 | 0.654 | 0.118 | 0.206 | 1.18 | 0.20 |
| 6000 | author | 95 | 13 | 90826 | 1.360 | 0.774 | 0.586 | 1.547 | -0.961 | -0.706 | 0.38 | 0.23 |
| 6000 | reproducer | 61 | 2 | 11415 | 0.125 | 0.095 | 0.029 | 0.158 | -0.128 | -0.051 | 0.19 | 0.50 |

Total USD the 180 hand-backs cost the PI over their lives: 12.37 (748097 characters of worker text; PI frame about 1276 characters each).
