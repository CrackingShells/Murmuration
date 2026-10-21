## S-w05-author-w05-2-1
The Agent tool of the 2.1.304 headless build has no `name` property (`description, prompt, subagent_type, model, effort, run_in_background, isolation`), and both PIs in the smoke runs said so. The Desktop wave-4 PI (2.1.299) did pass `name` (second of its first two Agent calls; `description, name, prompt, run_in_background, subagent_type`). The lab's briefs, `SendMessage` by name and the whole naming scheme of the research-loop skill assume the field exists. If the `claude` on PATH or a later Desktop drops it, naming silently moves into prompt text and `SendMessage(to: name)` has no target. Which version removed it, and is it only headless?
refs: /private/tmp/murmuration-w05/author-w05-2/runs/A1/stdout.jsonl (init and PI text); prompt_snapshot attachment in ~/.claude/projects/-private-tmp-murmuration-w05-author-w05-2-runs-A1-lab/*.jsonl; wave-4 transcript c533f1c6… Agent tool_use inputs

## S-w05-author-w05-2-2
`mcp__*` in a `tools:` line matches nothing, while `mcp__dummy__*` matches the one tool of that server, and entries the build does not know (`Foo`, `Glob`, `TodoWrite`) are ignored without any message. A list written in good faith can therefore lose tools silently (the PI answers "I have no such tool" instead of the harness saying the name was dropped). Nothing in the plugin checks a `tools:` line against the tools that arrive at request 0. A selftest that reads `init.tools` from one headless run and compares with the line would catch a typo, a renamed tool or a new app server.
refs: __reports__/wave-05/author-w05-2/haiku_mechanics_probes.tsv (V1, V2, V3 rows); /private/tmp/murmuration-w05/author-w05-2/p_V1/out.jsonl

## S-w05-author-w05-2-3
Naming a tool in `tools:` can add a tool the default set lacks: `WebFetch` is not in A's tool list (29 tools) and is in B's (21). So `tools:` is not only a filter; in this build it is also a switch for tools that are off by default. I did not test it for other names (`Glob`, `Grep`, `TodoWrite`), which stayed absent, so it is not general. What decides which names switch on?
refs: __reports__/wave-05/author-w05-2/e6_table_A_B.tsv (init_tools column); /private/tmp/murmuration-w05/author-w05-2/runs/B1/stdout.jsonl vs runs/A1/stdout.jsonl, init record

## S-w05-author-w05-2-4
The headless request 0 is 30.5k tokens in A where the Desktop wave-4 PI had 74.6k. Of the 44k difference I can name only the Desktop's MCP schemas (Claude_Browser 31.5k characters, ccd_turn and ccd_session 17.6k, iOS Simulator 6.9k, visualize 5.4k, docs 2.6k: about 64k characters, about 14k to 22k tokens at 0.211 to 0.342). The rest, about 22k to 30k tokens, I cannot account for: the Desktop's deferred-name list (213 names), MCP server instructions, hook and memory text, a longer listing? explorer-w05-b's composition (218k characters, of which tools 186.6k) does not separate these. The Desktop projection (26.8k to 43.5k tokens) rests on the tool schemas alone and so does not depend on this, but the "base would be 31k to 48k" line does.
refs: __reports__/wave-05/author-w05-2/desktop_projection_B_allowlist.txt; __reports__/wave-05/explorer-w05-b/wave4_categories.tsv

## S-w05-author-w05-2-5
The margin of the registered m1 rule was 497 tokens (15,497 against 15,000), and the rule is a cliff: a list that kept `Workflow` (9.1k characters, about 2k tokens) would have scored 13.5k and failed, with the same smoke result. The 15,000 figure was chosen before the headless token-per-character ratio (0.211) was known. For the Desktop the saving is projected at 27k to 44k, so the threshold is not the right test there; it only tests that `tools:` is honoured. Should the rule have been a ratio of the schema characters removed, or a test of the mechanism (any reduction plus a passing smoke)?
refs: __pondus__/w05-c3.md (result table, "Not covered"); __reports__/wave-05/00-experiment_protocol_v0.md (E6 decision rule)

## S-w05-author-w05-2-6
Allowlist or denylist is a real design choice that E6 did not register. The allowlist (B, proposed by the rule) is lean against future app tools and loses every user-attached MCP server whose name the plugin cannot know (GitHub and file-storage connectors have uuid names, so they cannot even be written as a portable wildcard). The denylist keeps all of them, removes within 3.4% of the same characters on the Desktop snapshot, and lets a new app tool in. The brief for this claim asked that "a PI on any open research project keeps every tool it needs"; only the denylist meets that for connectors. I left B on the branch tip because the rule says so and say here that I would put the question of B against D to the principal investigator before it is merged.
refs: __pondus__/w05-c3.md ("An alternative that meets that aim better"); __reports__/wave-05/author-w05-2/desktop_projection_Dprime_denylist.txt; e6_table_D_exploratory.tsv

## S-w05-author-w05-2-7
The cold pilot pair cost USD 0.4026 (A) and 0.2435 (B), the warm registered pairs 0.18 and 0.16: the difference between arms in the money of one request-0 write is large, but the difference over a whole run is small because a smoke task of 9 to 11 requests is dominated by what one cache write costs. In a wave-length PI session (114 requests, per explorer-w05-b) the same 15k tokens are re-read 113 times; I did not measure it, only projected it. Is a per-request carry model good enough for the decision, or does the first request after every cache lapse (the 1-hour limit) matter more for the PI than the reads?
refs: __reports__/wave-05/author-w05-2/e6_costs_per_run.tsv; __reports__/wave-05/explorer-w05-b/00-findings_v0.md (cache rows)

## S-w05-author-w05-2-8
In every smoke run the tiny explorer was stopped once by the SubagentHandback hook ("your findings report is not yet at __reports__/explorer-smoke/00-findings_v0.md. Write it there …"), although the PI's brief said "Write no file" and the task was a one-line answer. The hook's demand is the explorer role's deliverable rule, applied to a probe that has none. A tiny worker therefore pays an extra write-and-handback round. Not an E6 matter, but it is a cost per dispatch that the gate adds to cheap tasks.
refs: /private/tmp/murmuration-w05/author-w05-2/runs/B1/stdout.jsonl (the `PreToolUse:SubagentHandback hook error` tool_result with agent_id); scripts/handback.py

## S-w05-author-w05-2-9
In E6b, cell a6D3 took 145.7 s of wall time against 53 to 72 s for the other five, with the same token counts (request 0 14,841, 10 requests) and a normal cost (0.1740). Nothing in the table explains 90 extra seconds. A hook, a slow explorer, or a wait in the platform? I did not open the transcript timestamps.
refs: /private/tmp/murmuration-w05/author-w05-2/runs/a6D3/stdout.jsonl; __reports__/wave-05/author-w05-2/e6b_costs_per_run.tsv

## S-w05-author-w05-2-10
Both E6 and E6b pass their rules, and the two passes differ by only about 1k to 1.5k tokens on the Desktop projection. The threshold of 15,000 was met by 497 (B) and 687 (D) tokens. A rule built as "at least X tokens" could not tell a list that is lean from one that merely drops the one big schema (Artifact is 74% of everything either line removes); the real decision between B and D was about connectors and future tools, which only the E6b addendum made visible, after the fact. What metric would have forced that question in the first protocol?
refs: __pondus__/w05-c3.md; __pondus__/w05-c6.md; __reports__/wave-05/00-experiment_protocol_v1.md
