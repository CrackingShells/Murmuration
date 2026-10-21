### permission decision ms, median over reps (calls 2..n only; n = reps)

| cell | all calls median | p90 | true | pwd | ls | cat /etc/hosts | echo hi | git status | python3 -c pass | date |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| auto+bashshell | 521 | 924 | -1 | 406 | 514 | 536 | 676 | 558 | 612 | 517 |
| auto+exactallow | 2 | 369 | -1 | 1 | 2 | 559 | 1 | 2 | 1 | 1 |
| auto | 609 | 728 | -1 | 648 | 716 | 593 | 621 | 551 | 603 | 588 |

### first Bash call, snapshot, tokens, USD per run

| cell | runs | first call run s median | min | snapshot ok/runs | snapshot s median | cache_read median | cache_create median | output median | USD mean | api-turns median |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| auto+bashshell | 4 | 0.28 | 0.18 | 4/4 | 0.22 | 412868 | 15607 | 919 | 0.00772 | 10 |
| auto+exactallow | 4 | 6.11 | 5.42 | 4/4 | 6.06 | 413732 | 15664 | 993 | 0.00777 | 10 |
| auto | 4 | 5.76 | 4.92 | 4/4 | 5.70 | 412959 | 15616 | 958 | 0.00775 | 10 |
