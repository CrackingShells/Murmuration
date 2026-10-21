| case | script | variant | n | wall median ms | wall p90 ms | cpu median ms | rc=0 | stdout bytes |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|
| post_tool_use:handback | budget | new | 40 | 97.8 | 108.9 | 48.7 | 40 | 0 |
| post_tool_use:handback | budget | old | 40 | 107.2 | 125.9 | 51.5 | 40 | 0 |
| post_tool_use:handback | handback | new | 40 | 84.7 | 93.5 | 29.7 | 40 | 0 |
| post_tool_use:handback | handback | old | 40 | 92.3 | 111.7 | 38.1 | 40 | 0 |
| post_tool_use:main | budget | new | 40 | 51.9 | 62.9 | 15.6 | 40 | 0 |
| post_tool_use:main | budget | old | 40 | 103.1 | 119.0 | 48.4 | 40 | 0 |
| post_tool_use:worker-long | budget | new | 40 | 96.7 | 111.4 | 48.7 | 40 | 0 |
| post_tool_use:worker-long | budget | old | 40 | 142.3 | 150.8 | 88.3 | 40 | 0 |
| post_tool_use:worker-short | budget | new | 40 | 97.9 | 109.9 | 48.7 | 40 | 0 |
| post_tool_use:worker-short | budget | old | 40 | 105.9 | 119.8 | 50.8 | 40 | 0 |

| case | script | old median ms | new median ms | ratio (new/old) | old cpu | new cpu | cpu ratio |
|:--|:--|--:|--:|--:|--:|--:|--:|
| post_tool_use:handback | budget | 107.2 | 97.8 | 0.91 | 51.5 | 48.7 | 0.95 |
| post_tool_use:handback | handback | 92.3 | 84.7 | 0.92 | 38.1 | 29.7 | 0.78 |
| post_tool_use:main | budget | 103.1 | 51.9 | 0.50 | 48.4 | 15.6 | 0.32 |
| post_tool_use:worker-long | budget | 142.3 | 96.7 | 0.68 | 88.3 | 48.7 | 0.55 |
| post_tool_use:worker-short | budget | 105.9 | 97.9 | 0.92 | 50.8 | 48.7 | 0.96 |
