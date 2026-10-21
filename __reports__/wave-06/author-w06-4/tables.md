## s2: platform-recorded hook time per run (2 workers per run), main 134e3ac against build a5e708b
| run | workers | command hook ms (budget / handback / outage: n, sum) | mcp_tool ms (n, sum) | platform total ms | per worker ms |
|:--|--:|:--|:--|--:|--:|
| g_s2_main_0 | 2 | budget: 34, 11685 / handback: 6, 1547 / outage: 0, 0 | 0, 0 | 13232 | 6616 |
| g_s2_new_0 | 2 | budget: 0, 0 / handback: 0, 0 / outage: 6, 2436 | 37, 155 | 2591 | 1296 |
| g_s2_main_1 | 2 | budget: 32, 3411 / handback: 6, 749 / outage: 0, 0 | 0, 0 | 4160 | 2080 |
| g_s2_new_1 | 2 | budget: 0, 0 / handback: 0, 0 / outage: 6, 1023 | 40, 111 | 1134 | 567 |
| g_s2_main_2 | 2 | budget: 34, 3724 / handback: 6, 768 / outage: 0, 0 | 0, 0 | 4492 | 2246 |
| g_s2_new_2 | 2 | budget: 0, 0 / handback: 0, 0 / outage: 6, 1000 | 40, 136 | 1136 | 568 |

## m3-style context: request 0 input tokens (main thread; each worker)
| run | request 0 input tokens, main thread | worker request 0 input tokens (each) |
|:--|--:|:--|
| g_s2_main_0 | 32511 | [12653, 12653] |
| g_s2_new_0 | 34470 | [12751, 12751] |
| g_s2_main_1 | 27984 | [12974, 12974] |
| g_s2_new_1 | 33844 | [12754, 12754] |
| g_s2_main_2 | 33357 | [12968, 12968] |
| g_s2_new_2 | 28012 | [13076, 12761] |

## s3: outage runs on a5e708b (a: kill by pid, restart works; b: restart exits; c: restart hangs; mid: the worker kills the server and the restart exits)
| run | server starts | failure records (main / workers) | boundaries over 1 s: PostToolUse+PostToolBatch settle ms | longest boundary ms | text with HOOKS DOWN / Hooks down in: PI transcript / worker transcripts | DENYME-style effects |
|:--|--:|:--|:--|--:|:--|:--|
| g_b0 | -1 | 8 err, 0 cancelled / 17 err | [] | 190 | 2 / [3] | final:  |
| g_b1 | -1 | 8 err, 0 cancelled / 18 err | [] | 193 | 2 / [3] | final:  |
| g_mid0 | -1 | 0 err, 0 cancelled / 0 err | [] | 184 | 0 / [0] | final:  |
| g_mid1 | -1 | 2 err, 0 cancelled / 12 err | [2220] | 2220 | 4 / [1] | final:  |
| g_c0 | -1 | 2 err, 7 cancelled / 17 err | [6013, 6015, 6013] | 6015 | 4 / [1] | final:  |

## s1: replay of 197 transcripts (final build; sequential and parallel result records), EQUAL / DIFF counts
final_seq: 197 EQUAL, 0 DIFF
final_par: 197 EQUAL, 0 DIFF
mutants on the first 60 transcripts: mut1 (dispatch row without tool_input) 15 DIFF; mut2 (PostToolBatch row without tool_calls) 29 DIFF
