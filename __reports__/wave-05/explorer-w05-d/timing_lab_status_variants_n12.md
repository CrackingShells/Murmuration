| case | n | wall median ms | wall p90 ms | cpu median ms | rc != 0 |
|:--|--:|--:|--:|--:|--:|
| v0 k=306 | 12 | 830.4 | 863.7 | 664.5 | 0 |
| v1 k=306 | 12 | 705.8 | 720.2 | 631.3 | 0 |
| v2 k=306 | 12 | 684.0 | 709.6 | 604.0 | 0 |
| v3 k=306 | 12 | 306.4 | 311.4 | 227.6 | 0 |
| 3 x git worktree list (/usr/bin/git) | 12 | 163.8 | 205.8 | 45.0 | 0 |
| 1 x git worktree list (/usr/bin/git) | 12 | 78.1 | 89.1 | 17.4 | 0 |
| python3 -c 'import lab_status' only (imports) | 12 | 84.1 | 107.2 | 37.4 | 0 |
| python3 -S -I -c pass | 12 | 60.3 | 71.1 | 11.5 | 0 |
