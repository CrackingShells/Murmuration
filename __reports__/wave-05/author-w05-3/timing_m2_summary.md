| case | script | variant | n | wall median ms | wall p90 ms | cpu median ms | rc=0 | stdout bytes |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|
| floor:python3-S-I-c-pass | - | - | 100 | 106.1 | 225.5 | 13.9 | 100 | 0 |
| floor:python3-S-I-import-json-os-sys | - | - | 100 | 112.4 | 236.7 | 21.6 | 100 | 0 |
| floor:python3-c-pass | - | - | 100 | 126.2 | 233.8 | 28.8 | 100 | 0 |
| floor:sh-noop | - | - | 100 | 59.4 | 142.0 | 4.1 | 100 | 0 |
| post_tool_batch:main | budget | old | 100 | 145.6 | 249.0 | 49.3 | 100 | 0 |
| post_tool_batch:worker-long | budget | old | 100 | 172.6 | 277.7 | 88.9 | 100 | 0 |
| post_tool_batch:worker-short | budget | old | 100 | 133.1 | 257.7 | 51.4 | 100 | 0 |
| post_tool_use:handback | budget | new | 100 | 147.1 | 292.6 | 33.2 | 100 | 0 |
| post_tool_use:handback | budget | old | 100 | 148.8 | 282.7 | 51.8 | 100 | 0 |
| post_tool_use:handback | handback | new | 100 | 119.3 | 237.3 | 29.6 | 100 | 0 |
| post_tool_use:handback | handback | old | 100 | 127.1 | 263.1 | 38.3 | 100 | 0 |
| post_tool_use:main | budget | new | 100 | 67.8 | 174.6 | 4.8 | 100 | 0 |
| post_tool_use:main | budget | old | 100 | 140.0 | 279.5 | 48.7 | 100 | 0 |
| post_tool_use:worker-long | budget | new | 100 | 127.3 | 261.0 | 33.1 | 100 | 0 |
| post_tool_use:worker-long | budget | old | 100 | 187.8 | 314.4 | 89.0 | 100 | 0 |
| post_tool_use:worker-short | budget | new | 100 | 121.6 | 239.1 | 33.0 | 100 | 0 |
| post_tool_use:worker-short | budget | old | 100 | 130.4 | 300.8 | 52.0 | 100 | 0 |
| pre_tool_use:dispatch | budget | new | 100 | 117.7 | 250.8 | 31.7 | 100 | 0 |
| pre_tool_use:dispatch | budget | old | 100 | 137.3 | 259.1 | 49.4 | 100 | 0 |
| pre_tool_use:handback-explorer-no-report | handback | new | 100 | 114.1 | 225.7 | 24.8 | 100 | 0 |
| pre_tool_use:handback-explorer-no-report | handback | old | 100 | 133.5 | 268.8 | 50.3 | 100 | 0 |
| subagent_start:worker | budget | new | 100 | 137.8 | 246.4 | 32.8 | 100 | 1092 |
| subagent_start:worker | budget | old | 100 | 145.5 | 287.2 | 49.9 | 100 | 1092 |
| subagent_stop:worker-long | budget | new | 100 | 111.7 | 222.7 | 32.9 | 100 | 0 |
| subagent_stop:worker-long | budget | old | 100 | 169.4 | 293.3 | 89.0 | 100 | 0 |
| subagent_stop:worker-long | handback | new | 100 | 110.3 | 224.5 | 29.3 | 100 | 0 |
| subagent_stop:worker-long | handback | old | 100 | 118.0 | 235.3 | 37.5 | 100 | 0 |
| subagent_stop:worker-short | budget | new | 100 | 127.9 | 249.4 | 32.6 | 100 | 0 |
| subagent_stop:worker-short | budget | old | 100 | 148.2 | 299.4 | 51.8 | 100 | 0 |
| subagent_stop:worker-short | handback | new | 100 | 138.8 | 271.5 | 29.4 | 100 | 0 |
| subagent_stop:worker-short | handback | old | 100 | 129.4 | 237.7 | 37.8 | 100 | 0 |
| user_prompt_submit:main | user_words | new | 100 | 143.2 | 282.3 | 35.0 | 100 | 0 |
| user_prompt_submit:main | user_words | old | 100 | 147.5 | 259.3 | 34.8 | 100 | 0 |

| case | script | old median ms | new median ms | ratio (new/old) | old cpu | new cpu | cpu ratio |
|:--|:--|--:|--:|--:|--:|--:|--:|
| post_tool_use:handback | budget | 148.8 | 147.1 | 0.99 | 51.8 | 33.2 | 0.64 |
| post_tool_use:handback | handback | 127.1 | 119.3 | 0.94 | 38.3 | 29.6 | 0.77 |
| post_tool_use:main | budget | 140.0 | 67.8 | 0.48 | 48.7 | 4.8 | 0.10 |
| post_tool_use:worker-long | budget | 187.8 | 127.3 | 0.68 | 89.0 | 33.1 | 0.37 |
| post_tool_use:worker-short | budget | 130.4 | 121.6 | 0.93 | 52.0 | 33.0 | 0.64 |
| pre_tool_use:dispatch | budget | 137.3 | 117.7 | 0.86 | 49.4 | 31.7 | 0.64 |
| pre_tool_use:handback-explorer-no-report | handback | 133.5 | 114.1 | 0.85 | 50.3 | 24.8 | 0.49 |
| subagent_start:worker | budget | 145.5 | 137.8 | 0.95 | 49.9 | 32.8 | 0.66 |
| subagent_stop:worker-long | budget | 169.4 | 111.7 | 0.66 | 89.0 | 32.9 | 0.37 |
| subagent_stop:worker-long | handback | 118.0 | 110.3 | 0.94 | 37.5 | 29.3 | 0.78 |
| subagent_stop:worker-short | budget | 148.2 | 127.9 | 0.86 | 51.8 | 32.6 | 0.63 |
| subagent_stop:worker-short | handback | 129.4 | 138.8 | 1.07 | 37.8 | 29.4 | 0.78 |
| user_prompt_submit:main | user_words | 147.5 | 143.2 | 0.97 | 34.8 | 35.0 | 1.01 |
