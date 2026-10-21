| case | script | variant | n | wall median ms | wall p90 ms | cpu median ms | rc=0 | stdout bytes |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|
| post_tool_use:handback | budget | new | 40 | 111.2 | 119.0 | 73.1 | 40 | 0 |
| post_tool_use:handback | budget | old | 40 | 105.2 | 133.2 | 51.4 | 40 | 0 |
| post_tool_use:handback | handback | new | 40 | 83.9 | 110.6 | 30.0 | 40 | 0 |
| post_tool_use:handback | handback | old | 40 | 91.6 | 105.4 | 37.9 | 40 | 0 |
| post_tool_use:main | budget | new | 40 | 64.7 | 76.6 | 31.5 | 40 | 0 |
| post_tool_use:main | budget | old | 40 | 101.4 | 106.0 | 48.4 | 40 | 0 |
| post_tool_use:worker-long | budget | new | 40 | 111.3 | 123.8 | 72.9 | 40 | 0 |
| post_tool_use:worker-long | budget | old | 40 | 141.8 | 165.3 | 88.2 | 40 | 0 |
| post_tool_use:worker-short | budget | new | 40 | 110.9 | 118.7 | 72.7 | 40 | 0 |
| post_tool_use:worker-short | budget | old | 40 | 104.6 | 115.2 | 51.0 | 40 | 0 |

| case | script | old median ms | new median ms | ratio (new/old) | old cpu | new cpu | cpu ratio |
|:--|:--|--:|--:|--:|--:|--:|--:|
| post_tool_use:handback | budget | 105.2 | 111.2 | 1.06 | 51.4 | 73.1 | 1.42 |
| post_tool_use:handback | handback | 91.6 | 83.9 | 0.92 | 37.9 | 30.0 | 0.79 |
| post_tool_use:main | budget | 101.4 | 64.7 | 0.64 | 48.4 | 31.5 | 0.65 |
| post_tool_use:worker-long | budget | 141.8 | 111.3 | 0.78 | 88.2 | 72.9 | 0.83 |
| post_tool_use:worker-short | budget | 104.6 | 110.9 | 1.06 | 51.0 | 72.7 | 1.43 |
