## 1. Worker context USD by source class (68 workers, waves 4-7)

Context USD = cache reads + cache writes (5 min and 1 hour rates as recorded) + uncached input, at list price, of every request; output tokens are left out (the transcripts hold the output count at the start of the stream, so it is not usable). Total USD 83.69. Each element's USD is the sum over the requests that carried it (see the method in the report).

| source class | elements | est. tokens | first write | reads | re-writes after a pause | total USD | share |
|:--|--:|--:|--:|--:|--:|--:|--:|
| Read of source code | 23 | 190,305 | 0.48 | 1.54 | 0.52 | 2.53 | 3.0% |
| Read of a non-lab document | 2 | 62,973 | 0.07 | 0.32 | 0.07 | 0.45 | 0.5% |
| the agent's own turns: thinking blocks | 3617 | 2,160,867 | 5.37 | 9.99 | 3.46 | 18.82 | 22.5% |
| Read of a lab document | 115 | 440,912 | 1.10 | 2.51 | 0.69 | 4.31 | 5.1% |
| cat/sed/head/tail of source code in Bash | 373 | 636,386 | 1.59 | 4.01 | 1.09 | 6.70 | 8.0% |
| the agent's own turns: tool calls (input text) | 3617 | 2,129,127 | 5.31 | 7.76 | 2.84 | 15.92 | 19.0% |
| cat/sed/head/tail of a document in Bash | 472 | 850,450 | 2.13 | 4.26 | 0.83 | 7.22 | 8.6% |
| system prompt and tool schemas (base) | 68 | 337,454 | 0.26 | 1.54 | 0.01 | 1.81 | 2.2% |
| worker's own code run (scratch script, inline python) | 1083 | 934,625 | 2.34 | 3.80 | 1.14 | 7.28 | 8.7% |
| messages, resume prompts, task notices | 344 | 422,340 | 1.06 | 1.88 | 0.40 | 3.34 | 4.0% |
| search results (colgrep, grep, find) | 241 | 246,007 | 0.59 | 0.94 | 0.20 | 1.73 | 2.1% |
| lab script output (scripts/, __instrumenta__/) | 470 | 437,618 | 1.09 | 1.49 | 0.48 | 3.07 | 3.7% |
| other tool results (edits, ToolSearch, mkdir, ls ...) | 859 | 402,694 | 0.99 | 1.58 | 0.52 | 3.09 | 3.7% |
| git output | 171 | 123,763 | 0.31 | 0.44 | 0.10 | 0.85 | 1.0% |
| web or MCP results | 67 | 137,980 | 0.17 | 0.19 | 0.02 | 0.38 | 0.4% |
| harness text at start (instructions, session context, tool lists) | 628 | 322,096 | 0.80 | 1.64 | 0.33 | 2.77 | 3.3% |
| hook-injected text (additionalContext, total_tokens reminders) | 3692 | 209,621 | 0.52 | 0.98 | 0.27 | 1.76 | 2.1% |
| ToolSearch results (tool schemas) | 74 | 150,274 | 0.38 | 0.46 | 0.09 | 0.92 | 1.1% |
| the brief (first prompt) | 68 | 85,394 | 0.16 | 0.49 | 0.06 | 0.71 | 0.8% |
| the agent's own turns: text and per-turn wrapper | 3617 | 8,287 | 0.02 | 0.02 | 0.01 | 0.04 | 0.1% |

Of the total, tool results (all rows whose tool is a call, not the base, the agent's own output, hook text, messages) are USD 38.53 (46.0%); re-writes after a pause are USD 13.12 (15.7% of all).

## 1b. By wave (USD, share of that wave's context USD)

| source class | w4 | w5 | w6 | w7 |
|:--|--:|--:|--:|--:|
| Read of source code | 0.89 (5%) | 0.58 (4%) | 0.53 (2%) | 0.53 (2%) |
| Read of a non-lab document | 0.00 (0%) | 0.00 (0%) | 0.45 (2%) | 0.00 (0%) |
| the agent's own turns: thinking blocks | 3.91 (23%) | 3.19 (21%) | 7.37 (25%) | 4.35 (20%) |
| Read of a lab document | 1.40 (8%) | 1.04 (7%) | 0.80 (3%) | 1.06 (5%) |
| cat/sed/head/tail of source code in Bash | 1.31 (8%) | 1.23 (8%) | 2.74 (9%) | 1.43 (7%) |
| the agent's own turns: tool calls (input text) | 3.38 (20%) | 2.23 (15%) | 6.24 (21%) | 4.06 (19%) |
| cat/sed/head/tail of a document in Bash | 0.78 (4%) | 1.35 (9%) | 2.72 (9%) | 2.37 (11%) |
| system prompt and tool schemas (base) | 0.29 (2%) | 0.32 (2%) | 0.56 (2%) | 0.65 (3%) |
| worker's own code run (scratch script, inline python) | 1.63 (9%) | 1.47 (10%) | 2.30 (8%) | 1.87 (9%) |
| messages, resume prompts, task notices | 0.80 (5%) | 0.65 (4%) | 1.01 (3%) | 0.88 (4%) |
| search results (colgrep, grep, find) | 0.23 (1%) | 0.34 (2%) | 0.68 (2%) | 0.48 (2%) |
| lab script output (scripts/, __instrumenta__/) | 0.78 (5%) | 0.52 (3%) | 0.88 (3%) | 0.89 (4%) |
| other tool results (edits, ToolSearch, mkdir, ls ...) | 0.40 (2%) | 0.58 (4%) | 1.36 (5%) | 0.76 (4%) |
| git output | 0.13 (1%) | 0.27 (2%) | 0.30 (1%) | 0.16 (1%) |
| web or MCP results | 0.00 (0%) | 0.06 (0%) | 0.12 (0%) | 0.19 (1%) |
| harness text at start (instructions, session context, tool lists) | 0.65 (4%) | 0.58 (4%) | 0.73 (2%) | 0.81 (4%) |
| hook-injected text (additionalContext, total_tokens reminders) | 0.38 (2%) | 0.33 (2%) | 0.61 (2%) | 0.44 (2%) |
| ToolSearch results (tool schemas) | 0.21 (1%) | 0.16 (1%) | 0.34 (1%) | 0.21 (1%) |
| the brief (first prompt) | 0.12 (1%) | 0.13 (1%) | 0.22 (1%) | 0.24 (1%) |
| the agent's own turns: text and per-turn wrapper | 0.00 (0%) | 0.01 (0%) | 0.03 (0%) | 0.01 (0%) |
| total | 17.28 | 15.03 | 29.99 | 21.39 |

## 2. Lab documents by kind and route (Read vs Bash cat/sed/head/tail)

| document kind | route | results | est. tokens (mean per result) | USD | share of all context USD | read in part (offset/limit) |
|:--|:--|--:|--:|--:|--:|--:|
| report | Bash | 102 | 2,447 | 2.10 | 2.5% | 0 |
| claim file | Bash | 157 | 1,560 | 2.08 | 2.5% | 0 |
| claim file | Read | 24 | 5,206 | 1.36 | 1.6% | 0 |
| report | Read | 32 | 3,717 | 1.26 | 1.5% | 0 |
| framing | Read | 34 | 3,662 | 1.06 | 1.3% | 0 |
| framing | Bash | 20 | 4,572 | 0.96 | 1.2% | 0 |
| other document | Bash | 75 | 993 | 0.52 | 0.6% | 0 |
| other document | Read | 2 | 31,486 | 0.45 | 0.5% | 0 |
| report data (tsv/json/py) | Bash | 20 | 2,413 | 0.43 | 0.5% | 0 |
| wave note | Read | 12 | 3,840 | 0.42 | 0.5% | 0 |
| wave note | Bash | 11 | 4,538 | 0.37 | 0.4% | 0 |
| brief protocol (skills/agents/templates) | Bash | 28 | 1,594 | 0.30 | 0.4% | 0 |
| synthesis | Bash | 4 | 4,025 | 0.25 | 0.3% | 0 |
| puzzle file | Bash | 41 | 374 | 0.14 | 0.2% | 0 |
| report data (tsv/json/py) | Read | 3 | 4,460 | 0.07 | 0.1% | 0 |
| puzzle file | Read | 4 | 1,614 | 0.07 | 0.1% | 0 |
| brief protocol (skills/agents/templates) | Read | 6 | 1,100 | 0.07 | 0.1% | 0 |
| statera other | Bash | 6 | 1,746 | 0.05 | 0.1% | 0 |
| harness log | Bash | 6 | 564 | 0.02 | 0.0% | 0 |
| user_words | Bash | 2 | 967 | 0.01 | 0.0% | 0 |
| all documents | | 589 | | 11.98 | 14.3% | |

Bash document reads by command word: cat 275 results USD 4.15; sed 108 results USD 1.75; head 32 results USD 0.73; wc 20 results USD 0.21; cut 7 results USD 0.18; awk 6 results USD 0.09; tail 18 results USD 0.08; sort 1 results USD 0.01; diff 4 results USD 0.01; jq 1 results USD 0.00

## 3. The 20 costliest documents and scripts (aggregated over workers; wave notes merged into one row, kind | path)

| rank | type | what | results | workers | mean est. tokens | USD | share | of which re-writes |
|--:|:--|:--|--:|--:|--:|--:|--:|--:|
| 1 | script | inline python/heredoc | 841 | 65 | 834 | 5.41 | 6.5% | 0.87 |
| 2 | document | framing | __design__/framing.md | 52 | 50 | 3,975 | 1.93 | 2.3% | 0.22 |
| 3 | script | own scratch script | 136 | 24 | 878 | 0.95 | 1.1% | 0.15 |
| 4 | script | inline python -c | 106 | 43 | 1,076 | 0.91 | 1.1% | 0.12 |
| 5 | document | claim file | __pondus__/w04-c5.md | 9 | 5 | 7,072 | 0.86 | 1.0% | 0.07 |
| 6 | document | wave note | __statera__/wave-NN.md | 20 | 16 | 3,893 | 0.63 | 0.8% | 0.04 |
| 7 | document | other document | blgpdcaey.txt | 1 | 1 | 26,304 | 0.45 | 0.5% | 0.07 |
| 8 | document | report | __reports__/wave-06/explorer-w06-b/00-findings_v0.md | 4 | 4 | 6,981 | 0.38 | 0.5% | 0.04 |
| 9 | document | report | __reports__/reflective_run/w04/00-experiment_protocol_v0.md | 16 | 10 | 2,200 | 0.35 | 0.4% | 0.08 |
| 10 | document | claim file | __pondus__/w03-c1.md | 1 | 1 | 12,810 | 0.32 | 0.4% | 0.16 |
| 11 | document | synthesis | __statera__/synthesis.md | 4 | 4 | 4,025 | 0.25 | 0.3% | 0.08 |
| 12 | document | report | __reports__/wave-05/explorer-w05-d/00-findings_v0.md | 3 | 3 | 5,666 | 0.20 | 0.2% | 0.04 |
| 13 | document | claim file | __pondus__/w05-c4.md | 7 | 3 | 3,118 | 0.20 | 0.2% | 0.01 |
| 14 | script | __instrumenta__/w06c7_e3_report.py | 3 | 1 | 2,705 | 0.19 | 0.2% | 0.04 |
| 15 | document | claim file | __pondus__/w06-c3.md | 6 | 3 | 2,260 | 0.17 | 0.2% | 0.02 |
| 16 | script | __instrumenta__/e3_measure.py | 7 | 1 | 3,025 | 0.17 | 0.2% | 0.01 |
| 17 | document | claim file | __reports__/wave-07/explorer-w07-c/00-findings_v0.md | 1 | 1 | 11,683 | 0.17 | 0.2% | 0.03 |
| 18 | document | claim file | __pondus__/w03-c2.md | 1 | 1 | 9,393 | 0.15 | 0.2% | 0.02 |
| 19 | document | claim file | __pondus__/w06-c9.md | 6 | 4 | 2,312 | 0.14 | 0.2% | 0.03 |
| 20 | script | __instrumenta__/w07f_binary_window.py | 11 | 1 | 2,018 | 0.14 | 0.2% | 0.00 |

Separately, the 10 costliest lab scripts only:

| rank | script | results | workers | mean est. tokens | USD | share of lab-script USD |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | __instrumenta__/w06c7_e3_report.py | 3 | 1 | 2,705 | 0.19 | 6.1% |
| 2 | __instrumenta__/e3_measure.py | 7 | 1 | 3,025 | 0.17 | 5.5% |
| 3 | __instrumenta__/w07f_binary_window.py | 11 | 1 | 2,018 | 0.14 | 4.5% |
| 4 | __instrumenta__/w06c9_timing.sh | 7 | 1 | 1,054 | 0.13 | 4.2% |
| 5 | __instrumenta__/hook_cost_summary.py | 10 | 3 | 1,015 | 0.12 | 3.9% |
| 6 | __instrumenta__/budget_arms_analyze.py | 10 | 1 | 731 | 0.10 | 3.2% |
| 7 | __instrumenta__/e3_reread_runs.py | 4 | 1 | 5,543 | 0.10 | 3.2% |
| 8 | __instrumenta__/w05c_summarize.py | 4 | 1 | 2,708 | 0.06 | 2.0% |
| 9 | __instrumenta__/w06c3_analyze.py | 6 | 1 | 1,045 | 0.06 | 1.9% |
| 10 | __instrumenta__/wave_worker_events.py | 2 | 1 | 6,111 | 0.06 | 1.9% |

Lab-script USD in all: 3.07 over 470 results (3.7% of all context USD).

## 4. ESTIMATE: ceiling saving if each output were capped, or a document read by section only

Formula: for an element with t tokens and context USD c (first write + reads + re-writes), a cap of K tokens leaves c x min(1, K/t), because every later request carries the element, so its whole cost is proportional to its tokens (same position in the life of the worker, same pauses). Saving = sum over capped elements of c x max(0, 1 - K/t). It is a ceiling: it assumes the cut text was not needed, that no extra call is made to get it, and that the worker's answer does not change. 'By section only' is the same formula with K = the section size read (a Read with offset and limit).

| group | elements | USD now | share | saving at cap 1,000 tokens | saving at cap 2,500 tokens | saving at cap 5,000 tokens | saving at cap 10,000 tokens | elements above 2,500 tokens |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| lab script output | 470 | 3.07 | 3.7% | 1.14 (1.4% of all) | 0.45 (0.5% of all) | 0.12 (0.1% of all) | 0.00 (0.0% of all) | 35 |
| documents, Read | 117 | 4.76 | 5.7% | 3.74 (4.5% of all) | 2.46 (2.9% of all) | 1.37 (1.6% of all) | 0.51 (0.6% of all) | 79 |
| documents, Bash cat/sed/head/tail | 472 | 7.22 | 8.6% | 5.24 (6.3% of all) | 3.28 (3.9% of all) | 1.35 (1.6% of all) | 0.10 (0.1% of all) | 125 |
| all documents (Read + Bash) | 589 | 11.98 | 14.3% | 8.98 (10.7% of all) | 5.74 (6.9% of all) | 2.73 (3.3% of all) | 0.61 (0.7% of all) | 204 |
| lab scripts + all documents | 1059 | 15.05 | 18.0% | 10.13 (12.1% of all) | 6.19 (7.4% of all) | 2.85 (3.4% of all) | 0.61 (0.7% of all) | 239 |
| source code (Read + Bash) | 396 | 9.23 | 11.0% | 6.53 (7.8% of all) | 4.16 (5.0% of all) | 2.20 (2.6% of all) | 0.73 (0.9% of all) | 104 |
| every tool result | 3950 | 38.53 | 46.0% | 22.82 (27.3% of all) | 13.06 (15.6% of all) | 5.89 (7.0% of all) | 1.42 (1.7% of all) | 542 |

## 5. Duplicate reads of one document by one worker (ceiling saving: every read after the first is not needed)

Repeat reads (same worker, same path, route Read or Bash): 131 results, USD 1.08 (1.3% of all context USD): report 0.40; claim file 0.32; framing 0.21; other document 0.06; wave note 0.06; brief protocol (skills/agents/templates) 0.02; harness log 0.01; puzzle file 0.00; report data (tsv/json/py) 0.00.

## 6. Position in the worker's life

Document results that entered in the first 4 requests: USD 8.49 (10.1% of all context USD; 71% of document USD).
Per worker: total context USD median 0.71, mean 1.23, max 9.09; document share of a worker's USD median 17%.

## 7. USD per 1,000 tokens of one tool result, by the request at which it entered (all tool results)

| entered at request | results | mean later requests | USD per 1,000 tokens (mean of sums) | of which re-write share |
|:--|--:|--:|--:|--:|
| 1-3 | 357 | 51 | 0.0088 | 13% |
| 4-10 | 512 | 48 | 0.0094 | 15% |
| 11-30 | 1316 | 36 | 0.0074 | 14% |
| 31-60 | 965 | 37 | 0.0072 | 18% |
| 61-1000 | 798 | 46 | 0.0089 | 22% |

A document of 23,000 tokens read at request 2 would, at the first bucket's rate, cost USD 0.20 in the life of one worker (ESTIMATE: tokens x USD per token of the bucket).
