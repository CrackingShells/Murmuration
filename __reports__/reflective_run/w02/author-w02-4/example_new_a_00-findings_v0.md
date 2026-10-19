---
type: findings
wave: wave-01
author: explorer-w01-a
date: 2026-10-19
version: v0
decision-required: none
---

# Worst-fitting row of data/measurements.csv: findings (v0)

## Result
Row (x=9, y=31.5) fits worst: CHECKED residual +10.83, studentised 3.16, Cook's D 0.725, n=12 [source: __reports__/wave-01/explorer-w01-a/probe_out.txt]. Dropping it moves the OLS line from y=2.238x+0.523 to y=2.021x+0.899 (slope -9.7%), and residual RMSE falls from about 3.8 to 0.213 [source: probe_out.txt]. __design__/framing.md is an unfilled template, so no project notation applies; x, y are the CSV column names.

## Table
| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Full fit (12 rows) | slope 2.2383, intercept 0.5230 | CHECKED | probe_out.txt |
| Fit without x=9 | slope 2.0213, intercept 0.8991, RMSE 0.213 | CHECKED | probe_out.txt |
| x=9 residual / studentised / Cook | 10.833 / 3.16 / 0.725 | CHECKED | probe_out.txt |
| Next-largest Cook (x=12) | 0.118; dropping it gives slope 2.3644 | CHECKED | probe_out.txt |
| Other 10 rows' residuals (full fit) | |r| from 0.14 to 2.31, a trend, not noise | CHECKED | probe_out.txt |

## Worst-fitting case
Worst: (9, 31.5), roughly 10 above the line, while neighbours 8 and 10 give 17.17 and 21.1. Typical: (4, 8.87), residual -0.61. Counter-point: in the full fit the other rows have a systematic residual pattern (positive at x=1,2, negative from x=3 on, growing to -2.3 at x=12). That pattern is produced by the outlier pulling the line up. Without x=9 the points are near-linear with RMSE 0.21. OLS only, not robust fits.

## Not covered
No robust fit (Theil-Sen, Huber), no check of whether 31.5 is a typo (e.g. 19.5 or 21.5 would fit the line, CONJECTURE), no uncertainty on the slopes.

## Steering questions
- [now] Is x=9 a known bad measurement? If so, should it be excluded or corrected before later waves?

## Pointers
- /private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/author-w02-4/lab_new_a/__reports__/wave-01/explorer-w01-a/probe.py (run: `python3 -I probe.py data/measurements.csv`, numpy)
- same folder, probe_out.txt: its output
