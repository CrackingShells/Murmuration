## run c1_window100k
visible requests 5, compact_boundary events 3, turns 8, total_cost_usd (haiku list) 0.0533793, wall in meta 57.8 s

context per visible request (input+read+write): 49820, 73797, 61709, 78859, 61592

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|
| 1 | auto | 80183 | 20930 | 11409 |
| 2 | auto | 76935 | 31856 | 12436 |
| 3 | auto | 82840 | 20724 | 9105 |

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | reactive-compact | 25644 | 2204 | 49818 | 330 | 0.159 |
| 2 | reactive-compact | 33986 | 2744 | 26635 | 3081 | 0.221 |
| 3 | reactive-compact | 50860 | 2093 | 26635 | 3357 | 0.277 |

reconciliation (input, output, read, write): total from result (110500, 9096, 257030, 178593); visible requests (10, 21, 153942, 171825); difference (110490, 9075, 103088, 6768); sum of forked-agent lines (110490, 7041, 103088, 6768)
autocompact lines: level=compact window=80000, level=ok window=80000
routing: [('reactive', 'env')]
bail lines: 1 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 3 injections, escaped-line lengths (chars) [394, 394, 394]
hooks.log events: SessionStart/startup, PreCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto

last PostCompact summary: 5479 chars; facts present verbatim: {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}
no resume run

## run c2_window100k
visible requests 6, compact_boundary events 3, turns 9, total_cost_usd (haiku list) 0.04795035, wall in meta 80.5 s

context per visible request (input+read+write): 49965, 63340, 65127, 66981, 66405, 0

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|
| 1 | auto | 71212 | 23621 | 11996 |
| 2 | auto | 73457 | 24233 | 9127 |
| 3 | auto | 74154 | 23781 | 9215 |

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | reactive-compact | 15164 | 2045 | 49963 | 208 | 0.113 |
| 2 | reactive-compact | 37450 | 1950 | 26635 | 3035 | 0.218 |
| 3 | reactive-compact | 39288 | 2184 | 26635 | 3051 | 0.231 |

reconciliation (input, output, read, write): total from result (91912, 7710, 257320, 164015); visible requests (10, 17, 154087, 157721); difference (91902, 7693, 103233, 6294); sum of forked-agent lines (91902, 6179, 103233, 6294)
autocompact lines: level=compact window=80000, level=ok window=80000, level=warn window=80000
routing: [('reactive', 'env')]
bail lines: 0 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 3 injections, escaped-line lengths (chars) [394, 394, 394]
resume_brief output on SessionStart:resume: 1 injections, lengths [394]
hooks.log events: SessionStart/startup, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, SessionStart/resume, PreCompact/auto, SessionStart/compact, PostCompact/auto

last PostCompact summary: 5025 chars; facts present verbatim: {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}
after --resume, model's answer (facts named verbatim): {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}

## run c3_window200k
visible requests 29, compact_boundary events 2, turns 31, total_cost_usd (haiku list) 0.36860910999999996, wall in meta 118.4 s

context per visible request (input+read+write): 50033, 63612, 75870, 87655, 99376, 111557, 123651, 134251, 144885, 155548, 166152, 66819, 78135, 88664, 99304, 109971, 120597, 131086, 141705, 152349, 162871, 66820, 78230, 88864, 99446, 110101, 120645, 131314, 141925

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|
| 1 | auto | 172979 | 24156 | 10922 |
| 2 | auto | 169701 | 24143 | 10260 |

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | reactive-compact | 12504 | 2275 | 155546 | 97 | 0.127 |
| 2 | reactive-compact | 12422 | 2246 | 152347 | 97 | 0.126 |

reconciliation (input, output, read, write): total from result (24984, 7984, 3115818, 393647); visible requests (58, 211, 2807925, 393453); difference (24926, 7773, 307893, 194); sum of forked-agent lines (24926, 4521, 307893, 194)
autocompact lines: level=compact window=180000, level=ok window=180000, level=warn window=180000
routing: [('reactive', 'env')]
bail lines: 0 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 2 injections, escaped-line lengths (chars) [394, 394]
resume_brief output on SessionStart:resume: 1 injections, lengths [394]
hooks.log events: SessionStart/startup, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, SessionStart/resume

last PostCompact summary: 6263 chars; facts present verbatim: {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}
after --resume, model's answer (facts named verbatim): {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}

## run c4_codes_w200k
visible requests 12, compact_boundary events 1, turns 13, total_cost_usd (haiku list) 0.152190875, wall in meta 66.1 s

context per visible request (input+read+write): 50039, 63502, 76512, 87113, 99024, 110457, 122452, 133000, 143591, 154216, 164766, 66956

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|
| 1 | auto | 171534 | 24144 | 10382 |

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | reactive-compact | 12450 | 2362 | 154214 | 97 | 0.129 |

reconciliation (input, output, read, write): total from result (12474, 4282, 1244957, 180958); visible requests (24, 148, 1090743, 180861); difference (12450, 4134, 154214, 97); sum of forked-agent lines (12450, 2362, 154214, 97)
autocompact lines: level=compact window=180000, level=ok window=180000, level=warn window=180000
routing: [('reactive', 'env')]
bail lines: 0 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 1 injections, escaped-line lengths (chars) [394]
resume_brief output on SessionStart:resume: 1 injections, lengths [394]
hooks.log events: SessionStart/startup, PreCompact/auto, SessionStart/compact, PostCompact/auto, SessionStart/resume

last PostCompact summary: 5937 chars; facts present verbatim: {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}
after --resume, model's answer (facts named verbatim): {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}

ref codes after --resume (files read: 11, total compactions 1)
| compactions after the file was read | files | exact code given | UNKNOWN | wrong code |
|--:|--:|--:|--:|--:|
| 0 | 0 | 0 | 0 | 0 |
| 1 | 11 | 10 | 1 | 0 |
codes present verbatim in last PostCompact summary: 9 of 28

## run c5_codes_precompact_w200k
visible requests 29, compact_boundary events 2, turns 31, total_cost_usd (haiku list) 0.38750008500000005, wall in meta 130.3 s

context per visible request (input+read+write): 50057, 62936, 75447, 86914, 97523, 109251, 119779, 132095, 142693, 153322, 164814, 67438, 78981, 89473, 100279, 110981, 121591, 132075, 142681, 153289, 163802, 66876, 78247, 88875, 99433, 110052, 120562, 131188, 141748

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|
| 1 | auto | 172535 | 24546 | 12751 |
| 2 | auto | 170621 | 24031 | 10422 |

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | reactive-compact | 13438 | 2654 | 153320 | 104 | 0.138 |
| 2 | reactive-compact | 12446 | 2422 | 153287 | 117 | 0.130 |

reconciliation (input, output, read, write): total from result (25942, 10734, 3106096, 393076); visible requests (58, 214, 2799489, 392855); difference (25884, 10520, 306607, 221); sum of forked-agent lines (25884, 5076, 306607, 221)
autocompact lines: level=compact window=180000, level=ok window=180000, level=warn window=180000
routing: [('reactive', 'env')]
bail lines: 0 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 2 injections, escaped-line lengths (chars) [394, 394]
resume_brief output on SessionStart:resume: 1 injections, lengths [394]
hooks.log events: SessionStart/startup, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, SessionStart/resume

last PostCompact summary: 5678 chars; facts present verbatim: {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}
after --resume, model's answer (facts named verbatim): {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}

ref codes after --resume (files read: 28, total compactions 2)
| compactions after the file was read | files | exact code given | UNKNOWN | wrong code |
|--:|--:|--:|--:|--:|
| 0 | 7 | 0 | 7 | 0 |
| 1 | 10 | 0 | 10 | 0 |
| 2 | 11 | 0 | 11 | 0 |
codes present verbatim in last PostCompact summary: 20 of 28

## run d1_plain
visible requests 29, compact_boundary events 2, turns 31, total_cost_usd (haiku list) 0.3691535799999999, wall in meta 115.7 s

context per visible request (input+read+write): 49772, 62238, 74604, 87482, 99876, 110391, 122132, 133651, 145767, 156388, 166934, 66556, 77958, 88465, 99067, 109681, 120252, 130708, 141325, 151912, 162401, 67061, 78404, 88971, 99505, 110116, 120618, 131236, 141788

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|
| 1 | auto | 173762 | 23958 | 10731 |
| 2 | auto | 169194 | 24206 | 11381 |

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | reactive-compact | 12450 | 2197 | 156386 | 93 | 0.126 |
| 2 | reactive-compact | 12393 | 2696 | 151910 | 93 | 0.135 |

reconciliation (input, output, read, write): total from result (24901, 8218, 3109867, 393816); visible requests (58, 295, 2801571, 393630); difference (24843, 7923, 308296, 186); sum of forked-agent lines (24843, 4893, 308296, 186)
autocompact lines: level=compact window=180000, level=ok window=180000, level=warn window=180000
routing: [('reactive', 'env')]
bail lines: 0 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 2 injections, escaped-line lengths (chars) [394, 394]
resume_brief output on SessionStart:resume: 1 injections, lengths [394]
hooks.log events: SessionStart/startup, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, SessionStart/resume, SessionStart/resume

last PostCompact summary: 6762 chars; facts present verbatim: {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}
after --resume, model's answer (facts named verbatim): {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}

ref codes after --resume (files read: 28, total compactions 2)
| compactions after the file was read | files | exact code given | UNKNOWN | wrong code |
|--:|--:|--:|--:|--:|
| 0 | 7 | 7 | 0 | 0 |
| 1 | 10 | 10 | 0 | 0 |
| 2 | 11 | 11 | 0 | 0 |
codes present verbatim in last PostCompact summary: 20 of 28

## run d1_precompact
visible requests 29, compact_boundary events 2, turns 31, total_cost_usd (haiku list) 0.37067684999999995, wall in meta 133.7 s

context per visible request (input+read+write): 50594, 64121, 76060, 86604, 98957, 109512, 121708, 132256, 143575, 154200, 164750, 67011, 78523, 89069, 99672, 110287, 120907, 131367, 141949, 152537, 163030, 67171, 78731, 89327, 99911, 110556, 121059, 131700, 142279

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|
| 1 | auto | 171543 | 24188 | 12921 |
| 2 | auto | 169855 | 24218 | 11877 |

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | reactive-compact | 12503 | 2784 | 154198 | 97 | 0.137 |
| 2 | reactive-compact | 12446 | 2889 | 152535 | 97 | 0.139 |

reconciliation (input, output, read, write): total from result (25007, 9730, 3111534, 392758); visible requests (58, 198, 2804801, 392564); difference (24949, 9532, 306733, 194); sum of forked-agent lines (24949, 5673, 306733, 194)
autocompact lines: level=compact window=180000, level=ok window=180000, level=warn window=180000
routing: [('reactive', 'env')]
bail lines: 0 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 2 injections, escaped-line lengths (chars) [394, 394]
resume_brief output on SessionStart:resume: 1 injections, lengths [394]
hooks.log events: SessionStart/startup, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, SessionStart/resume, SessionStart/resume

last PostCompact summary: 6630 chars; facts present verbatim: {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}
after --resume, model's answer (facts named verbatim): {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}

ref codes after --resume (files read: 28, total compactions 2)
| compactions after the file was read | files | exact code given | UNKNOWN | wrong code |
|--:|--:|--:|--:|--:|
| 0 | 7 | 7 | 0 | 0 |
| 1 | 10 | 10 | 0 | 0 |
| 2 | 11 | 11 | 0 | 0 |
codes present verbatim in last PostCompact summary: 20 of 28

## run d2_plain
visible requests 29, compact_boundary events 2, turns 31, total_cost_usd (haiku list) 0.36460044999999996, wall in meta 122.3 s

context per visible request (input+read+write): 50489, 64354, 76378, 86972, 97573, 108091, 118611, 129158, 139748, 151230, 161827, 65126, 76680, 87167, 97769, 108383, 118957, 129416, 139997, 150584, 161076, 65335, 76965, 87532, 98066, 108677, 119179, 129797, 140349

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|
| 1 | auto | 168618 | 23423 | 11119 |
| 2 | auto | 167869 | 23458 | 11198 |

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | reactive-compact | 12450 | 2363 | 151228 | 144 | 0.128 |
| 2 | reactive-compact | 12393 | 2735 | 150582 | 96 | 0.135 |

reconciliation (input, output, read, write): total from result (24901, 8960, 3061479, 385999); visible requests (58, 203, 2759669, 385759); difference (24843, 8757, 301810, 240); sum of forked-agent lines (24843, 5098, 301810, 240)
autocompact lines: level=compact window=180000, level=ok window=180000, level=warn window=180000
routing: [('reactive', 'env')]
bail lines: 0 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 2 injections, escaped-line lengths (chars) [394, 394]
resume_brief output on SessionStart:resume: 1 injections, lengths [394]
hooks.log events: SessionStart/startup, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, SessionStart/resume

last PostCompact summary: 6405 chars; facts present verbatim: {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}
after --resume, model's answer (facts named verbatim): {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}

ref codes after --resume (files read: 28, total compactions 2)
| compactions after the file was read | files | exact code given | UNKNOWN | wrong code |
|--:|--:|--:|--:|--:|
| 0 | 7 | 7 | 0 | 0 |
| 1 | 10 | 10 | 0 | 0 |
| 2 | 11 | 11 | 0 | 0 |
codes present verbatim in last PostCompact summary: 20 of 28

## run d2_precompact
visible requests 23, compact_boundary events 2, turns 25, total_cost_usd (haiku list) 0.3006858, wall in meta 108.8 s

context per visible request (input+read+write): 50928, 63882, 75995, 86539, 98420, 108939, 119460, 130008, 142350, 152975, 165200, 67695, 78592, 89129, 99767, 110414, 121018, 131478, 142084, 152695, 163210, 66727, 78138

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|
| 1 | auto | 172480 | 24658 | 15792 |
| 2 | auto | 170005 | 24024 | 11767 |

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | reactive-compact | 14178 | 3447 | 152973 | 97 | 0.157 |
| 2 | reactive-compact | 12446 | 2905 | 152693 | 119 | 0.139 |

reconciliation (input, output, read, write): total from result (26670, 9447, 2472210, 329269); visible requests (46, 159, 2166544, 329053); difference (26624, 9288, 305666, 216); sum of forked-agent lines (26624, 6352, 305666, 216)
autocompact lines: level=compact window=180000, level=ok window=180000, level=warn window=180000
routing: [('reactive', 'env')]
bail lines: 0 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 2 injections, escaped-line lengths (chars) [394, 394]
resume_brief output on SessionStart:resume: 1 injections, lengths [394]
hooks.log events: SessionStart/startup, PreCompact/auto, SessionStart/compact, PostCompact/auto, PreCompact/auto, SessionStart/compact, PostCompact/auto, SessionStart/resume

last PostCompact summary: 6871 chars; facts present verbatim: {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}
after --resume, model's answer (facts named verbatim): {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}

ref codes after --resume (files read: 22, total compactions 2)
| compactions after the file was read | files | exact code given | UNKNOWN | wrong code |
|--:|--:|--:|--:|--:|
| 0 | 1 | 1 | 0 | 0 |
| 1 | 10 | 10 | 0 | 0 |
| 2 | 11 | 11 | 0 | 0 |
codes present verbatim in last PostCompact summary: 20 of 28

## run e1_control_nocompact
visible requests 11, compact_boundary events 0, turns 11, total_cost_usd (haiku list) 0.12036907000000002, wall in meta 45.5 s

context per visible request (input+read+write): 52782, 64557, 76423, 87014, 97616, 108135, 118656, 129204, 139795, 150420, 160970

| compaction | trigger | pre_tokens | post_tokens | duration_ms |
|--:|:--|--:|--:|--:|

| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |
|--:|:--|--:|--:|--:|--:|--:|

reconciliation (input, output, read, write): total from result (22, 1509, 1048801, 136749); visible requests (22, 134, 1048801, 136749); difference (0, 1375, 0, 0); sum of forked-agent lines (0, 0, 0, 0)
autocompact lines: level=ok window=980000
routing: []
bail lines: 0 ("no assistant messages in summarize set")
resume_brief output on SessionStart:compact: 0 injections, escaped-line lengths (chars) []
resume_brief output on SessionStart:resume: 1 injections, lengths [394]
hooks.log events: SessionStart/startup, SessionStart/resume, SessionStart/resume

last PostCompact summary: 0 chars; facts present verbatim: {'number 48213': False, 'path /opt/zeta/config.toml': False, 'quote (heron ... blue ink)': False, 'audit code KX-9917': False}
after --resume, model's answer (facts named verbatim): {'number 48213': True, 'path /opt/zeta/config.toml': True, 'quote (heron ... blue ink)': True, 'audit code KX-9917': True}

ref codes after --resume (files read: 10, total compactions 0)
| compactions after the file was read | files | exact code given | UNKNOWN | wrong code |
|--:|--:|--:|--:|--:|
| 0 | 10 | 9 | 1 | 0 |
codes present verbatim in last PostCompact summary: 0 of 10

