# strata of recorded classifier allows (version >= 2.1.293)

population N = 30525; sample n = 1608; seed 20261024; allocation n_h = min(N_h, max(floor, round(1500 * sqrt(N_h) / sum sqrt(N)))), floor 8 (25 for risky-word strata)

| tool family | source | Bash command family | risk words | N_h | n_h | weight N_h/n_h | unique texts (digits and uuids masked) | sessions |
|:--|:--|:--|:--|--:|--:|--:|--:|--:|
| Bash | arena | read-shell | plain | 8017 | 152 | 52.7 | 628 | 740 |
| Bash | natural | read-shell | plain | 5048 | 121 | 41.7 | 3814 | 132 |
| Bash | natural | python/uv | plain | 2266 | 81 | 28.0 | 2257 | 45 |
| Bash | natural | read-shell | risky | 1727 | 71 | 24.3 | 1591 | 86 |
| Bash | natural | git | plain | 1205 | 59 | 20.4 | 1186 | 70 |
| Bash | natural | other | plain | 1187 | 59 | 20.1 | 1181 | 43 |
| Bash | natural | python/uv | risky | 1082 | 56 | 19.3 | 1075 | 64 |
| MCP | natural | - | plain | 1058 | 55 | 19.2 | 904 | 82 |
| other | natural | - | plain | 909 | 51 | 17.8 | 863 | 105 |
| Bash | natural | search | plain | 875 | 50 | 17.5 | 870 | 43 |
| Bash | arena | process | plain | 830 | 49 | 16.9 | 30 | 127 |
| other | arena | - | plain | 761 | 47 | 16.2 | 652 | 566 |
| Agent | arena | - | plain | 743 | 46 | 16.2 | 207 | 583 |
| Bash | natural | other | risky | 609 | 42 | 14.5 | 605 | 46 |
| Bash | natural | process | plain | 589 | 41 | 14.4 | 329 | 50 |
| Agent | natural | - | plain | 386 | 33 | 11.7 | 329 | 107 |
| Bash | natural | fs-mutate | risky | 372 | 33 | 11.3 | 372 | 50 |
| Bash | natural | search | risky | 326 | 31 | 10.5 | 326 | 46 |
| Bash | natural | fs-mutate | plain | 288 | 29 | 9.9 | 288 | 39 |
| Bash | arena | python/uv | plain | 255 | 27 | 9.4 | 161 | 189 |
| Bash | arena | fs-mutate | plain | 241 | 26 | 9.3 | 241 | 177 |
| Bash | arena | other | plain | 236 | 26 | 9.1 | 118 | 125 |
| Bash | natural | git | risky | 225 | 26 | 8.7 | 225 | 31 |
| Bash | natural | agent-cli | plain | 173 | 22 | 7.9 | 163 | 51 |
| WebSearch | natural | - | plain | 123 | 19 | 6.5 | 123 | 9 |
| Bash | natural | process | risky | 113 | 25 | 4.5 | 98 | 18 |
| WebFetch | natural | - | plain | 102 | 17 | 6.0 | 91 | 13 |
| Bash | arena | read-shell | risky | 102 | 25 | 4.1 | 71 | 84 |
| Bash | natural | heredoc | plain | 100 | 17 | 5.9 | 100 | 19 |
| Bash | arena | git | plain | 94 | 17 | 5.5 | 39 | 86 |
| Write | natural | - | plain | 88 | 16 | 5.5 | 83 | 10 |
| Bash | natural | build/toolchain | plain | 60 | 13 | 4.6 | 60 | 7 |
| Bash | natural | heredoc | risky | 50 | 25 | 2.0 | 49 | 15 |
| Bash | arena | search | plain | 43 | 11 | 3.9 | 29 | 39 |
| WebFetch | arena | - | plain | 35 | 10 | 3.5 | 14 | 4 |
| Bash | natural | network | risky | 24 | 24 | 1.0 | 24 | 8 |
| Bash | natural | remote | risky | 21 | 21 | 1.0 | 21 | 1 |
| Edit | natural | - | plain | 21 | 8 | 2.6 | 13 | 5 |
| Bash | natural | gh | risky | 20 | 20 | 1.0 | 20 | 9 |
| Bash | natural | agent-cli | risky | 19 | 19 | 1.0 | 19 | 16 |
| MCP | arena | - | plain | 19 | 8 | 2.4 | 9 | 15 |
| Write | natural | - | risky | 12 | 12 | 1.0 | 12 | 2 |
| Edit | natural | - | risky | 12 | 12 | 1.0 | 8 | 3 |
| Bash | natural | gh | plain | 11 | 8 | 1.4 | 11 | 5 |
| Bash | arena | fs-mutate | risky | 10 | 10 | 1.0 | 10 | 6 |
| WebSearch | arena | - | plain | 8 | 8 | 1.0 | 7 | 3 |
| Bash | arena | process | risky | 7 | 7 | 1.0 | 6 | 7 |
| Bash | arena | search | risky | 6 | 6 | 1.0 | 6 | 5 |
| Bash | arena | other | risky | 5 | 5 | 1.0 | 5 | 3 |
| Bash | arena | heredoc | plain | 5 | 5 | 1.0 | 5 | 5 |
| Bash | natural | build/toolchain | risky | 4 | 4 | 1.0 | 4 | 3 |
| Bash | arena | python/uv | risky | 2 | 2 | 1.0 | 2 | 2 |
| Bash | arena | network | risky | 1 | 1 | 1.0 | 1 | 1 |

## marginals (N / n)

- tool family: Bash 26248 / 1266; other 1670 / 98; Agent 1129 / 79; MCP 1077 / 63; WebFetch 137 / 27; WebSearch 131 / 27; Write 100 / 28; Edit 33 / 20
- source: natural 19105 / 1120; arena 11420 / 488
- risk: plain 25776 / 1131; risky 4749 / 477

## refusals file

- classifier_block 67; interrupted_by_safety_classifier 1; classifier_unavailable 39
- by (decider, recorded-decision era): classifier_block pre-era 44; interrupted_by_safety_classifier era 1; classifier_unavailable era 27; classifier_unavailable pre-era 12; classifier_block era 23
- classifier_block by tool: {'Bash': 57, 'MCP': 4, 'Write': 2, 'Agent': 2, 'other': 2}
- classifier_block by source: {'natural': 67}

## inferred allows (pre-2.1.293, auto mode seen, no decision record, tool result not an error)

- N = 26305 by tool: {'Bash': 21239, 'Write': 1260, 'Agent': 983, 'Edit': 2552, 'WebFetch': 271}; sample written: 300
