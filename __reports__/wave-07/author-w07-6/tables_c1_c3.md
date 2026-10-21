| session | req | gap s | input | cache read | write 5m | write 1h | ctx | read/prev ctx | tools |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|:--|
| A1 | 0 |  | 2 | 3636 | 8308 | 0 | 11946 |  | Bash |
| A1 | 1 | 2.3 | 2 | 11944 | 332 | 0 | 12278 | 1.000 | Bash |
| A1 | 2 | 2.0 | 2 | 12276 | 113 | 0 | 12391 | 1.000 | Bash |
| A1 | 3 | 1.7 | 2 | 12389 | 122 | 0 | 12513 | 1.000 | Bash |
| A1 | 4 | 1.5 | 2 | 12511 | 106 | 0 | 12619 | 1.000 |  |
| A1 | 5 | 1.3 | 4 | 12617 | 53 | 0 | 12674 | 1.000 | SubagentHandback |
| B1 | 0 |  | 2 | 0 | 0 | 11948 | 11950 |  | Bash |
| B1 | 1 | 2.0 | 2 | 11948 | 0 | 293 | 12243 | 1.000 | Bash |
| B1 | 2 | 1.9 | 2 | 12241 | 0 | 112 | 12355 | 1.000 | Bash |
| B1 | 3 | 1.7 | 2 | 12353 | 0 | 120 | 12475 | 1.000 | Bash |
| B1 | 4 | 1.6 | 2 | 12473 | 0 | 106 | 12581 | 1.000 |  |
| B1 | 5 | 1.2 | 4 | 12579 | 0 | 53 | 12636 | 1.000 | SubagentHandback |
| A2 | 0 |  | 2 | 10539 | 1404 | 0 | 11945 |  | Bash |
| A2 | 1 | 2.6 | 2 | 11943 | 644 | 0 | 12589 | 1.000 | Bash |
| A2 | 2 | 2.0 | 2 | 12587 | 113 | 0 | 12702 | 1.000 | Bash |
| A2 | 3 | 2.2 | 2 | 12700 | 120 | 0 | 12822 | 1.000 | Bash |
| A2 | 4 | 2.0 | 2 | 12820 | 106 | 0 | 12928 | 1.000 | SubagentHandback |
| B2 | 0 |  | 2 | 10539 | 0 | 1406 | 11947 |  | Bash |
| B2 | 1 | 2.1 | 2 | 11945 | 0 | 537 | 12484 | 1.000 | Bash |
| B2 | 2 | 1.5 | 2 | 12482 | 0 | 113 | 12597 | 1.000 | Bash |
| B2 | 3 | 1.6 | 2 | 12595 | 0 | 120 | 12717 | 1.000 | Bash |
| B2 | 4 | 1.6 | 2 | 12715 | 0 | 105 | 12822 | 1.000 |  |
| B2 | 5 | 1.3 | 4 | 12820 | 0 | 53 | 12877 | 1.000 | SubagentHandback |
| A3 | 0 |  | 2 | 5202 | 6795 | 0 | 11999 |  | Bash |
| A3 | 1 | 2.3 | 2 | 11997 | 756 | 0 | 12755 | 1.000 | Bash |
| A3 | 2 | 422.3 | 2 | 5202 | 7719 | 0 | 12923 | 0.408 | Bash |
| A3 | 3 | 3.8 | 2 | 12921 | 122 | 0 | 13045 | 1.000 |  |
| A3 | 4 | 1.6 | 4 | 13043 | 53 | 0 | 13100 | 1.000 | SubagentHandback |
| B3 | 0 |  | 2 | 0 | 0 | 12000 | 12002 |  | Bash |
| B3 | 1 | 2.7 | 2 | 12000 | 0 | 333 | 12335 | 1.000 | Bash |
| B3 | 2 | 422.4 | 2 | 12333 | 0 | 130 | 12465 | 1.000 | Bash |
| B3 | 3 | 1.9 | 2 | 12463 | 0 | 96 | 12561 | 1.000 |  |
| B3 | 4 | 1.6 | 4 | 12559 | 0 | 53 | 12616 | 1.000 | SubagentHandback |

| session | tool names | tools hash | system hash | system chars | request 0 ctx | requests | hand-back |
|:--|:--|--:|--:|--:|--:|--:|:--|
| A1 | Read,Bash,Write,Edit,ToolSearch,SubagentHandback | 2444391396 | 3110601320 | 4783 | 11946 | 6 | Cache test complete. No claim filed and no file written, as instructed. The four Bash calls ran in order, one per turn:  |
| B1 | Read,Bash,Write,Edit,ToolSearch,SubagentHandback | 2444391396 | 3110601320 | 4783 | 11950 | 6 | done |
| A2 | Read,Bash,Write,Edit,ToolSearch,SubagentHandback | 2444391396 | 3110601320 | 4783 | 11945 | 5 | done |
| B2 | Read,Bash,Write,Edit,ToolSearch,SubagentHandback | 2444391396 | 3110601320 | 4783 | 11947 | 6 | done  Cache test, no claim filed, no file written. The four Bash calls ran in order, one per turn: 1. pwd -> /private/tm |
| A3 | Read,Bash,Write,Edit,ToolSearch,SubagentHandback | 2444391396 | 3110601320 | 4783 | 11999 | 5 | Cache test finished. No claim filed, no file written, as the brief asked.  Call 1, `pwd`: /private/tmp/murmuration-w07/a |
| B3 | Read,Bash,Write,Edit,ToolSearch,SubagentHandback | 2444391396 | 3110601320 | 4783 | 12002 | 5 | done  Cache test, as briefed: no claim filed, no file written. 1. pwd: /private/tmp/murmuration-w07/author-w07-6/work/B3 |
