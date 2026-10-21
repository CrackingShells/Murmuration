## model request time (request sent to last assistant block; first-block time = request sent to first block), requests that end in a tool call

| set | requests | model_s median | p90 | time to first block median | of which requests with no thinking block (n, median) | client gap after a tool result, median / p90 (gaps under 5 s) |
|:--|--:|--:|--:|--:|--:|--:|
| workers w5 | 745 | 6.13 | 18.16 | 3.63 | 134, 2.20 | 0.34 / 0.57 |
| workers w6 | 1166 | 5.65 | 18.41 | 3.65 | 268, 2.84 | 0.30 / 0.64 |
| PI w5 | 118 | 9.42 | 28.54 | 5.75 | 14, 4.52 | 0.35 / 0.88 |
| PI w6 | 175 | 9.28 | 25.88 | 5.18 | 48, 4.52 | 0.37 / 0.75 |

fixed cost of one more request used below: floor = median time to first block of workers' requests with no thinking (2.71 s) + median client gap (0.32 s) = 3.03 s.

## where a worker's wall time goes (sums over workers, seconds)

`first` = model time of the first request; `model` = request sent to last assistant block (waves 5-6); `gap` = last tool result to the next request being sent (client side: hooks, reminders, request build); `pre` = model + gap together (wave 4 has no request timestamps); `tool` = last assistant block to last tool result, phases up to 120 s; `long` = tool phases over 120 s; `wait` = idle until a message arrived: after a turn that ended without a tool call, or a gap over 5 s after a tool result with a message arriving (a worker waiting on a peer); `resid` = wall minus the rest.

| wave | workers | wall | first | model | gap | pre (model+gap) | tool <=120 s | long tool | wait | resid |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| w4 | 15 | 20003 | 10 | 0 | 0 | 6197 | 4110 | 6447 | 3237 | 1 |
| w5 | 15 | 18805 | 44 | 6834 | 286 | 0 | 5291 | 4471 | 1880 | 0 |
| w6 | 17 | 37631 | 53 | 10424 | 461 | 0 | 6038 | 9934 | 10721 | 0 |
| all | 47 | 76439 | 107 | 17259 | 746 | 6197 | 15440 | 20851 | 15838 | 1 |

same, as shares of wall (waves 5-6 pooled; wave 4's pre split by the waves 5-6 model/gap ratio is not attempted):

| part | seconds | share of wall |
|:--|--:|--:|
| first | 97 | 0.2% |
| model | 17259 | 30.6% |
| gap | 746 | 1.3% |
| tool | 11329 | 20.1% |
| long | 14405 | 25.5% |
| wait | 12601 | 22.3% |
| model + first (all model request time) | 17355 | 30.8% |

same without idle waits and long tool phases (the loop proper, 29431 s): model + first 59.0%, client gap 2.5%, tool phases <=120 s 38.5%.

same, all three waves, wave 4 counted with its model+gap together as `pre` (39750 s without waits and long phases): model+gap 61.2%, tool 38.8%.

## tool-phase latency per call (block complete to its result record), workers, single-call turns only unless noted

| class | n single | median s | p90 s | p99 s | n all calls | median s (all) |
|:--|--:|--:|--:|--:|--:|--:|
| Bash[classifier] | 2131 | 1.54 | 30.76 | 266.4 | 2348 | 1.58 |
| Read | 9 | 0.16 | 0.80 | 0.8 | 108 | 0.17 |
| Write | 56 | 0.18 | 0.70 | 1.2 | 104 | 0.73 |
| SubagentHandback | 87 | 1.09 | 1.56 | 13.1 | 90 | 1.11 |
| Bash[mode/rule/none] | 47 | 0.01 | 1.62 | 46.3 | 57 | 0.19 |
| ToolSearch | 25 | 0.15 | 0.22 | 0.3 | 52 | 0.16 |
| SendMessage | 31 | 0.99 | 1.25 | 1.4 | 48 | 1.13 |
| Edit | 7 | 0.18 | 1.09 | 1.1 | 21 | 1.09 |
| mcp__plugin_colgrep-mcp_colgrep__search | 8 | 2.18 | 7.58 | 7.6 | 18 | 4.33 |
| mcp__context7__query-docs | 5 | 3.84 | 4.09 | 4.1 | 14 | 4.16 |

trivial single Bash calls (first word ls/cat/head/tail/wc/git/grep/sed/echo/date/pwd/stat/test/cd, result under 3000 chars): decided by classifier: n = 1159, median 1.49 s, p10 1.05, p90 9.57; decided by mode/rule/none: n = 17, median 1.03 s, p10 0.20, p90 31.02.

permission decisions on workers' tool results (label / decision/source/reasonType: count):

| wave | decision/source/reasonType | n |
|:--|:--|--:|
| w4 | accept/config/None | 15 |
| w4 | accept/config/classifier | 688 |
| w4 | accept/config/mode | 54 |
| w4 | accept/config/other | 1 |
| w4 | reject/config/safetyCheck | 1 |
| w5 | accept/config/None | 16 |
| w5 | accept/config/classifier | 714 |
| w5 | accept/config/mode | 64 |
| w5 | accept/config/other | 1 |
| w6 | accept/config/None | 21 |
| w6 | accept/config/classifier | 1144 |
| w6 | accept/config/mode | 109 |
| w6 | accept/config/other | 17 |
| w6 | reject/config/safetyCheck | 1 |
| w6 | reject/config/subcommandResults | 2 |
| w6 | reject/hook/hook | 2 |
| w6 | reject/user_reject/rule | 1 |

### do several calls in one message overlap? tool phase of turns with k calls, workers

| calls in message | n turns | median tool_s | p90 | median of (slowest result - fastest result) |
|--:|--:|--:|--:|--:|
| 1 | 2414 | 1.47 | 22.54 | - |
| 2 | 181 | 1.63 | 7.57 | 0.70 |
| 3 | 21 | 0.36 | 2.33 | 0.20 |
| 4 | 3 | 1.28 | 2.32 | 1.20 |

## tool calls per assistant message (one message = one API request)

| set | requests | 0 calls | 1 call | 2 calls | 3-4 | 5+ | calls | calls per request | share of requests with 1 call among those with >=1 | share of calls sent in a multi-call message |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| workers w4 | 716 | 2 | 670 | 34 | 9 | 1 | 770 | 1.08 | 93.8% | 13.0% |
| workers w5 | 747 | 2 | 698 | 36 | 9 | 2 | 810 | 1.08 | 93.7% | 13.8% |
| workers w6 | 1170 | 4 | 1046 | 111 | 6 | 3 | 1303 | 1.11 | 89.7% | 19.7% |
| workers all | 2633 | 8 | 2414 | 181 | 24 | 6 | 2883 | 1.09 | 92.0% | 16.3% |
| PI w4 | 114 | 25 | 75 | 11 | 3 | 0 | 107 | 0.94 | 84.3% | 29.9% |
| PI w5 | 153 | 35 | 96 | 18 | 3 | 1 | 148 | 0.97 | 81.4% | 35.1% |
| PI w6 | 223 | 48 | 157 | 15 | 3 | 0 | 197 | 0.88 | 89.7% | 20.3% |

calls by tool (workers): Bash 2405 (9% in multi-call messages), Read 108 (92% in multi-call messages), Write 104 (46% in multi-call messages), SubagentHandback 90 (3% in multi-call messages), ToolSearch 52 (52% in multi-call messages), SendMessage 48 (35% in multi-call messages), Edit 21 (67% in multi-call messages), mcp__plugin_colgrep-mcp_colgrep__search 18 (56% in multi-call messages), WebFetch 15 (100% in multi-call messages), mcp__context7__query-docs 14 (64% in multi-call messages), mcp__context7__resolve-library-id 4 (0% in multi-call messages), Monitor 3 (0% in multi-call messages)

## requests that independent calls could have saved (ESTIMATE; heuristic dependency test)

Rule: consecutive turns merge into one message when the absorbed turn's calls are all read-only (Read, Glob, Grep, ToolSearch, colgrep, Bash with only read-only words and no redirect) like the batch before them, or all file Write/Edit to distinct paths; no call of the absorbed turn contains a path-like token that first appeared in a tool result of the batch; no call a near-copy (word overlap 0.6 or more) of the previous turn's call (a refinement), none needing the schema of a deferred tool that a ToolSearch of the batch loads; no error result in the batch; no message arrived in between; at most 8 calls per message. `strict` also needs each absorbed call to name at least one path-like token and none unseen anywhere before. Fixed cost of a request: see the line above.

| wave | mode | workers' requests | requests saved | share | seconds floor | seconds mid | seconds high | + tool overlap | USD (cache reads of the saved requests) | USD (+ their output tokens) | worker wall (s) | mid share of wall |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| w4 | loose | 716 | 19 | 2.7% | 57 | 57 | 77 | 20 | 0.16 | 0.16 | 20003 | 0.3% |
| w5 | loose | 747 | 23 | 3.1% | 70 | 114 | 116 | 29 | 0.12 | 0.13 | 18805 | 0.6% |
| w6 | loose | 1170 | 25 | 2.1% | 76 | 296 | 319 | 36 | 0.28 | 0.30 | 37631 | 0.8% |
| all | loose | 2633 | 67 | 2.5% | 203 | 467 | 512 | 85 | 0.56 | 0.59 | 76439 | 0.6% |
| w4 | strict | 716 | 8 | 1.1% | 24 | 24 | 32 | 9 | 0.08 | 0.08 | 20003 | 0.1% |
| w5 | strict | 747 | 12 | 1.6% | 36 | 50 | 48 | 17 | 0.06 | 0.06 | 18805 | 0.3% |
| w6 | strict | 1170 | 12 | 1.0% | 36 | 121 | 125 | 19 | 0.18 | 0.18 | 37631 | 0.3% |
| all | strict | 2633 | 32 | 1.2% | 97 | 196 | 206 | 45 | 0.32 | 0.32 | 76439 | 0.3% |

workers' list-price spend in the same transcripts: USD 65.75; formula for the USD columns: sum over saved requests of (cache_read_tokens x read price + uncached input tokens x input price) / 1e6 (output tokens are kept in the merged message for the `+output` column they are saved). Prices from scripts/lab_status.py PRICES at the model of the request.

most common (previous turn's calls -> absorbed turn's calls), loose:

| previous | absorbed | n |
|:--|:--|--:|
| Bash:cd | Bash:cd | 39 |
| mcp__context7__query-docs | mcp__context7__query-docs | 3 |
| Bash:sed | Bash:sed | 3 |
| Bash:git | Bash:grep | 2 |
| Bash:D=/private/tmp/murmu | Bash:cat | 1 |
| Bash:cat | Bash:for | 1 |
| Bash:D=/private/tmp/murmu | Bash:D=/private/tmp/murmu | 1 |
| Bash:D=/private/tmp/murmu | Bash:cd | 1 |
| Read | Read | 1 |
| Bash:ls | Bash:ls | 1 |
| Bash:cd | Read | 1 |
| Read | Bash:cat | 1 |

## per worker task

| set | workers | requests per worker (median / p90 / max) | calls per worker (median / p90 / max) | wall s (median / p90 / max) | USD (median / max) |
|:--|--:|:--|:--|:--|:--|
| w4 | 15 | 33 / 116 / 122 | 35 / 121 / 125 | 643 / 4599 / 4805 | 0.43 / 5.90 |
| w5 | 15 | 39 / 68 / 136 | 44 / 74 / 143 | 784 / 3932 / 4026 | 0.77 / 5.05 |
| w6 | 17 | 51 / 174 / 241 | 55 / 219 / 269 | 910 / 6365 / 7849 | 1.00 / 9.97 |
| all | 47 | 39 / 122 / 241 | 43 / 125 / 269 | 819 / 4746 / 7849 | 0.63 / 9.97 |

by agent type (all waves): claude-code-guide: n=1, median requests 9, median wall 256 s, median calls/request 2.44; murmuration:author: n=13, median requests 107, median wall 4026 s, median calls/request 1.07; murmuration:explorer: n=9, median requests 45, median wall 784 s, median calls/request 1.09; murmuration:reproducer: n=24, median requests 32, median wall 669 s, median calls/request 1.08

### every worker (seconds; saved = requests merged, loose / strict)

| wave | name | type | requests | calls | calls/req | wall | USD | model+first | gap | pre | tool | long tool | wait | saved loose | saved strict |
|:--|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| w4 | author-w04-1 | author | 36 | 41 | 1.14 | 997 | 0.70 | 2 | 0 | 336 | 341 | 0 | 318 | 1 | 0 |
| w4 | author-w04-2 | author | 107 | 115 | 1.07 | 4599 | 3.62 | 1 | 0 | 1042 | 321 | 2893 | 342 | 2 | 2 |
| w4 | author-w04-3 | author | 116 | 121 | 1.04 | 3994 | 3.20 | 1 | 0 | 1327 | 625 | 1780 | 260 | 5 | 3 |
| w4 | author-w04-4 | author | 122 | 125 | 1.02 | 4805 | 5.90 | 1 | 0 | 1254 | 571 | 1231 | 1746 | 2 | 0 |
| w4 | author-w04-6 | author | 24 | 29 | 1.21 | 344 | 0.26 | 1 | 0 | 128 | 49 | 0 | 166 | 0 | 0 |
| w4 | reproducer-w04-1 | reproducer | 29 | 31 | 1.07 | 402 | 0.30 | 0 | 0 | 173 | 229 | 0 | 0 | 1 | 1 |
| w4 | reproducer-w04-10 | reproducer | 18 | 20 | 1.11 | 128 | 0.23 | 1 | 0 | 110 | 17 | 0 | 0 | 0 | 0 |
| w4 | reproducer-w04-2 | reproducer | 31 | 33 | 1.06 | 643 | 0.33 | 1 | 0 | 150 | 492 | 0 | 0 | 1 | 0 |
| w4 | reproducer-w04-3 | reproducer | 33 | 37 | 1.12 | 696 | 0.43 | 1 | 0 | 248 | 175 | 273 | 0 | 0 | 0 |
| w4 | reproducer-w04-4 | reproducer | 33 | 35 | 1.06 | 607 | 0.45 | 0 | 0 | 184 | 301 | 122 | 0 | 2 | 0 |
| w4 | reproducer-w04-5 | reproducer | 51 | 55 | 1.08 | 1121 | 0.75 | 1 | 0 | 441 | 530 | 148 | 0 | 0 | 0 |
| w4 | reproducer-w04-6 | reproducer | 26 | 28 | 1.08 | 222 | 0.25 | 0 | 0 | 134 | 88 | 0 | 0 | 0 | 0 |
| w4 | reproducer-w04-7 | reproducer | 21 | 24 | 1.14 | 219 | 0.30 | 1 | 0 | 172 | 47 | 0 | 0 | 2 | 0 |
| w4 | reproducer-w04-8 | reproducer | 40 | 45 | 1.12 | 888 | 0.79 | 0 | 0 | 251 | 232 | 0 | 404 | 2 | 2 |
| w4 | reproducer-w04-9 | reproducer | 29 | 31 | 1.07 | 339 | 0.36 | 0 | 0 | 248 | 91 | 0 | 0 | 1 | 0 |
| w5 | author-w05-1 | author | 68 | 74 | 1.09 | 4026 | 1.69 | 670 | 28 | 0 | 734 | 1733 | 860 | 0 | 0 |
| w5 | author-w05-2 | author | 60 | 64 | 1.07 | 1836 | 1.01 | 643 | 26 | 0 | 433 | 390 | 343 | 0 | 0 |
| w5 | author-w05-3 | author | 136 | 143 | 1.05 | 3932 | 5.05 | 1420 | 57 | 0 | 1361 | 479 | 616 | 2 | 1 |
| w5 | explorer-w05-a | explorer | 39 | 44 | 1.13 | 544 | 0.91 | 465 | 13 | 0 | 66 | 0 | 0 | 1 | 0 |
| w5 | explorer-w05-b | explorer | 39 | 43 | 1.10 | 649 | 0.77 | 525 | 12 | 0 | 113 | 0 | 0 | 0 | 0 |
| w5 | explorer-w05-c | explorer | 55 | 56 | 1.02 | 784 | 1.37 | 678 | 19 | 0 | 86 | 0 | 0 | 0 | 0 |
| w5 | explorer-w05-d | explorer | 67 | 73 | 1.09 | 1267 | 1.15 | 555 | 21 | 0 | 570 | 121 | 0 | 0 | 0 |
| w5 | explorer-w05-e | explorer | 45 | 48 | 1.07 | 527 | 0.52 | 367 | 14 | 0 | 146 | 0 | 0 | 1 | 1 |
| w5 | explorer-w05-f | explorer | 36 | 42 | 1.17 | 1592 | 0.96 | 297 | 16 | 0 | 193 | 1086 | 0 | 1 | 1 |
| w5 | reproducer-w05-1 | reproducer | 29 | 35 | 1.21 | 880 | 0.40 | 180 | 10 | 0 | 176 | 514 | 0 | 6 | 1 |
| w5 | reproducer-w05-3 | reproducer | 32 | 35 | 1.09 | 436 | 0.35 | 172 | 18 | 0 | 246 | 0 | 0 | 5 | 3 |
| w5 | reproducer-w05-4 | reproducer | 51 | 52 | 1.02 | 916 | 0.63 | 301 | 18 | 0 | 450 | 147 | 0 | 4 | 4 |
| w5 | reproducer-w05-5 | reproducer | 33 | 35 | 1.06 | 755 | 0.41 | 238 | 11 | 0 | 507 | 0 | 0 | 0 | 0 |
| w5 | reproducer-w05-6 | reproducer | 32 | 35 | 1.09 | 367 | 0.34 | 195 | 14 | 0 | 112 | 0 | 46 | 2 | 0 |
| w5 | reproducer-w05-8 | reproducer | 25 | 31 | 1.24 | 292 | 0.29 | 173 | 9 | 0 | 96 | 0 | 15 | 1 | 1 |
| w6 | author-w06-3 | author | 87 | 91 | 1.05 | 6365 | 2.70 | 787 | 25 | 0 | 308 | 964 | 4281 | 2 | 1 |
| w6 | author-w06-4 | author | 126 | 128 | 1.02 | 4746 | 4.03 | 1262 | 47 | 0 | 913 | 1999 | 524 | 1 | 0 |
| w6 | author-w06-5 | author | 241 | 269 | 1.12 | 7849 | 9.97 | 2540 | 111 | 0 | 1036 | 2424 | 1738 | 3 | 2 |
| w6 | author-w06-6 | author | 174 | 219 | 1.26 | 4853 | 5.50 | 1383 | 75 | 0 | 746 | 1369 | 1281 | 4 | 3 |
| w6 | author-w06-7 | author | 21 | 22 | 1.05 | 388 | 0.26 | 176 | 5 | 0 | 206 | 0 | 0 | 0 | 0 |
| w6 | explorer-w06-a | explorer | 40 | 42 | 1.05 | 1761 | 0.58 | 338 | 13 | 0 | 303 | 1107 | 0 | 0 | 0 |
| w6 | explorer-w06-b | explorer | 52 | 59 | 1.13 | 1529 | 1.00 | 413 | 19 | 0 | 319 | 779 | 0 | 4 | 2 |
| w6 | explorer-w06-c | explorer | 51 | 55 | 1.08 | 618 | 1.01 | 522 | 19 | 0 | 77 | 0 | 0 | 0 | 0 |
| w6 | guide-w06-perm | claude-code-guide | 9 | 22 | 2.44 | 256 | 0.18 | 169 | 2 | 0 | 85 | 0 | 0 | 0 | 0 |
| w6 | reproducer-w06-1 | reproducer | 28 | 32 | 1.14 | 260 | 0.35 | 198 | 9 | 0 | 52 | 0 | 0 | 0 | 0 |
| w6 | reproducer-w06-2 | reproducer | 27 | 29 | 1.07 | 346 | 0.37 | 231 | 11 | 0 | 104 | 0 | 0 | 1 | 0 |
| w6 | reproducer-w06-3 | reproducer | 40 | 45 | 1.12 | 819 | 0.52 | 236 | 13 | 0 | 186 | 251 | 132 | 1 | 0 |
| w6 | reproducer-w06-4 | reproducer | 36 | 40 | 1.11 | 839 | 0.43 | 258 | 17 | 0 | 225 | 339 | 0 | 3 | 0 |
| w6 | reproducer-w06-5 | reproducer | 53 | 56 | 1.06 | 775 | 1.03 | 482 | 20 | 0 | 273 | 0 | 0 | 1 | 0 |
| w6 | reproducer-w06-6 | reproducer | 67 | 71 | 1.06 | 3323 | 1.25 | 475 | 32 | 0 | 729 | 701 | 1387 | 3 | 2 |
| w6 | reproducer-w06-7 | reproducer | 83 | 88 | 1.06 | 1994 | 2.21 | 738 | 35 | 0 | 265 | 0 | 956 | 2 | 2 |
| w6 | reproducer-w06-8 | reproducer | 35 | 35 | 1.00 | 910 | 0.62 | 269 | 8 | 0 | 210 | 0 | 423 | 0 | 0 |

## cache re-writes after gaps over 300 s (workers' 5-minute cache)

| wave | requests after a gap over 300 s | misses (read under half of previous context) | tokens not read | USD over a read (tokens x (cache-write-5m - read price)) | longest gap s | share of worker spend |
|:--|--:|--:|--:|--:|--:|--:|
| w4 | 12 | 11 | 1821292 | 4.37 | 1005 | 24.5% |
| w5 | 4 | 4 | 666099 | 1.60 | 723 | 10.1% |
| w6 | 9 | 8 | 1849391 | 4.44 | 4187 | 13.9% |
| all | 25 | 23 | 4336782 | 10.41 | 4187 | 15.8% |

(gap = time between two requests of one worker, waves 5-6 from request timestamps; wave 4 has none, so its gap is the time between the previous message's last block and this message's first block)

gaps behind misses (all waves): author-w04-1 w4 gap 319 s, tool phase before it 2 s; author-w04-2 w4 gap 341 s, tool phase before it 337 s; author-w04-2 w4 gap 391 s, tool phase before it 386 s; author-w04-2 w4 gap 319 s, tool phase before it 313 s; author-w04-2 w4 gap 546 s, tool phase before it 541 s; author-w04-2 w4 gap 345 s, tool phase before it 343 s; author-w04-3 w4 gap 604 s, tool phase before it 601 s; author-w04-4 w4 gap 606 s, tool phase before it 602 s; author-w04-4 w4 gap 1005 s, tool phase before it 1 s; author-w04-4 w4 gap 534 s, tool phase before it - s; reproducer-w04-8 w4 gap 405 s, tool phase before it 1 s; author-w05-3 w5 gap 460 s, tool phase before it 1 s

## tool outputs that every later request re-reads

calibration: growth of context (cache read + write + input) from one request to the next, minus the assistant's output tokens, against the result's characters, single-call turns, n = 2344: tokens = 1179 + 0.418 x chars (so 2.39 chars per token).

| size class (chars) | results | estimated tokens | USD of re-reads by later requests (tokens x later requests x read price) | share of workers' cache-read USD (USD 34.59) |
|:--|--:|--:|--:|--:|
| 0-2000 | 2028 | 447538 | 1.99 | 5.7% |
| 2000-5000 | 466 | 609005 | 2.80 | 8.1% |
| 5000-20000 | 361 | 1416435 | 7.45 | 21.5% |
| 20000-+ | 28 | 394927 | 2.85 | 8.2% |

five costliest re-reads: w6 author-w06-4 Read 61427 chars, 122 later requests, USD 0.313; w4 author-w04-4 Read 61427 chars, 119 later requests, USD 0.306; w6 author-w06-6 Read 32259 chars, 172 later requests, USD 0.232; w6 author-w06-3 Read 61427 chars, 83 later requests, USD 0.213; w5 author-w05-3 Read 31889 chars, 127 later requests, USD 0.169

## errors, denials, hook time visible in the records

| wave | tool results with is_error | calls rejected (decision reject) | requests with no assistant message | PreToolUse hook timeouts | SubagentStart hook records (sum ms / max ms) | PostToolBatch records (n, sum ms) |
|:--|--:|--:|--:|--:|--:|--:|
| w4 | 31 | 1 | 0 | 0 | 36264 / 2190 | 10, 1639 |
| w5 | 30 | 0 | 2 | 0 | 25703 / 1085 | 11, 1528 |
| w6 | 100 | 6 | 0 | 0 | 28942 / 988 | 23, 6709 |

workers: 2633 requests, 2883 tool calls. Hook durations in the records cover only SubagentStart and PostToolBatch (and one cancelled PreToolUse); PreToolUse/PostToolUse successes carry no record in these transcripts.

requests that follow a turn with at least one error result (a retry or a reaction): w4 31, w5 30, w6 99

## by agent type (all waves, workers): shares of wall

| type | workers | wall s | requests | model+first | gap | pre (w4 only) | tool <=120 s | long tool | wait | requests saved (loose) |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| claude-code-guide | 1 | 256 | 9 | 66.1% | 0.9% | 0.0% | 33.0% | 0.0% | 0.0% | 0 |
| author | 13 | 48734 | 1318 | 18.2% | 0.8% | 8.4% | 15.7% | 31.3% | 25.6% | 22 |
| explorer | 9 | 9272 | 424 | 44.9% | 1.6% | 0.0% | 20.2% | 33.4% | 0.0% | 7 |
| reproducer | 24 | 18177 | 882 | 22.8% | 1.2% | 11.6% | 32.1% | 13.7% | 18.5% | 38 |

## where the tool phases go (workers, single-call turns, by tool and first word of a Bash command)

| call | n | sum s (all phases) | sum s in phases over 120 s | n over 120 s | median s | share of all tool-phase seconds |
|:--|--:|--:|--:|--:|--:|--:|
| Bash timeout | 75 | 10878 | 8893 | 40 | 138.50 | 31.5% |
| Bash cd | 1163 | 8802 | 3086 | 14 | 1.45 | 25.5% |
| Bash S=/private/tmp/murmu | 76 | 4298 | 3275 | 11 | 2.62 | 12.5% |
| Bash python3 | 220 | 2075 | 648 | 4 | 1.82 | 6.0% |
| Bash until | 12 | 1780 | 1233 | 4 | 105.77 | 5.2% |
| Bash W=/private/tmp/murmu | 31 | 1306 | 950 | 3 | 6.72 | 3.8% |
| Bash cat | 109 | 949 | 122 | 1 | 1.69 | 2.8% |
| Bash B=/private/tmp/murmu | 22 | 674 | 390 | 2 | 10.43 | 2.0% |
| Bash D=/private/tmp/murmu | 14 | 673 | 651 | 4 | 1.58 | 2.0% |
| Bash mkdir | 29 | 601 | 0 | 0 | 2.65 | 1.7% |
| Bash git | 78 | 514 | 242 | 1 | 1.46 | 1.5% |
| Bash kill | 8 | 217 | 195 | 1 | 3.44 | 0.6% |
| Bash sed | 87 | 207 | 0 | 0 | 1.35 | 0.6% |
| Bash export | 10 | 167 | 0 | 0 | 1.70 | 0.5% |

Bash single-call latency by wave (classifier-decided, result under 3000 chars, first word in the trivial set): w4 n=355 median 1.30 s p90 12.24 s; w5 n=331 median 1.78 s p90 17.06 s; w6 n=473 median 1.45 s p90 7.72 s

Read single-call latency (no classifier context in the record): median 0.16 s, n 9; ToolSearch 0.15 s, Write 0.18 s.

classifier-decided Bash calls in the workers' records: 2348 (w4 633, w5 661, w6 1054). At the earlier measured 0.45-0.75 s each that is 1057-1761 s; at the trivial-call median above minus the Read median it is about 3111 s. Worker wall over all waves: 76439 s.

## calls already batched inside one Bash command; thinking time; what the errors were

Bash calls by number of statements (split on && ; newline): 1 statement 111, 2 491, 3-5 1105, 6+ 698; share with 2 or more: 95.4% of 2405 Bash calls; mean statements 4.72. (A statement chain is one tool call, one classifier call, one request.)

thinking: 1510 of 1917 worker requests (waves 5-6) carry a thinking block with a recorded duration; thinkingDurationMs sums to 7074 s against 17355 s of model time (40.8%); wave 6 alone: 4285 s of 10477 s (40.9%).

worker tool results with is_error, by wave, tool and first 45 characters (top 14):

| wave | tool | start of the error text | n |
|:--|:--|:--|--:|
| w6 | Bash | This agent is isolated in the worktree /Users | 33 |
| w6 | Bash | Exit code 1 Traceback (most recent call last) | 7 |
| w4 | Bash | <tool_use_error>Blocked: sleep 45 followed by | 6 |
| w5 | Bash | <tool_use_error>Blocked: sleep 45 followed by | 5 |
| w6 | Bash | Exit code 1 (eval):1: = not found | 4 |
| w5 | Bash | <tool_use_error>Blocked: sleep 100 followed b | 3 |
| w4 | Bash | Exit code 1 (eval):1: = not found | 2 |
| w4 | mcp__plugin_colgrep-mcp_colgrep__search | Error executing tool search: [PATH_NOT_FOUND] | 2 |
| w4 | Bash | <tool_use_error>Blocked: sleep 90 followed by | 2 |
| w5 | Bash | <tool_use_error>Blocked: sleep 60 followed by | 2 |
| w5 | Monitor | <tool_use_error>Error: No such tool available | 2 |
| w6 | Bash | <tool_use_error>Blocked: sleep 60 followed by | 2 |
| w6 | Bash | Permission to use Bash with command cd /priva | 2 |
| w4 | Bash | Exit code 1 (eval):9: = not found | 1 |

requests that directly follow a turn with an error result (retry or reaction), and their cost: w4: 31 of 716 requests (4.3%), USD 0.35 of 17.88 (2.0%), 137 s of model+gap time; w5: 30 of 747 requests (4.0%), USD 0.43 of 15.85 (2.7%), 146 s of model+gap time; w6: 99 of 1170 requests (8.5%), USD 2.17 of 32.03 (6.8%), 609 s of model+gap time

cache misses after a gap over 300 s: 23, USD 10.65 over a read. Of them 9 follow a single long tool call that filled at least 80% of the gap; if each such wait had been cut into tool calls of 270 s (one extra request per 270 s: previous context at the read price + 150 output tokens), the saving would be USD 2.70 (ESTIMATE; assumes the waiting command can be split, and that the model's extra requests are as small as 150 output tokens, which the Bash timeout of 270 s lets it be).

## PI main thread, same split (seconds)

| wave | requests | calls | 0 / 1 / 2+ calls | wall | first | model | gap | pre | tool <=120 s | long tool | wait (idle until next message) | USD |
|:--|--:|--:|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| w4 | 114 | 107 | 25 / 75 / 14 | 5270 | 3 | 0 | 0 | 952 | 146 | 0 | 4059 | 10.50 |
| w5 | 153 | 148 | 35 / 96 / 22 | 17848 | 8 | 1786 | 53 | 0 | 460 | 0 | 15542 | 18.08 |
| w6 | 223 | 197 | 48 / 157 / 18 | 25754 | 4 | 2446 | 381 | 0 | 380 | 0 | 22543 | 22.06 |

PI batching (same rule, PI turns): w4 loose: 4 of 114 requests, seconds floor/mid/high 12/12/23, USD 0.11 (reads) to 0.14 (+output); w5 loose: 1 of 153 requests, seconds floor/mid/high 3/11/13, USD 0.04 (reads) to 0.06 (+output); w6 loose: 10 of 223 requests, seconds floor/mid/high 30/53/59, USD 0.26 (reads) to 0.36 (+output); w4 strict: 0 of 114 requests, seconds floor/mid/high 0/0/0, USD 0.00 (reads) to 0.00 (+output); w5 strict: 0 of 153 requests, seconds floor/mid/high 0/0/0, USD 0.00 (reads) to 0.00 (+output); w6 strict: 5 of 223 requests, seconds floor/mid/high 15/31/34, USD 0.19 (reads) to 0.24 (+output)

PI tool-phase latency (single-call turns): Bash: median 1.59 s, n 241; SendMessage: median 1.08 s, n 27; Agent: median 1.18 s, n 19; Write: median 0.17 s, n 8; Read: median 0.16 s, n 4

