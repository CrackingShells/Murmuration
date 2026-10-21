| thread / registration | starts in wave 4 | old ms | new ms (short / long transcript) |
|:--|--:|--:|--:|
| main PostToolBatch||budget.py | 89 | 145.6 / 145.6 | 0.0 / 0.0 |
| main PostToolUse||budget.py | 104 | 140.0 / 140.0 | 67.8 / 67.8 |
| main PreToolUse|Agent|Task|budget.py | 15 | 137.3 / 137.3 | 117.7 / 117.7 |
| workers PostToolBatch||budget.py | 714 | 133.1 / 172.6 | 0.0 / 0.0 |
| workers PostToolUse||budget.py | 739 | 130.4 / 187.8 | 121.6 / 127.3 |
| workers PostToolUse|SubagentHandback|handback.py | 29 | 127.1 / 127.1 | 119.3 / 119.3 |
| workers PreToolUse|SubagentHandback|handback.py | 29 | 133.5 / 133.5 | 114.1 / 114.1 |
| workers SubagentStart||budget.py | 23 | 145.5 / 145.5 | 137.8 / 137.8 |
| workers SubagentStop||budget.py | 23 | 148.2 / 169.4 | 127.9 / 111.7 |
| workers SubagentStop||handback.py | 23 | 129.4 / 118.0 | 138.8 / 110.3 |

interpolation weight F (0 = short transcript price, 1 = long) = 0.049 over 15 workers

transcript price = short: old 238.3 s, new 114.8 s serial per wave; new/old 0.482 (95% bootstrap 0.409 to 0.567); down 51.8%

transcript price = interp: old 241.7 s, new 114.9 s serial per wave; new/old 0.475 (95% bootstrap 0.410 to 0.558); down 52.5%

transcript price = long: old 309.1 s, new 117.9 s serial per wave; new/old 0.381 (95% bootstrap 0.328 to 0.478); down 61.9%
