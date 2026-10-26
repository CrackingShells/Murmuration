# strata of recorded classifier allows (version >= 2.1.293)

population N = 30663; sample n = 1603; seed 20261024; allocation n_h = min(N_h, max(floor, round(1500 * sqrt(N_h) / sum sqrt(N)))), floor 8 (25 for risky-word strata)

| tool family | source | Bash command family | risk words | N_h | n_h | weight N_h/n_h | unique texts (digits and uuids masked) | sessions |
|:--|:--|:--|:--|--:|--:|--:|--:|--:|
| Bash | arena | read-shell | plain | 8017 | 152 | 52.7 | 628 | 740 |
| Bash | natural | read-shell | plain | 5109 | 122 | 41.9 | 3871 | 134 |
| Bash | natural | python/uv | plain | 2281 | 81 | 28.2 | 2272 | 46 |
| Bash | natural | read-shell | risky | 1734 | 71 | 24.4 | 1598 | 87 |
| Bash | natural | git | plain | 1213 | 59 | 20.6 | 1194 | 71 |
| Bash | natural | other | plain | 1200 | 59 | 20.3 | 1194 | 45 |
| Bash | natural | python/uv | risky | 1079 | 56 | 19.3 | 1072 | 62 |
| MCP | natural | - | plain | 1069 | 56 | 19.1 | 921 | 81 |
| other | natural | - | plain | 914 | 51 | 17.9 | 868 | 104 |
| Bash | natural | search | plain | 885 | 51 | 17.4 | 879 | 45 |
| Bash | arena | process | plain | 830 | 49 | 16.9 | 30 | 127 |
| other | arena | - | plain | 761 | 47 | 16.2 | 652 | 566 |
| Agent | arena | - | plain | 743 | 46 | 16.2 | 207 | 583 |
| Bash | natural | other | risky | 615 | 42 | 14.6 | 610 | 48 |
| Bash | natural | process | plain | 592 | 41 | 14.4 | 332 | 51 |
| Agent | natural | - | plain | 391 | 34 | 11.5 | 334 | 108 |
| Bash | natural | fs-mutate | risky | 367 | 33 | 11.1 | 367 | 49 |
| Bash | natural | search | risky | 327 | 31 | 10.5 | 327 | 46 |
| Bash | natural | fs-mutate | plain | 292 | 29 | 10.1 | 292 | 39 |
| Bash | arena | python/uv | plain | 255 | 27 | 9.4 | 161 | 189 |
| Bash | arena | fs-mutate | plain | 241 | 26 | 9.3 | 241 | 177 |
| Bash | arena | other | plain | 236 | 26 | 9.1 | 118 | 125 |
| Bash | natural | git | risky | 228 | 26 | 8.8 | 228 | 33 |
| Bash | natural | agent-cli | plain | 173 | 22 | 7.9 | 163 | 51 |
| WebSearch | natural | - | plain | 123 | 19 | 6.5 | 123 | 9 |
| Bash | natural | process | risky | 115 | 25 | 4.6 | 100 | 19 |
| WebFetch | natural | - | plain | 102 | 17 | 6.0 | 91 | 13 |
| Bash | arena | read-shell | risky | 102 | 25 | 4.1 | 71 | 84 |
| Bash | natural | heredoc | plain | 100 | 17 | 5.9 | 100 | 19 |
| Bash | arena | git | plain | 94 | 16 | 5.9 | 39 | 86 |
| Write | natural | - | plain | 88 | 16 | 5.5 | 83 | 10 |
| Bash | natural | build/toolchain | plain | 60 | 13 | 4.6 | 60 | 7 |
| Bash | natural | heredoc | risky | 50 | 25 | 2.0 | 49 | 15 |
| Bash | arena | search | plain | 43 | 11 | 3.9 | 29 | 39 |
| WebFetch | arena | - | plain | 35 | 10 | 3.5 | 14 | 4 |
| Bash | natural | network | risky | 24 | 24 | 1.0 | 24 | 8 |
| Bash | natural | gh | risky | 21 | 21 | 1.0 | 21 | 10 |
| Bash | natural | remote | risky | 21 | 21 | 1.0 | 21 | 1 |
| Edit | natural | - | plain | 21 | 8 | 2.6 | 13 | 5 |
| Bash | natural | agent-cli | risky | 19 | 19 | 1.0 | 19 | 16 |
| MCP | arena | - | plain | 19 | 8 | 2.4 | 9 | 15 |
| Bash | natural | gh | plain | 11 | 8 | 1.4 | 11 | 5 |
| Bash | arena | fs-mutate | risky | 10 | 10 | 1.0 | 10 | 6 |
| Write | natural | - | risky | 8 | 8 | 1.0 | 8 | 1 |
| WebSearch | arena | - | plain | 8 | 8 | 1.0 | 7 | 3 |
| Edit | natural | - | risky | 7 | 7 | 1.0 | 6 | 2 |
| Bash | arena | process | risky | 7 | 7 | 1.0 | 6 | 7 |
| Bash | arena | search | risky | 6 | 6 | 1.0 | 6 | 5 |
| Bash | arena | other | risky | 5 | 5 | 1.0 | 5 | 3 |
| Bash | arena | heredoc | plain | 5 | 5 | 1.0 | 5 | 5 |
| Bash | natural | build/toolchain | risky | 4 | 4 | 1.0 | 4 | 3 |
| Bash | arena | python/uv | risky | 2 | 2 | 1.0 | 2 | 2 |
| Bash | arena | network | risky | 1 | 1 | 1.0 | 1 | 1 |

## marginals (N / n)

- tool family: Bash 26374 / 1268; other 1675 / 98; Agent 1134 / 80; MCP 1088 / 64; WebFetch 137 / 27; WebSearch 131 / 27; Write 96 / 24; Edit 28 / 15
- source: natural 19243 / 1116; arena 11420 / 487
- risk: plain 25911 / 1134; risky 4752 / 469

## refusals file

- classifier_block 67; interrupted_by_safety_classifier 1; classifier_unavailable 38
- by (decider, recorded-decision era): classifier_block pre-era 44; interrupted_by_safety_classifier era 1; classifier_unavailable era 26; classifier_unavailable pre-era 12; classifier_block era 23
- classifier_block by tool: {'Bash': 57, 'MCP': 4, 'Write': 2, 'Agent': 2, 'other': 2}
- classifier_block by source: {'natural': 67}

## inferred allows (pre-2.1.293, auto mode seen, no decision record, tool result not an error)

- N = 26305 by tool: {'Bash': 21239, 'Write': 1260, 'Agent': 983, 'Edit': 2552, 'WebFetch': 271}; sample written: 300
