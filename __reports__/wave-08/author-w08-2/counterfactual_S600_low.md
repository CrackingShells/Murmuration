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
| 1000 | all | 180 | 178 | 639926 | 8.301 | 4.075 | 4.226 | 18.949 | -14.722 | -8.955 | 0.22 | 0.29 |
| 1000 | explorer | 23 | 23 | 131553 | 2.085 | 0.514 | 1.571 | 2.749 | -1.178 | 0.411 | 0.57 | 0.70 |
| 1000 | author | 95 | 93 | 309336 | 3.996 | 2.725 | 1.271 | 10.098 | -8.827 | -6.928 | 0.13 | 0.17 |
| 1000 | reproducer | 61 | 61 | 190712 | 2.106 | 0.831 | 1.275 | 6.050 | -4.775 | -2.494 | 0.21 | 0.33 |
| 1500 | all | 180 | 169 | 633990 | 8.233 | 3.885 | 4.348 | 18.099 | -13.751 | -8.174 | 0.24 | 0.30 |
| 1500 | explorer | 23 | 23 | 131553 | 2.085 | 0.514 | 1.571 | 2.749 | -1.178 | 0.411 | 0.57 | 0.70 |
| 1500 | author | 95 | 86 | 304586 | 3.941 | 2.556 | 1.385 | 9.377 | -7.992 | -6.285 | 0.15 | 0.17 |
| 1500 | reproducer | 61 | 59 | 189526 | 2.093 | 0.810 | 1.283 | 5.921 | -4.638 | -2.358 | 0.22 | 0.34 |
| 2000 | all | 180 | 150 | 612612 | 8.011 | 3.387 | 4.624 | 16.325 | -11.701 | -6.419 | 0.28 | 0.33 |
| 2000 | explorer | 23 | 23 | 131553 | 2.085 | 0.514 | 1.571 | 2.749 | -1.178 | 0.411 | 0.57 | 0.70 |
| 2000 | author | 95 | 70 | 286857 | 3.755 | 2.090 | 1.665 | 7.791 | -6.127 | -4.714 | 0.21 | 0.19 |
| 2000 | reproducer | 61 | 56 | 185877 | 2.057 | 0.778 | 1.279 | 5.732 | -4.454 | -2.173 | 0.22 | 0.36 |
| 2500 | all | 180 | 139 | 594800 | 7.820 | 3.118 | 4.702 | 15.040 | -10.338 | -5.529 | 0.31 | 0.33 |
| 2500 | explorer | 23 | 23 | 131553 | 2.085 | 0.514 | 1.571 | 2.749 | -1.178 | 0.411 | 0.57 | 0.70 |
| 2500 | author | 95 | 64 | 277365 | 3.641 | 1.895 | 1.745 | 7.098 | -5.353 | -4.248 | 0.25 | 0.17 |
| 2500 | reproducer | 61 | 51 | 177557 | 1.981 | 0.704 | 1.277 | 5.141 | -3.864 | -1.748 | 0.25 | 0.37 |
| 3000 | all | 180 | 124 | 562083 | 7.447 | 2.778 | 4.669 | 13.242 | -8.573 | -4.177 | 0.35 | 0.35 |
| 3000 | explorer | 23 | 23 | 131553 | 2.085 | 0.514 | 1.571 | 2.749 | -1.178 | 0.411 | 0.57 | 0.70 |
| 3000 | author | 95 | 54 | 255529 | 3.391 | 1.619 | 1.772 | 5.753 | -3.981 | -3.246 | 0.31 | 0.17 |
| 3000 | reproducer | 61 | 46 | 166676 | 1.857 | 0.640 | 1.217 | 4.688 | -3.471 | -1.399 | 0.26 | 0.39 |
| 3500 | all | 180 | 110 | 524966 | 7.093 | 2.555 | 4.538 | 11.739 | -7.201 | -3.549 | 0.39 | 0.34 |
| 3500 | explorer | 23 | 22 | 128709 | 2.027 | 0.500 | 1.527 | 2.606 | -1.079 | 0.367 | 0.59 | 0.68 |
| 3500 | author | 95 | 50 | 245137 | 3.278 | 1.509 | 1.769 | 5.257 | -3.488 | -2.753 | 0.34 | 0.18 |
| 3500 | reproducer | 61 | 37 | 142795 | 1.674 | 0.541 | 1.133 | 3.824 | -2.691 | -1.220 | 0.30 | 0.35 |
| 4000 | all | 180 | 88 | 455640 | 6.227 | 2.214 | 4.013 | 9.407 | -5.393 | -3.094 | 0.43 | 0.28 |
| 4000 | explorer | 23 | 17 | 112447 | 1.798 | 0.396 | 1.403 | 2.032 | -0.629 | 0.442 | 0.69 | 0.65 |
| 4000 | author | 95 | 45 | 229328 | 3.097 | 1.421 | 1.676 | 4.771 | -3.095 | -2.532 | 0.35 | 0.16 |
| 4000 | reproducer | 61 | 25 | 105540 | 1.218 | 0.392 | 0.825 | 2.552 | -1.727 | -1.062 | 0.32 | 0.28 |
| 5000 | all | 180 | 42 | 276433 | 4.008 | 1.168 | 2.839 | 4.573 | -1.733 | -0.553 | 0.62 | 0.31 |
| 5000 | explorer | 23 | 7 | 73679 | 1.276 | 0.180 | 1.096 | 0.998 | 0.098 | 0.530 | 1.10 | 0.43 |
| 5000 | author | 95 | 25 | 150088 | 2.085 | 0.807 | 1.279 | 2.791 | -1.513 | -1.018 | 0.46 | 0.24 |
| 5000 | reproducer | 61 | 9 | 44341 | 0.533 | 0.177 | 0.355 | 0.731 | -0.376 | -0.122 | 0.49 | 0.44 |
| 6000 | all | 180 | 21 | 174408 | 2.753 | 0.592 | 2.161 | 2.411 | -0.250 | 0.171 | 0.90 | 0.24 |
| 6000 | explorer | 23 | 5 | 63842 | 1.155 | 0.127 | 1.028 | 0.654 | 0.374 | 0.461 | 1.57 | 0.20 |
| 6000 | author | 95 | 13 | 90826 | 1.360 | 0.411 | 0.949 | 1.547 | -0.598 | -0.343 | 0.61 | 0.23 |
| 6000 | reproducer | 61 | 2 | 11415 | 0.125 | 0.050 | 0.075 | 0.158 | -0.083 | -0.005 | 0.48 | 0.50 |

Total USD the 180 hand-backs cost the PI over their lives: 12.37 (748097 characters of worker text; PI frame about 1276 characters each).
