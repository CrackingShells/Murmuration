## S-w06-explorer-w06-b-1
Bare, a Rust binary starts in 51 ms against 33 ms for `sh :` and 58 ms for `python3 -S -I -c pass`; as the platform records it, Rust is 58 to 70 ms against 65 for `-S -I`. Nothing I measured says a compiled hook starts nearer the shell floor, and I do not know why 18 ms is spent between `sh` and a 340 KB static-ish executable (dyld, Rust runtime init, macOS signature check on each exec?). If code signing or runtime init is the cost, a smaller or differently linked binary may change the whole comparison.
refs: __reports__/wave-06/explorer-w06-b/bare_n60.jsonl; __reports__/wave-06/explorer-w06-b/inter_partial_table.md

## S-w06-explorer-w06-b-2
`mcp_tool` hooks cost 2 ms per event, 40 times less than any process start, and the lab's own platform probe measured it in the design session (row 5 and 6 of the probe report) and then the v6 cut dropped it with SA1 and SA15 without a number against the hooks' real cost. Whether a bundled `.mcp.json` server breaks the agents' allowlists (SA15's reason) was never tested against `mcp_tool` hooks specifically: the hook calls the server, the model need not see the tool.
refs: __reports__/platform_probes/01-findings_v1.md (rows 5, 6, 26); __reports__/wave-06/explorer-w06-b/inter_partial_table.md

## S-w06-explorer-w06-b-3
Both lean builds were judged by wall-time thresholds (50%) written before anyone had measured the platform's own floor of 38 to 60 ms per start. A start that cannot be below 38 ms cannot be cut by 50% from 90, so E4 and E7 had a built-in ceiling. Would the verdicts have been the same if the rules had been written on CPU time, where w04-c5 reached -78 to -91%?
refs: __pondus__/w04-c5.md (Decision); __pondus__/w05-c4.md (m2, m3); __reports__/wave-06/explorer-w06-b/bare_n60.jsonl

## S-w06-explorer-w06-b-4
The inventory could not price `user_words.py`: explorer-w05-d's counter shows 0 starts for it in wave 4, but it fires on every prompt including each task notification (one per hand-back), so wave 4 had at least 29 of them. Nobody has counted prompts per wave.
refs: __reports__/wave-05/explorer-w05-d/starts_wave4_pi_session.json ("UserPromptSubmit||user_words.py": 0); scripts/user_words.py (NON_USER_PREFIXES)

## S-w06-explorer-w06-b-5
The interleaved probe for mcp_tool and the other variants ran on a machine with load average 4.6 to 5.7 from other agents, and its first session was cut at my 280 s timeout. The ordering (sh 38 < Rust 58-70 about python -S -I 65 < python 75 < budget.py 104 << mcp_tool 2) looks stable between the two sessions, but the Rust-versus-Python gap is inside the noise. A rerun on an idle machine with 5 sessions would settle it for about USD 0.15.
refs: __reports__/wave-06/explorer-w06-b/rows3_try.jsonl; __reports__/wave-06/explorer-w06-b/rows4_partial.json; __reports__/wave-06/explorer-w06-b/platform_unpaired_table.md
