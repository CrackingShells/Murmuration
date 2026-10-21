python3 = /Users/hacker/miniforge3/bin/python3 | reps 40 
| start form | median ms | p10 | p90 |
|:--|--:|--:|--:|
| sh -c | 152.0 | 121.0 | 301.4 |
| bash -c | 107.4 | 80.9 | 184.2 |
| zsh -c | 107.5 | 80.4 | 198.3 |
| exec (no shell) | 53.7 | 40.1 | 90.3 |
| sh -c ':' (shell alone) | 80.6 | 64.9 | 185.6 |
| bash -c ':' (shell alone) | 40.3 | 27.2 | 69.9 |
