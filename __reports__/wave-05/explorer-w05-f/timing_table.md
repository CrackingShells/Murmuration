# Timing table (explorer-w05-f). Debug logs and raw rows with session ids stay in /private/tmp/murmuration-w05/explorer-w05-f/.

## Run 1: eight trivial commands, 8 cells x 5 reps, 3 jobs in parallel (rows_main.jsonl)
### permission decision ms, median over reps (calls 2..n only; n = reps)

| cell | all calls median | p90 | true | pwd | ls | cat /etc/hosts | echo hi | git status | python3 -c pass | date |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| auto | 747 | 987 | -1 | 740 | 614 | 886 | 679 | 960 | 761 | 747 |
| auto+mcp | 837 | 1086 | -1 | 827 | 1018 | 861 | 529 | 818 | 896 | 946 |
| bypass | 2 | 3 | -1 | 2 | 2 | 3 | 1 | 3 | 2 | 2 |
| auto+nohooks | 1101 | 1386 | -1 | 1101 | 1097 | 1210 | 1201 | 1157 | 1048 | 1200 |
| auto+blanketBash | 671 | 1234 | -1 | 563 | 671 | 641 | 647 | 773 | 934 | 1012 |
| auto+exactallow | 2 | 599 | -1 | 2 | 2 | 622 | 2 | 2 | 1 | 2 |
| auto+globallow | 2 | 965 | -1 | 2 | 2 | 1261 | 2 | 2 | 695 | 2 |
| auto+bashshell | 733 | 1141 | -1 | 577 | 723 | 837 | 999 | 689 | 842 | 905 |

### first Bash call, snapshot, tokens, USD per run

| cell | runs | first call run s median | min | snapshot ok/runs | snapshot s median | cache_read median | cache_create median | output median | USD mean | api-turns median |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| auto | 5 | 10.11 | 7.18 | 1/5 | 10.01 | 412956 | 15616 | 1043 | 0.00776 | 10 |
| auto+mcp | 5 | 9.80 | 8.96 | 3/5 | 9.70 | 517467 | 27816 | 1119 | 0.01128 | 10 |
| bypass | 5 | 10.10 | 7.44 | 2/5 | 10.00 | 412951 | 15614 | 950 | 0.00776 | 10 |
| auto+nohooks | 5 | 8.50 | 6.36 | 3/5 | 8.41 | 406976 | 14962 | 918 | 0.00754 | 10 |
| auto+blanketBash | 5 | 8.11 | 6.53 | 4/5 | 8.06 | 412976 | 15621 | 951 | 0.00775 | 10 |
| auto+exactallow | 5 | 8.00 | 6.57 | 3/5 | 7.93 | 413550 | 15688 | 1046 | 0.00780 | 10 |
| auto+globallow | 5 | 10.09 | 6.74 | 2/5 | 10.00 | 412866 | 15610 | 939 | 0.00772 | 10 |
| auto+bashshell | 5 | 0.49 | 0.32 | 5/5 | 0.41 | 412864 | 15599 | 923 | 0.00770 | 10 |

## Run 2: lab-shaped commands, 6 cells x 5 reps, 3 jobs (rows_lab.jsonl)
### permission decision ms, median over reps (calls 2..n only; n = reps)

| cell | all calls median | p90 | python3 -I ./hello.py a | python3 ./hello.py b | git log --oneline -3 | ls -la | wc -l hello.py | sleep 1 | grep -c print hello.py | command -v python3; echo $SHELL |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| bypass | 2 | 2 | -1 | 2 | 2 | 2 | 1 | 1 | 2 | 2 |
| auto | 448 | 632 | -1 | 475 | 438 | 481 | 362 | 472 | 448 | 431 |
| auto+bashshell | 296 | 488 | -1 | 267 | 291 | 296 | 360 | 248 | 241 | 313 |
| auto+pywild | 486 | 679 | -1 | 463 | 461 | 403 | 512 | 486 | 540 | 433 |
| auto+labrules | 2 | 479 | -1 | 497 | 2 | 2 | 2 | 1 | 1 | 475 |
| auto+flagrules | 2 | 491 | -1 | 492 | 2 | 2 | 2 | 1 | 2 | 369 |

### first Bash call, snapshot, tokens, USD per run

| cell | runs | first call run s median | min | snapshot ok/runs | snapshot s median | cache_read median | cache_create median | output median | USD mean | api-turns median |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| bypass | 5 | 10.38 | 10.28 | 0/5 | 10.00 | 415461 | 15789 | 1141 | 0.00791 | 10 |
| auto | 5 | 10.44 | 9.41 | 1/5 | 10.00 | 415894 | 15895 | 1085 | 0.00804 | 10 |
| auto+bashshell | 5 | 0.61 | 0.48 | 5/5 | 0.44 | 415416 | 15823 | 1218 | 0.00800 | 10 |
| auto+pywild | 5 | 10.35 | 10.29 | 0/5 | 10.00 | 415741 | 15826 | 1161 | 0.00792 | 10 |
| auto+labrules | 5 | 10.36 | 10.31 | 0/5 | 10.00 | 415720 | 15809 | 1098 | 0.00785 | 10 |
| auto+flagrules | 5 | 10.34 | 10.27 | 0/5 | 10.00 | 415537 | 15783 | 1127 | 0.00787 | 10 |

## Run 3: serial (1 job), 3 cells x 4 reps, first Bash call and snapshot at idle (rows_serial.jsonl)
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
