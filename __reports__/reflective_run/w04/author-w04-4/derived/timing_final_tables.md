| case | script | variant | n | wall median ms | wall p90 ms | cpu median ms | rc=0 | stdout bytes |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|
| floor:python3-S-I-c-pass | - | - | 60 | 54.0 | 113.5 | 11.4 | 60 | 0 |
| floor:python3-S-I-import-json-os-sys | - | - | 60 | 60.8 | 100.9 | 17.6 | 60 | 0 |
| floor:python3-c-pass | - | - | 60 | 68.3 | 126.4 | 23.1 | 60 | 0 |
| floor:sh-noop | - | - | 60 | 30.4 | 56.7 | 3.3 | 60 | 0 |
| post_tool_batch:main | budget | new | 60 | 33.5 | 63.6 | 3.6 | 60 | 0 |
| post_tool_batch:main | budget | old | 60 | 89.5 | 176.8 | 40.5 | 60 | 0 |
| post_tool_batch:worker-long | budget | new | 60 | 63.9 | 111.8 | 15.9 | 60 | 0 |
| post_tool_batch:worker-long | budget | old | 60 | 119.5 | 159.1 | 72.2 | 60 | 0 |
| post_tool_batch:worker-short | budget | new | 60 | 59.3 | 99.6 | 15.7 | 60 | 0 |
| post_tool_batch:worker-short | budget | old | 60 | 93.3 | 147.6 | 41.9 | 60 | 0 |
| post_tool_use:handback | budget | new | 60 | 59.3 | 116.2 | 15.6 | 60 | 0 |
| post_tool_use:handback | budget | old | 60 | 89.9 | 135.1 | 41.9 | 60 | 0 |
| post_tool_use:handback | handback | new | 60 | 66.4 | 114.1 | 20.8 | 60 | 0 |
| post_tool_use:handback | handback | old | 60 | 76.2 | 124.7 | 31.5 | 60 | 0 |
| post_tool_use:main | budget | new | 60 | 31.1 | 53.4 | 3.5 | 60 | 0 |
| post_tool_use:main | budget | old | 60 | 90.0 | 150.7 | 40.7 | 60 | 0 |
| post_tool_use:worker-long | budget | new | 60 | 59.2 | 96.2 | 15.8 | 60 | 0 |
| post_tool_use:worker-long | budget | old | 60 | 126.4 | 175.0 | 73.2 | 60 | 0 |
| post_tool_use:worker-short | budget | new | 60 | 59.0 | 91.2 | 15.6 | 60 | 0 |
| post_tool_use:worker-short | budget | old | 60 | 90.1 | 141.7 | 42.6 | 60 | 0 |
| pre_tool_use:dispatch | budget | new | 60 | 64.0 | 104.1 | 19.0 | 60 | 0 |
| pre_tool_use:dispatch | budget | old | 60 | 86.1 | 134.9 | 40.6 | 60 | 0 |
| pre_tool_use:handback-explorer-no-report | handback | new | 60 | 57.0 | 103.5 | 13.1 | 60 | 0 |
| pre_tool_use:handback-explorer-no-report | handback | old | 60 | 87.4 | 134.8 | 40.1 | 60 | 0 |
| subagent_start:worker | budget | new | 60 | 72.1 | 115.8 | 20.9 | 60 | 1092 |
| subagent_start:worker | budget | old | 60 | 85.9 | 124.0 | 40.5 | 60 | 1092 |
| subagent_stop:worker-long | budget | new | 60 | 67.6 | 121.5 | 21.1 | 60 | 0 |
| subagent_stop:worker-long | budget | old | 60 | 119.1 | 210.4 | 72.2 | 60 | 0 |
| subagent_stop:worker-long | handback | new | 60 | 70.1 | 128.7 | 21.7 | 60 | 0 |
| subagent_stop:worker-long | handback | old | 60 | 74.8 | 103.6 | 31.3 | 60 | 0 |
| subagent_stop:worker-short | budget | new | 60 | 65.7 | 113.7 | 21.0 | 60 | 0 |
| subagent_stop:worker-short | budget | old | 60 | 88.0 | 169.1 | 42.1 | 60 | 0 |
| subagent_stop:worker-short | handback | new | 60 | 63.5 | 102.4 | 21.1 | 60 | 0 |
| subagent_stop:worker-short | handback | old | 60 | 77.0 | 129.4 | 31.6 | 60 | 0 |
| user_prompt_submit:main | user_words | new | 60 | 73.2 | 125.4 | 28.2 | 60 | 0 |
| user_prompt_submit:main | user_words | old | 60 | 69.9 | 104.1 | 27.4 | 60 | 0 |

| case | script | old median ms | new median ms | ratio (new/old) | old cpu | new cpu | cpu ratio |
|:--|:--|--:|--:|--:|--:|--:|--:|
| post_tool_batch:main | budget | 89.5 | 33.5 | 0.37 | 40.5 | 3.6 | 0.09 |
| post_tool_batch:worker-long | budget | 119.5 | 63.9 | 0.53 | 72.2 | 15.9 | 0.22 |
| post_tool_batch:worker-short | budget | 93.3 | 59.3 | 0.64 | 41.9 | 15.7 | 0.37 |
| post_tool_use:handback | budget | 89.9 | 59.3 | 0.66 | 41.9 | 15.6 | 0.37 |
| post_tool_use:handback | handback | 76.2 | 66.4 | 0.87 | 31.5 | 20.8 | 0.66 |
| post_tool_use:main | budget | 90.0 | 31.1 | 0.35 | 40.7 | 3.5 | 0.09 |
| post_tool_use:worker-long | budget | 126.4 | 59.2 | 0.47 | 73.2 | 15.8 | 0.22 |
| post_tool_use:worker-short | budget | 90.1 | 59.0 | 0.66 | 42.6 | 15.6 | 0.37 |
| pre_tool_use:dispatch | budget | 86.1 | 64.0 | 0.74 | 40.6 | 19.0 | 0.47 |
| pre_tool_use:handback-explorer-no-report | handback | 87.4 | 57.0 | 0.65 | 40.1 | 13.1 | 0.33 |
| subagent_start:worker | budget | 85.9 | 72.1 | 0.84 | 40.5 | 20.9 | 0.52 |
| subagent_stop:worker-long | budget | 119.1 | 67.6 | 0.57 | 72.2 | 21.1 | 0.29 |
| subagent_stop:worker-long | handback | 74.8 | 70.1 | 0.94 | 31.3 | 21.7 | 0.69 |
| subagent_stop:worker-short | budget | 88.0 | 65.7 | 0.75 | 42.1 | 21.0 | 0.50 |
| subagent_stop:worker-short | handback | 77.0 | 63.5 | 0.82 | 31.6 | 21.1 | 0.67 |
| user_prompt_submit:main | user_words | 69.9 | 73.2 | 1.05 | 27.4 | 28.2 | 1.03 |
