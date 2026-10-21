| case | script | variant | n | wall median ms | wall p90 ms | cpu median ms | rc=0 | stdout bytes |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|
| post_tool_use:handback | budget | new | 40 | 90.5 | 101.3 | 33.5 | 40 | 0 |
| post_tool_use:handback | budget | old | 40 | 108.2 | 116.1 | 51.7 | 40 | 0 |
| post_tool_use:handback | handback | new | 40 | 85.9 | 112.0 | 29.8 | 40 | 0 |
| post_tool_use:handback | handback | old | 40 | 93.8 | 96.9 | 38.3 | 40 | 0 |
| post_tool_use:main | budget | new | 40 | 41.6 | 57.3 | 5.0 | 40 | 0 |
| post_tool_use:main | budget | old | 40 | 103.2 | 128.2 | 48.2 | 40 | 0 |
| post_tool_use:worker-long | budget | new | 40 | 90.7 | 116.3 | 33.0 | 40 | 0 |
| post_tool_use:worker-long | budget | old | 40 | 145.5 | 201.8 | 88.5 | 40 | 0 |
| post_tool_use:worker-short | budget | new | 40 | 89.4 | 112.4 | 32.9 | 40 | 0 |
| post_tool_use:worker-short | budget | old | 40 | 107.7 | 117.5 | 51.7 | 40 | 0 |

| case | script | old median ms | new median ms | ratio (new/old) | old cpu | new cpu | cpu ratio |
|:--|:--|--:|--:|--:|--:|--:|--:|
| post_tool_use:handback | budget | 108.2 | 90.5 | 0.84 | 51.7 | 33.5 | 0.65 |
| post_tool_use:handback | handback | 93.8 | 85.9 | 0.92 | 38.3 | 29.8 | 0.78 |
| post_tool_use:main | budget | 103.2 | 41.6 | 0.40 | 48.2 | 5.0 | 0.10 |
| post_tool_use:worker-long | budget | 145.5 | 90.7 | 0.62 | 88.5 | 33.0 | 0.37 |
| post_tool_use:worker-short | budget | 107.7 | 89.4 | 0.83 | 51.7 | 32.9 | 0.64 |
