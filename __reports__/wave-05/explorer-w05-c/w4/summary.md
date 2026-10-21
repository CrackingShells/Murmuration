## Token-type split of list-price USD (input, cache write, cache read, output)
| group | workers | requests | USD | input | cache write | cache read | output |
|:--|--:|--:|--:|--:|--:|--:|--:|
| author | 5 | 405 | 18.79 | 0% | 37% | 33% | 30% |
| reproducer | 10 | 311 | 6.87 | 0% | 33% | 27% | 40% |
| all | 15 | 716 | 25.66 | 0% | 36% | 31% | 33% |

## Phase shares (category of each request's tool calls; strongest call wins)

### author: 405 requests, USD 18.79, 12064 s
| category | requests | share | USD | share | seconds | share |
|:--|--:|--:|--:|--:|--:|--:|
| handback | 17 | 4% | 0.841 | 4% | 194 | 2% |
| exchange | 9 | 2% | 0.451 | 2% | 111 | 1% |
| deliver | 50 | 12% | 3.622 | 19% | 974 | 8% |
| run | 219 | 54% | 8.929 | 48% | 9300 | 77% |
| write-other | 36 | 9% | 2.026 | 11% | 983 | 8% |
| outside | 7 | 2% | 0.165 | 1% | 81 | 1% |
| doc | 19 | 5% | 0.711 | 4% | 126 | 1% |
| search | 3 | 1% | 0.076 | 0% | 26 | 0% |
| look | 43 | 11% | 1.076 | 6% | 260 | 2% |
| none | 2 | 0% | 0.896 | 5% | 9 | 0% |

### reproducer: 311 requests, USD 6.87, 4849 s
| category | requests | share | USD | share | seconds | share |
|:--|--:|--:|--:|--:|--:|--:|
| handback | 12 | 4% | 0.453 | 7% | 133 | 3% |
| exchange | 11 | 4% | 0.362 | 5% | 124 | 3% |
| deliver | 31 | 10% | 1.311 | 19% | 512 | 11% |
| run | 108 | 35% | 1.752 | 26% | 2845 | 59% |
| write-other | 16 | 5% | 0.640 | 9% | 376 | 8% |
| outside | 23 | 7% | 0.501 | 7% | 188 | 4% |
| doc | 27 | 9% | 0.469 | 7% | 140 | 3% |
| search | 9 | 3% | 0.124 | 2% | 59 | 1% |
| wait | 1 | 0% | 0.012 | 0% | 3 | 0% |
| look | 73 | 23% | 1.243 | 18% | 468 | 10% |

### all: 716 requests, USD 25.66, 16913 s
| category | requests | share | USD | share | seconds | share |
|:--|--:|--:|--:|--:|--:|--:|
| handback | 29 | 4% | 1.293 | 5% | 327 | 2% |
| exchange | 20 | 3% | 0.813 | 3% | 235 | 1% |
| deliver | 81 | 11% | 4.932 | 19% | 1485 | 9% |
| run | 327 | 46% | 10.681 | 42% | 12145 | 72% |
| write-other | 52 | 7% | 2.666 | 10% | 1360 | 8% |
| outside | 30 | 4% | 0.666 | 3% | 269 | 2% |
| doc | 46 | 6% | 1.181 | 5% | 266 | 2% |
| search | 12 | 2% | 0.200 | 1% | 85 | 1% |
| wait | 1 | 0% | 0.012 | 0% | 3 | 0% |
| look | 116 | 16% | 2.319 | 9% | 728 | 4% |
| none | 2 | 0% | 0.896 | 3% | 9 | 0% |

## Orientation prefix (requests before the first run/write/deliver/exchange/handback call, first run only)
| worker | requests | prefix req | share | USD | prefix USD | share | s | prefix s | share |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| author-w04-1 | 36 | 4 | 11% | 1.305 | 0.119 | 9% | 690 | 27 | 4% |
| reproducer-w04-1 | 29 | 2 | 7% | 0.521 | 0.056 | 11% | 406 | 8 | 2% |
| reproducer-w04-3 | 33 | 3 | 9% | 0.704 | 0.082 | 12% | 701 | 16 | 2% |
| author-w04-2 | 107 | 9 | 8% | 5.026 | 0.219 | 4% | 4273 | 84 | 2% |
| reproducer-w04-2 | 31 | 5 | 16% | 0.504 | 0.091 | 18% | 646 | 23 | 3% |
| reproducer-w04-10 | 18 | 2 | 11% | 0.406 | 0.062 | 15% | 131 | 7 | 5% |
| reproducer-w04-6 | 26 | 4 | 15% | 0.429 | 0.065 | 15% | 225 | 11 | 5% |
| reproducer-w04-4 | 33 | 8 | 24% | 0.656 | 0.124 | 19% | 609 | 37 | 6% |
| reproducer-w04-5 | 51 | 3 | 6% | 1.331 | 0.090 | 7% | 1123 | 13 | 1% |
| author-w04-3 | 116 | 4 | 3% | 4.814 | 0.145 | 3% | 3635 | 46 | 1% |
| author-w04-4 | 122 | 8 | 7% | 7.146 | 0.210 | 3% | 3281 | 32 | 1% |
| author-w04-6 | 24 | 3 | 12% | 0.502 | 0.085 | 17% | 185 | 11 | 6% |
| reproducer-w04-7 | 21 | 3 | 14% | 0.531 | 0.081 | 15% | 222 | 12 | 5% |
| reproducer-w04-9 | 29 | 4 | 14% | 0.638 | 0.088 | 14% | 297 | 15 | 5% |
| reproducer-w04-8 | 40 | 7 | 18% | 1.147 | 0.138 | 12% | 489 | 39 | 8% |

## Fixed start cost: first request (cache write of ~13-14k tokens) plus carrying that context for every later request at cache-read price
- author: 0.72 of 18.79 (4%)
- reproducer: 0.67 of 6.87 (10%)

## Cold resumes and in-run cache expiries (ESTIMATE: cache-write tokens x (write - read price); read price would have applied had the cache been warm)
| worker | event | idle or gap s | cache-write tokens | premium USD | requests in run | run USD | run active s |
|:--|:--|--:|--:|--:|--:|--:|--:|
| author-w04-4 | resume 2 (task-notification) | 532 | 337631 | 0.810 | 1 | 0.848 | 4 |
| author-w04-4 | resume 1 (peer) | 997 | 332094 | 0.797 | 3 | 0.946 | 26 |
| author-w04-4 | mid-run request 100 | 602 | 294719 | 0.707 | 1 | - | - |
| author-w04-2 | mid-run request 66 | 343 | 175404 | 0.421 | 1 | - | - |
| author-w04-2 | mid-run request 44 | 541 | 122681 | 0.294 | 1 | - | - |
| author-w04-3 | mid-run request 27 | 601 | 111652 | 0.268 | 1 | - | - |
| author-w04-2 | mid-run request 29 | 313 | 102721 | 0.246 | 1 | - | - |
| author-w04-2 | mid-run request 25 | 386 | 95157 | 0.228 | 1 | - | - |
| author-w04-1 | resume 1 (peer) | 312 | 91751 | 0.220 | 5 | 0.362 | 53 |
| author-w04-2 | mid-run request 21 | 338 | 88854 | 0.213 | 1 | - | - |
| reproducer-w04-8 | resume 1 (coordinator) | 401 | 86495 | 0.208 | 13 | 0.537 | 215 |
sum premium: 4.41 of 25.66 total

## Warm resumes (cache read of the whole context): first-request cost vs the run it opens
| worker | run | origin | idle s | first request USD | run requests | run USD | run active s |
|:--|--:|:--|--:|--:|--:|--:|--:|
| author-w04-2 | 1 | coordinator | 57 | 0.025 | 24 | 1.354 | 823 |
| author-w04-2 | 2 | peer | 134 | 0.030 | 10 | 0.369 | 89 |
| author-w04-2 | 3 | coordinator | 61 | 0.028 | 3 | 0.130 | 27 |
| author-w04-2 | 4 | coordinator | 2 | 0.027 | 10 | 0.430 | 365 |
| author-w04-2 | 5 | peer | 76 | 0.036 | 3 | 0.135 | 30 |
| author-w04-3 | 1 | coordinator | 52 | 0.026 | 35 | 1.576 | 1205 |
| author-w04-3 | 2 | peer | 181 | 0.037 | 3 | 0.125 | 21 |
| author-w04-3 | 3 | coordinator | 22 | 0.031 | 14 | 0.667 | 370 |
| author-w04-3 | 4 | peer | 68 | 0.044 | 4 | 0.197 | 39 |
| author-w04-3 | 5 | coordinator | 38 | 0.051 | 2 | 0.092 | 14 |
| author-w04-6 | 1 | peer | 162 | 0.014 | 5 | 0.123 | 42 |
| reproducer-w04-9 | 1 | coordinator | 45 | 0.013 | 4 | 0.113 | 40 |

## Failed calls (is_error)
- author-w04-1 req 5 Bash `cd /private/tmp/murmuration-w04/author-w04-1/run1; for f in A B; do ec` -> Exit code 1 (eval):1: = not found
- author-w04-1 req 6 Bash `cat > /private/tmp/murmuration-w04/author-w04-1/show.py <<'EOF' import` -> Exit code 1 (eval):9: = not found
- reproducer-w04-1 req 13 Bash `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuratio` -> Exit code 1 {"type":"queue-operation","operation":"enqueue","timestamp":"2026-10-18T03:21:49.868Z","
- reproducer-w04-1 req 26 Bash `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuratio` -> Exit code 1 error: pathspec '__scrupuli__/wave-04-reproducer-w04-1.md' did not match any file(s) kno
- reproducer-w04-3 req 25 Bash `sleep 45; echo waited` -> <tool_use_error>Blocked: sleep 45 followed by: echo waited. To wait for a condition, use Monitor wit
- author-w04-2 req 13 Bash `sleep 200; S=/private/tmp/murmuration-w04/author-w04-2; cat $S/logs/*;` -> <tool_use_error>Blocked: sleep 200 followed by: S=/private/tmp/murmuration-w04/author-w04-2 cat $S/l
- author-w04-2 req 15 Bash `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuratio` -> Exit code 1 {"cell": "pilot-A", "arm": "A", "seed": 20261020, "B": 0.3, "usd_total": 0.3701146700000
- author-w04-2 req 16 Bash `S=/private/tmp/murmuration-w04/author-w04-2; for c in A C; do echo == ` -> Exit code 1 (eval):1: = not found
- author-w04-2 req 36 Bash `sleep 45; python3 - <<'EOF' import glob,collections for c in ['u-c1','` -> <tool_use_error>Blocked: sleep 45 followed by: python3 -. To wait for a condition, use Monitor with 
- author-w04-2 req 54 Bash `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuratio` -> Exit code 1 0 harness.jsonl user_words.md wave-01.md d430819 w04-c2/c3: puzzles of author-w04-2 and 
- reproducer-w04-2 req 7 mcp__plugin_colgrep-mcp_colgrep__search `` -> Error executing tool search: [PATH_NOT_FOUND] Path(s) not found: __instrumenta__ (relative paths are
- reproducer-w04-2 req 22 Bash `sleep 90; echo waited` -> <tool_use_error>Blocked: sleep 90 followed by: echo waited. To wait for a condition, use Monitor wit
- reproducer-w04-2 req 23 Bash `sleep 45; date` -> <tool_use_error>Blocked: sleep 45 followed by: date. To wait for a condition, use Monitor with an un
- reproducer-w04-2 req 25 Monitor `until [ -n "$(find /Users/hacker/Documents/tmp/claude-worktrees/Murmur` -> <tool_use_error>Error: No such tool available: Monitor. Monitor is not among the tools available her
- reproducer-w04-10 req 4 Bash `cd /private/tmp/murmuration-w04/author-w04-3/runs_c; for i in pt1r1 pt` -> Exit code 2 system hook_started None [] None None system hook_started None [] None None 149- 150-Whe
- reproducer-w04-10 req 9 Bash `sleep 45; echo ok` -> <tool_use_error>Blocked: sleep 45 followed by: echo ok. To wait for a condition, use Monitor with an
- reproducer-w04-6 req 16 Bash `sleep 60; cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/` -> <tool_use_error>Blocked: sleep 60 followed by: cd /Users/hacker/Documents/tmp/claude-worktrees/Murmu
- reproducer-w04-4 req 6 mcp__plugin_colgrep-mcp_colgrep__search `` -> Error executing tool search: [PATH_NOT_FOUND] Path(s) not found: __instrumenta__ (relative paths are
- reproducer-w04-5 req 31 Bash `python3 - <<'EOF' p="__instrumenta__/w04c5_paired_hook_timing.py" s=op` -> Permission for this command was denied by a built-in Claude Code safety check, not by the user. The 
- reproducer-w04-5 req 32 Bash `grep -c strip-sc __instrumenta__/w04c5_paired_hook_timing.py; cat > __` -> Exit code 1 0 nogate ['python3 -S -I "${CLAUDE_PLUGIN_ROOT}/scripts/budget.py"'] Traceback (most rec
- author-w04-3 req 28 Bash `sleep 90; D=/private/tmp/murmuration-w04/author-w04-3/runs; for r in x` -> <tool_use_error>Blocked: sleep 90 followed by: D=/private/tmp/murmuration-w04/author-w04-3/runs for 
- author-w04-3 req 91 Bash `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuratio` -> Exit code 1 1 9c226a0 w04-c7: correct the E3 near-fit count quoted 8d71e8c0f33b7e927133e7e44194de37
- author-w04-4 req 58 Bash `sed -i 's/(5000 + 200 + 300) \* 10 \/ 1e6 - 3 \* 8e-6/(5000 + 200 + 30` -> Exit code 1 sed: 1: "scripts/budget_selftest ...": unterminated substitute pattern
- author-w04-4 req 66 Bash `python3 - <<'PYEOF' p="scripts/budget_selftest.py"; s=open(p).read() a` -> Exit code 1 PASS budget Traceback (most recent call last):   File "/Users/hacker/Documents/tmp/claud
- author-w04-6 req 10 Bash `S=/private/tmp/murmuration-w04/author-w04-6; export COLGREP_DATA_DIR=$` -> Exit code 1 cat: illegal option -- A usage: cat [-belnstuv] [file ...] cat: illegal option -- A usag
- reproducer-w04-7 req 11 Bash `cd /private/tmp/murmuration-w04/author-w04-3/; diff -r export export-q` -> Exit code 1 diff -r export/agents/author.md export-q/agents/author.md 24,27c24,30 < computes, from w
- reproducer-w04-7 req 15 Bash `cd /private/tmp/murmuration-w04/author-w04-3/runs_b/pt1r1/lab; wc -c _` -> Exit code 1      447 __design__/framing.md Traceback (most recent call last):   File "<stdin>", line
- reproducer-w04-9 req 6 Bash `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuratio` -> Exit code 1 cell	n1_mine	n1_end_all_reqs	sonnet_usd_platform_over_B	hook_used_over_B_at_nearest_req	
- reproducer-w04-9 req 17 Bash `sleep 45; echo done` -> <tool_use_error>Blocked: sleep 45 followed by: echo done. To wait for a condition, use Monitor with 
- reproducer-w04-8 req 17 Bash `sleep 45; echo ok` -> <tool_use_error>Blocked: sleep 45 followed by: echo ok. To wait for a condition, use Monitor with an
- reproducer-w04-8 req 29 Bash `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuratio` -> Exit code 1 e1c-b1 {'seed': 20261041, 'cap': '', 'B': '0.30', 'T': '20', 'files': 150, 'brief': 'lis

## Re-reads (same file by Read or a bare cat/head/sed/tail, more than once) and repeated Bash commands
- reproducer-w04-2 repeated bash: {'timeout 115 sh -c \'until [ -n "$(find __pondus__/w04-c2.md _': 2}
- author-w04-4 repeated bash: {'W=/private/tmp/murmuration-w04/author-w04-4; source $W/paths': 2}

## Largest tool outputs by carry cost (one cache write, then a cache read at every later request; 4 chars per token)
pooled carry cost of all tool outputs: 3.16 USD of 25.66 total spend
- outputs over 2000 chars: 216 of 770 calls, carry 2.70 USD (86% of carry)
- outputs over 8000 chars: 60 of 770 calls, carry 1.62 USD (51% of carry)
- outputs over 20000 chars: 6 of 770 calls, carry 0.55 USD (17% of carry)
| carry USD | worker | request | call | chars | later requests | what |
|--:|:--|--:|:--|--:|--:|:--|
| 0.221 | author-w04-4 | 2 | Read | 61427 | 119 | `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417` |
| 0.099 | author-w04-2 | 1 | Read | 30415 | 105 | `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417` |
| 0.080 | author-w04-3 | 0 | Read | 22955 | 115 | `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417` |
| 0.076 | author-w04-2 | 5 | Bash | 23974 | 101 | `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3` |
| 0.069 | author-w04-4 | 3 | Read | 19401 | 118 | `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417` |
| 0.052 | author-w04-4 | 19 | Bash | 16533 | 102 | `uptime; cd /tmp; python3 - <<'EOF' import os,time,statistics as st def ts(argv,n` |
| 0.047 | author-w04-3 | 1 | Bash | 13464 | 114 | `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3` |
| 0.041 | author-w04-2 | 3 | Bash | 12731 | 103 | `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3` |
| 0.037 | author-w04-6 | 0 | Read | 30889 | 23 | `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417` |
| 0.036 | author-w04-4 | 30 | Bash | 12442 | 91 | `cd /private/tmp/murmuration-w04/author-w04-4/rec && python3 - <<'EOF' import jso` |
| 0.036 | reproducer-w04-5 | 0 | Read | 19068 | 50 | `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417` |
| 0.035 | author-w04-3 | 2 | Bash | 10187 | 113 | `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3` |
| 0.033 | reproducer-w04-8 | 12 | Bash | 25235 | 27 | `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3` |
| 0.032 | author-w04-2 | 4 | Bash | 10011 | 102 | `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3` |
| 0.031 | author-w04-2 | 2 | Bash | 9765 | 104 | `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3` |

## Seconds by category, model side vs tool side
| category | model s | tool s | tool share |
|:--|--:|--:|--:|
| handback | 294 | 34 | 10% |
| exchange | 213 | 22 | 10% |
| deliver | 1221 | 265 | 18% |
| run | 2731 | 9414 | 78% |
| write-other | 894 | 466 | 34% |
| outside | 170 | 99 | 37% |
| doc | 195 | 71 | 27% |
| search | 70 | 15 | 18% |
| wait | 3 | 0 | 0% |
| look | 557 | 171 | 23% |
| none | 9 | 0 | 0% |
| all | 6356 | 10557 | 62% |

tool waits over 120 s: 25 calls, 6447 s of 10557 s tool time
- author-w04-4 req 99: 602 s `W=/private/tmp/murmuration-w04/author-w04-4; until [ "$(wc -l < $W/final.log)" -ge 3 ]; do sleep 10; done; cat`
- author-w04-3 req 26: 601 s `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417be; D=/private/tmp/murmurat`
- author-w04-2 req 43: 541 s `S=/private/tmp/murmuration-w04/author-w04-2; timeout 590 sh -c "until [ \$(ls $S/runs/ux-*/meta.json 2>/dev/nu`
- author-w04-2 req 24: 386 s `S=/private/tmp/murmuration-w04/author-w04-2; timeout 580 sh -c "until [ \$(ls $S/runs/e2-c*/meta.json $S/runs/`
- author-w04-2 req 65: 343 s `S=/private/tmp/murmuration-w04/author-w04-2; timeout 595 sh -c "until ! pgrep -f watch2.py >/dev/null; do slee`
- author-w04-2 req 20: 337 s `S=/private/tmp/murmuration-w04/author-w04-2; timeout 560 sh -c "until [ \$(ls $S/runs/e1-*/meta.json 2>/dev/nu`
- author-w04-2 req 28: 313 s `S=/private/tmp/murmuration-w04/author-w04-2; timeout 590 sh -c "until [ \$(ls $S/runs/x-c*/meta.json 2>/dev/nu`
- author-w04-2 req 38: 307 s `S=/private/tmp/murmuration-w04/author-w04-2; timeout 590 sh -c "until [ \$(ls $S/runs/u-*/meta.json 2>/dev/nul`
- author-w04-4 req 94: 281 s `python3 - <<'PYEOF' p="__instrumenta__/hook_cost_time.py"; s=open(p).read() a='FLOORS = {"floor:sh-noop": "sh `
- author-w04-2 req 97: 265 s `S=/private/tmp/murmuration-w04/author-w04-2; timeout 590 sh -c "until [ \$(ls $S/runs/e1c-*/meta.json 2>/dev/n`
- author-w04-2 req 14: 235 s `S=/private/tmp/murmuration-w04/author-w04-2; timeout 500 sh -c "until [ -s $S/runs/pilot-A/meta.json ] && [ -s`
- author-w04-3 req 102: 213 s `D=/private/tmp/murmuration-w04/author-w04-3; for i in $(seq 1 55); do grep -q done $D/e3c_loop.log 2>/dev/null`

## Failed calls by class (request cost = the whole request at that context; the retry costs one more)
calls in total: 770; failed: 31
| class | calls | workers | USD of those requests |
|:--|--:|--:|--:|
| nonzero exit (probe, diff/grep/git/python traceback) | 14 | 10 | 0.451 |
| sleep blocked by the harness | 10 | 8 | 0.127 |
| zsh: unquoted == or =word | 3 | 2 | 0.048 |
| colgrep: relative path | 2 | 2 | 0.023 |
| tool not available to this worker | 1 | 1 | 0.012 |
| permission denied | 1 | 1 | 0.029 |

## Calls per request
{0: 2, 1: 670, 2: 34, 3: 9, 5: 1}

## Chains of consecutive read-only requests (look, doc, outside, search) that could have been one command
chains of 2 or more: 43; USD saved if each chain were one request: between 0.56 (cache reads only) and 1.94 (whole requests) of 25.66 (2% to 8%)

## Exchange latency (reproducer's question to the author's answer arriving in its queue)
| reproducer | author | question chars | answer after s | requests in the window | USD of those | of which a bare wait (sleep/until/poll) |
|:--|:--|--:|--:|--:|--:|--:|
| reproducer-w04-1 | author-w04-1 | 2522 | 50 | 2 | 0.041 | 0 |
| reproducer-w04-3 | author-w04-2 | 1460 | 447 | 7 | 0.102 | 1 |
| reproducer-w04-2 | author-w04-2 | 1391 | 419 | 11 | 0.129 | 7 |
| reproducer-w04-10 | author-w04-3 | 1687 | 34 | 6 | 0.087 | 2 |
| reproducer-w04-6 | author-w04-6 | 1512 | 39 | 7 | 0.082 | 1 |
| reproducer-w04-4 | author-w04-3 | 1744 | 311 | 8 | 0.168 | 0 |
| reproducer-w04-5 | author-w04-4 | 2094 | 24 | 3 | 0.081 | 0 |
| reproducer-w04-7 | author-w04-3 | 1795 | 17 | 1 | 0.040 | 0 |
| reproducer-w04-9 | author-w04-2 | 2386 | 83 | 6 | 0.084 | 1 |
| reproducer-w04-8 | author-w04-2 | 1675 | 113 | 8 | 0.116 | 3 |
| reproducer-w04-8 | author-w04-2 | 1625 | 127 | 3 | 0.069 | 2 |

answer latency: n=11, median 83 s, min 17 s, max 447 s

## Cost of the exchange on the author side (runs opened by a peer message)
peer-opened author runs: 7, USD 2.26, of which first requests 1.23; active 299 s
coordinator-opened runs (raises, instructions): 8, USD 4.90; active 3058 s
task-notification-opened runs: 1, USD 0.85

## ESTIMATE: split every tool wait over 240 s into polls of at most 240 s (so the 5 minute cache never lapses)
mid-run cache lapses: 7, premium 2.38 USD; polling cost 0.18 USD; net saving 2.20 USD of 25.66 total spend (9%)

## Orientation, three bounds (share of the worker's list-price USD / seconds)
strict = requests among the first 3 of the first run whose strongest call is doc/search/outside; prefix = requests before the first run/write call (reads of evidence included); wide = every doc/search/outside request of any run
| worker | strict req | strict USD | strict % | strict s | prefix % USD | wide % USD |
|:--|--:|--:|--:|--:|--:|--:|
| author-w04-1 | 2 | 0.092 | 7% | 15 | 9% | 27% |
| reproducer-w04-1 | 2 | 0.056 | 11% | 8 | 11% | 23% |
| reproducer-w04-3 | 2 | 0.069 | 10% | 11 | 12% | 22% |
| author-w04-2 | 3 | 0.097 | 2% | 13 | 4% | 3% |
| reproducer-w04-2 | 1 | 0.027 | 5% | 6 | 18% | 17% |
| reproducer-w04-10 | 1 | 0.026 | 6% | 3 | 15% | 12% |
| reproducer-w04-6 | 1 | 0.027 | 6% | 3 | 15% | 15% |
| reproducer-w04-4 | 1 | 0.028 | 4% | 3 | 19% | 10% |
| reproducer-w04-5 | 2 | 0.078 | 6% | 9 | 7% | 10% |
| author-w04-3 | 3 | 0.120 | 2% | 39 | 3% | 3% |
| author-w04-4 | 1 | 0.028 | 0% | 6 | 3% | 2% |
| author-w04-6 | 3 | 0.085 | 17% | 11 | 17% | 24% |
| reproducer-w04-7 | 2 | 0.070 | 13% | 8 | 15% | 17% |
| reproducer-w04-9 | 1 | 0.025 | 4% | 3 | 14% | 14% |
| reproducer-w04-8 | 2 | 0.053 | 5% | 8 | 12% | 21% |
pooled: strict 3%, prefix 6%, wide 8% of 25.66 USD
