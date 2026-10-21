## 1. Bash tool phase by arm (ms; median / p90 / max), calls 2..8 of each session (call 1 carries the shell-snapshot start and is shown apart)

| arm | sessions | n calls | tool phase (transcript: tool_use record to result record) | PreToolUse hooks (log, longest per call) | classifier wait (log permissionDecisionMs) | command run (log durationMs) | tool_use record to dispatch start (hooks and classifier, as one wait) | dispatch end to result record (PostToolUse hook) | phase, median per session |
|:--|:--|--:|:--|:--|:--|:--|:--|:--|:--|
| A auto, colgrep hook on, no lab plugin | A0,A1 | 14 | 753 / 1747 / 2294 (n=14) | 215 / 1135 / 1979 (n=14) | 372 / 661 / 1489 (n=14) | 74 / 238 / 293 (n=14) | 642 / 1676 / 1997 (n=14) | 2 / 3 / 4 (n=14) | A0 1048 / A1 597 |
| B auto, colgrep off, no lab plugin | B0,B1 | 14 | 709 / 1142 / 1448 (n=14) | 0 / 0 / 0 (n=14) | 628 / 1080 / 1358 (n=14) | 60 / 113 / 254 (n=14) | 631 / 1083 / 1362 (n=14) | 1 / 2 / 3 (n=14) | B0 608 / B1 1066 |
| F default + allowedTools, colgrep off, no lab plugin | F0,F1 | 14 | 55 / 83 / 106 (n=14) | 0 / 0 / 0 (n=14) | 1 / 2 / 2 (n=14) | 51 / 79 / 102 (n=14) | 3 / 3 / 3 (n=14) | 1 / 1 / 1 (n=14) | F0 53 / F1 57 |
| C auto, colgrep on, lab plugin | C0,C1 | 14 | 1054 / 1282 / 1756 (n=14) | 193 / 401 / 540 (n=14) | 640 / 804 / 939 (n=14) | 56 / 124 / 258 (n=14) | 877 / 1009 / 1217 (n=14) | 80 / 218 / 552 (n=14) | C0 1019 / C1 1123 |
| D auto, colgrep off, lab plugin | D0,D1 | 14 | 970 / 1297 / 1519 (n=14) | 84 / 252 / 266 (n=14) | 680 / 841 / 925 (n=14) | 56 / 217 / 314 (n=14) | 782 / 943 / 1100 (n=14) | 69 / 304 / 430 (n=14) | D0 1175 / D1 954 |

Call 1 of each session (first Bash of a session: shell snapshot), phase / run ms:

| arm | call-1 phase ms by session | call-1 run ms by session |
|:--|:--|:--|
| A | A1 736, A0 2316 | A1 236, A0 1207 |
| B | B0 1104, B1 1452 | B0 224, B1 339 |
| F | F0 190, F1 182 | F0 183, F1 173 |
| C | C0 1107, C1 1174 | C0 182, C1 179 |
| D | D0 1232, D1 1314 | D0 168, D1 315 |

## 2. Paired differences of the median tool phase per rep (calls 2..8; one session per arm per rep; arms were run interleaved in a shuffled order, so pairs are by rep index, not adjacent in time)

| rep | A (auto, colgrep on) | B (auto, colgrep off) | C (auto, colgrep on, lab) | D (auto, colgrep off, lab) | F (default+allow, colgrep off) | A-B | C-A | D-B | B-F |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0 | 1048 | 608 | 1019 | 1175 | 53 | 440 | -29 | 567 | 555 |
| 1 | 597 | 1066 | 1123 | 954 | 57 | -469 | 526 | -112 | 1009 |

## 3. Hook runs the log records, by event / tool / script (ms; median / p90 / max)

| event:tool | script | from | runs | ms |
|:--|:--|:--|--:|:--|
| PostToolBatch: | run_hook.py | murmuration@inline | 32 | 60 / 189 / 305 (n=32) |
| PostToolUse:Bash | run_hook.py | murmuration@inline | 32 | 72 / 267 / 548 (n=32) |
| PreToolUse:Bash | colgrep_policy.py | colgrep-mcp@cracking-shells | 32 | 194 / 554 / 1979 (n=32) |
| PreToolUse:Bash | permission_guard.py | murmuration@inline | 32 | 108 / 253 / 497 (n=32) |
| SessionStart:startup | colgrep_policy.py | colgrep-mcp@cracking-shells | 4 | 258 / 261 / 262 (n=4) |
| SessionStart:startup | reset_plan_directive_marker.py | settings | 16 | 171 / 258 / 279 (n=16) |
| SessionStart:startup | tool_routing_policy.py | settings | 16 | 150 / 250 / 277 (n=16) |
| UserPromptSubmit: | inject_plan_directive.py | settings | 16 | 124 / 156 / 204 (n=16) |
| UserPromptSubmit: | user_words.py | murmuration@inline | 4 | 184 / 219 / 233 (n=4) |

Lab plugin hooks fire once per Bash call: PreToolUse:Bash permission_guard.py, PostToolUse run_hook.py (budget); user plugin: colgrep-mcp PreToolUse:Bash colgrep_policy.py via `uv run --no-project --quiet python`.


## 4. Does the classifier wait grow with the transcript? (sessions L0, L1: auto, no colgrep, no lab plugin; 5 Bash calls early, 3 Reads, 5 Bash calls late)

| segment | calls | context tokens at the call | classifier wait ms | tool phase ms | run ms |
|:--|--:|:--|:--|:--|:--|
| early (calls 1-5; call 1 = shell start) | 10 | 41885-42520 | 710 / 1060 / 1175 (n=10) | 856 / 1172 / 1249 (n=10) | 74 / 203 / 266 (n=10) |
| early without call 1 | 8 | 42013-42520 | 710 / 1085 / 1175 (n=8) | 856 / 1189 / 1249 (n=8) | 60 / 159 / 266 (n=8) |
| late (calls 9-13) | 10 | 102337-102970 | 840 / 930 / 941 (n=10) | 908 / 1008 / 1049 (n=10) | 59 / 107 / 151 (n=10) |

Per session and call (L0, L1): n_in_run, ctx tokens, classifier ms, phase ms

L0: 1: 41k 498 660; 2: 42k 519 790; 3: 42k 494 554; 4: 42k 550 608; 5: 42k 549 575; 9: 102k 581 623; 10: 102k 809 905; 11: 102k 849 1004; 12: 102k 831 889; 13: 102k 929 968
L1: 1: 41k 904 1111; 2: 42k 909 999; 3: 42k 1175 1249; 4: 42k 1047 1163; 5: 42k 869 923; 9: 102k 738 821; 10: 102k 829 898; 11: 102k 885 912; 12: 102k 916 971; 13: 102k 941 1049

Reads in L0, L1 (tool, ctx, phase ms): L0 42k 294; L0 63k 272; L0 84k 257; L1 42k 317; L1 63k 291; L1 84k 268

## 5. The same four files read four ways (auto, colgrep off, no lab plugin; one session each)

| variant | sessions' wall duration_ms | prompt to last assistant record s | first tool_use to last result s | main API requests | side queries | tool calls | classifier-decided | sum of classifier waits ms | per-call tool phase ms |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|:--|
| W1 1 Bash, four `cat`s chained | 5724 | 3.39 | 1.17 | 2 | 1 | 1 | 1 | 923 | 1166 |
| W2 4 Bash calls in one message | 5563 | 3.79 | 1.79 | 2 | 1 | 4 | 4 | 4589 | 1696, 1559, 1313, 1195 |
| W3 4 Reads in one message | 5869 | 2.83 | 0.52 | 2 | 1 | 4 | 0 | 12 | 10, 6, 6, 6 |
| W4 4 Reads, one per message | 7097 | 5.11 | 3.03 | 5 | 1 | 4 | 0 | 53 | 30, 24, 28, 26 |

## 6. Sessions: cost, requests, load average

| label | arm | duration_ms | api_ms | main requests | side queries | calls | USD | load1 before | load1 after |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| A1 | auto/on/none | 17547 | 14928 | 10 | 1 | 8 | 0.0078 | 3.43 | 4.36 |
| B0 | auto/off/none | 18971 | 16157 | 10 | 1 | 8 | 0.0077 | 4.00 | 3.65 |
| B1 | auto/off/none | 22017 | 18981 | 10 | 1 | 8 | 0.0077 | 3.53 | 4.48 |
| C0 | auto/on/lab | 24539 | 19787 | 10 | 1 | 8 | 0.0081 | 6.17 | 6.21 |
| C1 | auto/on/lab | 21868 | 17923 | 10 | 1 | 8 | 0.0081 | 6.05 | 5.29 |
| D0 | auto/off/lab | 23170 | 17639 | 10 | 1 | 8 | 0.0086 | 5.62 | 6.17 |
| D1 | auto/off/lab | 20888 | 17090 | 10 | 1 | 8 | 0.0079 | 8.16 | 6.76 |
| F0 | default+allow/off/none | 13263 | 10816 | 10 | 1 | 8 | 0.0077 | 6.76 | 6.05 |
| F1 | default+allow/off/none | 14000 | 11816 | 10 | 1 | 8 | 0.0078 | 2.97 | 3.40 |
| L0 | auto/off/none | 26537 | 21281 | 14 | 4 | 13 | 0.0644 | 4.48 | 4.66 |
| L1 | auto/off/none | 27569 | 23152 | 14 | 4 | 13 | 0.0645 | 3.69 | 2.97 |
| W1 | auto/off/none | 5724 | 2979 | 2 | 1 | 1 | 0.0039 | 4.66 | 5.62 |
| W2 | auto/off/none | 5563 | 3353 | 2 | 1 | 4 | 0.0040 | 3.40 | 3.53 |
| W3 | auto/off/none | 5869 | 2667 | 2 | 1 | 4 | 0.0041 | 6.21 | 8.16 |
| W4 | auto/off/none | 7097 | 4882 | 5 | 1 | 4 | 0.0053 | 4.36 | 3.69 |
| trial | auto/on/none | 27208 | 21864 | 10 | 1 | 8 | 0.0085 | 5.99 | 0.00 |
