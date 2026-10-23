## 1 spend per request, split (list price, Opus 5.5: input 4, output 20, read 0.20, write 5 min 5, write 1 h 8 USD per million)

| session | requests | wall | USD total | cache read (context already there) | fresh write (new tokens) | re-write (tokens already in context, not read) | output (billed) | uncached input | read % | fresh write % | re-write % | output % | tokens written 1h / 5m |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| s1_w1-3 | 393 | 13.0 h | 63.23 | 38.68 | 9.78 | 7.01 | 7.75 | 0.00 | 61% | 15% | 11% | 12% | 2.10 M / 0.00 M |
| s2_w4 | 114 | 1.5 h | 10.50 | 5.45 | 2.89 | 0.00 | 2.16 | 0.00 | 52% | 28% | 0% | 21% | 0.36 M / 0.00 M |
| s3_w5 | 153 | 5.0 h | 18.08 | 8.07 | 3.42 | 3.41 | 3.18 | 0.00 | 45% | 19% | 19% | 18% | 0.85 M / 0.00 M |
| s4_w6 | 232 | 7.7 h | 23.08 | 14.42 | 4.16 | 0.00 | 4.50 | 0.00 | 62% | 18% | 0% | 19% | 0.52 M / 0.00 M |
| s4b_w6small | 1 | 0.0 h | 0.24 | 0.00 | 0.24 | 0.00 | 0.00 | 0.00 | 0% | 100% | 0% | 0% | 0.03 M / 0.00 M |
| s5_w7 | 201 | 7.8 h | 27.14 | 13.98 | 4.44 | 3.76 | 4.96 | 0.00 | 52% | 16% | 14% | 18% | 1.03 M / 0.00 M |
| s6_w8 | 29 | 0.1 h | 2.20 | 0.55 | 1.09 | 0.00 | 0.56 | 0.00 | 25% | 50% | 0% | 25% | 0.14 M / 0.00 M |
| ALL | 1123 | 35.1 h | 144.47 | 81.15 | 26.02 | 14.19 | 23.11 | 0.01 | 56% | 18% | 10% | 16% | 5.03 M / 0.00 M |

Fresh write = write and input cost minus re-write cost. Re-write = tokens at positions below the previous request's context that were not read (positional model: the cache covers the first `cache_read` tokens). USD of misses (cache read under half the previous context, not a compaction) versus noise (small shortfalls at cache breakpoints):

| session | misses | USD re-written in misses | USD re-written, small shortfalls |
|:--|--:|--:|--:|
| s1_w1-3 | 5 | 7.01 | 0.01 |
| s2_w4 | 0 | 0.00 | 0.00 |
| s3_w5 | 1 | 3.41 | 0.00 |
| s4_w6 | 0 | 0.00 | 0.00 |
| s4b_w6small | 0 | 0.00 | 0.00 |
| s5_w7 | 1 | 3.76 | 0.00 |
| s6_w8 | 0 | 0.00 | 0.00 |
| ALL | 7 | 14.17 | 0.02 |

## 2 what put the context there: USD over each item's life (fresh write + every later cache read + re-writes)

| source | items | tokens entered | USD write (fresh) | USD later reads | USD re-writes | USD total | share of PI spend |
|:--|--:|--:|--:|--:|--:|--:|--:|
| billed output (all sessions) | 1123 |  | 0.00 | 0.00 | 0.00 | 23.11 | 16.0% |
| own thinking carried in context (inferred: step residual, see section 2b) | 852 | 567k | 4.53 | 11.61 | 2.61 | 18.76 | 13.0% |
| injected: skill listing (re-entered) | 29 | 325k | 2.59 | 11.65 | 0.54 | 14.78 | 10.2% |
| worker hand-back messages (peer)  | 187 | 380k | 3.04 | 8.53 | 0.98 | 12.55 | 8.7% |
| own output: tool calls | 724 | 306k | 2.45 | 5.37 | 1.18 | 9.00 | 6.2% |
| system prompt + tool definitions (prefix, not in transcript) | 7 | 189k | 1.52 | 6.42 | 0.52 | 8.45 | 5.8% |
| own output: dispatch briefs and messages | 148 | 180k | 1.44 | 4.34 | 0.54 | 6.32 | 4.4% |
| post-compaction context (summary + prefix) | 1 | 91k | 0.33 | 2.05 | 3.26 | 5.64 | 3.9% |
| tool result: Bash file view (cat/sed/head/tail) | 80 | 133k | 1.07 | 3.72 | 0.47 | 5.26 | 3.6% |
| tool result: git | 219 | 135k | 1.08 | 3.48 | 0.69 | 5.26 | 3.6% |
| injected: deferred tools / agent listing / MCP instructions | 48 | 127k | 0.94 | 3.80 | 0.31 | 5.04 | 3.5% |
| task notifications (worker done) | 215 | 135k | 1.08 | 3.59 | 0.30 | 4.97 | 3.4% |
| tool result: Bash python/script/gh/other/write | 150 | 140k | 1.12 | 3.27 | 0.58 | 4.97 | 3.4% |
| own output: Write/Edit content | 57 | 106k | 0.85 | 2.20 | 0.42 | 3.47 | 2.4% |
| tool result: lab_status.py | 116 | 95k | 0.76 | 1.69 | 0.41 | 2.86 | 2.0% |
| own output: text | 468 | 94k | 0.75 | 1.67 | 0.38 | 2.80 | 1.9% |
| tool result: search (Glob/Grep/colgrep, grep/ls/find/jq) | 82 | 69k | 0.54 | 1.68 | 0.23 | 2.45 | 1.7% |
| tool result: Agent/SendMessage (dispatch ack) | 194 | 59k | 0.47 | 1.45 | 0.16 | 2.08 | 1.4% |
| tool result: Read of a document/code | 15 | 43k | 0.34 | 1.44 | 0.10 | 1.88 | 1.3% |
| injected: hooks, CLAUDE.md files, environment, other | 145 | 46k | 0.35 | 1.21 | 0.10 | 1.67 | 1.2% |
| injected: invoked skill text | 9 | 26k | 0.21 | 0.70 | 0.05 | 0.96 | 0.7% |
| injected: system reminders (linked sessions, total_tokens, silent turn) | 983 | 26k | 0.19 | 0.60 | 0.10 | 0.90 | 0.6% |
| own output: recorded thinking text | 117 | 13k | 0.10 | 0.24 | 0.04 | 0.39 | 0.3% |
| tool result: other MCP/web/other tools | 119 | 10k | 0.08 | 0.14 | 0.11 | 0.33 | 0.2% |
| user messages | 36 | 8k | 0.06 | 0.14 | 0.04 | 0.24 | 0.2% |
| tool result: Write/Edit echo | 67 | 6k | 0.05 | 0.12 | 0.03 | 0.20 | 0.1% |
| child-session notes (a session the PI started finished a turn) | 19 | 12k | 0.10 | 0.01 | 0.04 | 0.15 | 0.1% |
| uncached input (all sessions) | 0 |  | 0.00 | 0.00 | 0.00 | 0.01 | 0.0% |
| tool result: ToolSearch schemas | 10 |  | 0.00 | 0.00 | 0.00 | 0.00 | 0.0% |
| TOTAL |  |  |  |  |  | 144.48 | 100% of 144.47 |

Items sum plus billed output plus uncached input equals the usage-based total of section 1 by construction (the model prices each position of the context at each request). The prefix and the step residuals are not in the transcript as text.

### 2a roll-up

| family | USD | share of PI spend |
|:--|--:|--:|
| the PI's own words (billed output + carried tool calls, briefs, Write/Edit content, text, thinking) | 63.84 | 44.2% |
| tool results (reading, git, lab_status, search, acks) | 25.29 | 17.5% |
| workers' hand-backs, task notifications, child-session notes | 17.68 | 12.2% |
| injected text and the prefix (skill listing, tool/agent lists, hooks, reminders, system prompt) | 31.79 | 22.0% |
| post-compaction context | 5.64 | 3.9% |
| user messages | 0.24 | 0.2% |
| uncached input | 0.01 | 0.0% |

### by session (USD)

| source | s1_w1-3 | s2_w4 | s3_w5 | s4_w6 | s4b_w6small | s5_w7 | s6_w8 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| own thinking carried in context (inferred: step residual, see section 2b) | 6.88 | 0.97 | 1.99 | 2.22 | 0.00 | 6.53 | 0.17 |
| injected: skill listing (re-entered) | 11.88 | 0.65 | 0.65 | 0.76 | 0.10 | 0.57 | 0.17 |
| worker hand-back messages (peer)  | 5.85 | 0.75 | 1.27 | 2.65 | 0.00 | 2.03 | 0.00 |
| own output: tool calls | 3.02 | 0.50 | 1.34 | 2.19 | 0.00 | 1.92 | 0.03 |
| system prompt + tool definitions (prefix, not in transcript) | 2.91 | 1.32 | 1.94 | 0.75 | 0.04 | 1.26 | 0.23 |
| own output: dispatch briefs and messages | 2.68 | 0.45 | 0.67 | 1.17 | 0.00 | 1.28 | 0.08 |
| post-compaction context (summary + prefix) | 5.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| tool result: Bash file view (cat/sed/head/tail) | 1.48 | 0.40 | 0.70 | 0.78 | 0.00 | 1.69 | 0.21 |
| tool result: git | 1.39 | 0.38 | 1.73 | 0.84 | 0.00 | 0.83 | 0.09 |
| injected: deferred tools / agent listing / MCP instructions | 1.20 | 0.61 | 0.97 | 1.07 | 0.08 | 0.83 | 0.27 |
| task notifications (worker done) | 2.93 | 0.28 | 0.41 | 0.53 | 0.00 | 0.82 | 0.00 |
| tool result: Bash python/script/gh/other/write | 1.84 | 0.88 | 0.57 | 1.04 | 0.00 | 0.63 | 0.00 |
| own output: Write/Edit content | 1.37 | 0.14 | 0.42 | 0.83 | 0.00 | 0.69 | 0.02 |
| tool result: lab_status.py | 1.01 | 0.16 | 0.48 | 0.48 | 0.00 | 0.65 | 0.07 |
| own output: text | 1.63 | 0.11 | 0.40 | 0.44 | 0.00 | 0.23 | 0.00 |
| tool result: search (Glob/Grep/colgrep, grep/ls/find/jq) | 0.36 | 0.21 | 0.17 | 1.09 | 0.00 | 0.53 | 0.09 |

### 2b checks on the attribution

| session | sum of step residual tokens | sum of (billed output - estimated visible output) of the previous request | billed output tokens | correlation per step | slope | skill-listing injections | USD of those |
|:--|--:|--:|--:|--:|--:|--:|--:|
| s1_w1-3 | 185k | 144k | 388k | 0.85 | 1.01 | 22 | 11.88 |
| s2_w4 | 46k | 42k | 108k | 0.94 | 0.95 | 2 | 0.65 |
| s3_w5 | 63k | 63k | 159k | 0.85 | 0.92 | 1 | 0.65 |
| s4_w6 | 77k | 76k | 225k | 0.89 | 1.13 | 1 | 0.76 |
| s5_w7 | 180k | 126k | 248k | 0.92 | 1.06 | 1 | 0.57 |
| s6_w8 | 16k | 14k | 28k | 0.97 | 1.21 | 1 | 0.17 |

MEASURED: the step residual (tokens the context grew by that no recorded text explains) tracks the previous request's billed output minus its visible text, correlation 0.85-0.94, slope about 1. CONJECTURE: the residual is the model's thinking blocks, which stay in the context although the transcript stores them empty (thinking text is 0-466 characters in the records); the residual also holds per-step framing and reminders.

## 3 the ten costliest single items (all sessions)

| session | request | source | label (path or command head) | chars | tokens | later requests that read it | write | reads | re-writes | USD |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| s1_w1-3 | 276 | COMPACTION: context after reset | reset | 0 | 91k | 113 | 0.33 | 2.05 | 3.26 | 5.64 |
| s1_w1-3 | 0 | system prompt + tool defs + CLAUDE.md (not in transcript) | residual of request 0 | 0 | 46k | 275 | 0.37 | 2.54 | 0.00 | 2.91 |
| s3_w5 | 0 | system prompt + tool defs + CLAUDE.md (not in transcript) | residual of request 0 | 0 | 42k | 151 | 0.34 | 1.27 | 0.34 | 1.94 |
| s2_w4 | 0 | system prompt + tool defs + CLAUDE.md (not in transcript) | residual of request 0 | 0 | 43k | 113 | 0.35 | 0.98 | 0.00 | 1.32 |
| s5_w7 | 0 | system prompt + tool defs + CLAUDE.md (not in transcript) | residual of request 0 | 0 | 23k | 199 | 0.18 | 0.90 | 0.18 | 1.26 |
| s1_w1-3 | 9 | Read: reports | <id>.md | 33409 | 13k | 266 | 0.11 | 0.70 | 0.00 | 0.80 |
| s4_w6 | 0 | injected: skill_listing | skill_listing | 29999 | 14k | 231 | 0.11 | 0.65 | 0.00 | 0.76 |
| s4_w6 | 0 | system prompt + tool defs + CLAUDE.md (not in transcript) | residual of request 0 | 0 | 14k | 231 | 0.11 | 0.64 | 0.00 | 0.75 |
| s1_w1-3 | 0 | injected: skill_listing | skill_listing | 29990 | 12k | 275 | 0.09 | 0.65 | 0.00 | 0.74 |
| s3_w5 | 0 | injected: skill_listing | skill_listing | 29999 | 14k | 151 | 0.11 | 0.43 | 0.11 | 0.65 |

Top 10 together: USD 16.78 of 144.47 (11.6%). Next, the ten costliest items excluding the system prefix, residuals and post-compaction context:

| session | request | source | label | tokens | later reads | USD |
|:--|--:|--:|--:|--:|--:|--:|
| s1_w1-3 | 9 | Read: reports | <id>.md | 13k | 266 | 0.80 |
| s4_w6 | 0 | injected: skill_listing | skill_listing | 14k | 231 | 0.76 |
| s1_w1-3 | 0 | injected: skill_listing | skill_listing | 12k | 275 | 0.74 |
| s3_w5 | 0 | injected: skill_listing | skill_listing | 14k | 151 | 0.65 |
| s1_w1-3 | 23 | injected: skill_listing | skill_listing | 11k | 252 | 0.64 |
| s1_w1-3 | 289 | injected: skill_listing | skill_listing | 11k | 99 | 0.64 |
| s1_w1-3 | 26 | injected: skill_listing | skill_listing | 11k | 249 | 0.62 |
| s1_w1-3 | 29 | injected: skill_listing | skill_listing | 11k | 246 | 0.62 |
| s5_w7 | 0 | injected: skill_listing | skill_listing | 10k | 200 | 0.57 |
| s1_w1-3 | 55 | injected: skill_listing | skill_listing | 11k | 220 | 0.57 |

### 2c the preface: what the PI has bought before its first dispatch

| session | first dispatch at request | context at request 0 | context at the first dispatch | USD of requests up to and including it | share of the session's USD | share of the session's USD that items entering up to then cost over the whole session |
|:--|--:|--:|--:|--:|--:|--:|
| s1_w1-3 | 20 | 74k | 153k | 2.21 | 3.5% | 15.1% |
| s2_w4 | 21 | 74k | 153k | 2.21 | 21.0% | 43.4% |
| s3_w5 | 37 | 74k | 175k | 3.18 | 17.6% | 43.2% |
| s4_w6 | 18 | 46k | 105k | 1.43 | 6.2% | 24.4% |
| s5_w7 | 19 | 47k | 138k | 1.90 | 7.0% | 27.5% |
| s6_w8 | 22 | 50k | 125k | 1.88 | 85.7% | 70.0% |

## 4 pauses: gap from the end of one response to the start of the next request

| session | requests with a gap | gaps > 5 min | of them 5 min to 1 h | of those: 1 h cache hit | gaps > 1 h | misses (read < half previous context) | USD re-written in misses | of it: premium over a read | counterfactual: USD a 5-minute cache would have re-written for the 5 min - 1 h hits | USD extra paid for writing at the 1 h rate instead of 5 min (tokens x (8-5)) |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| s1_w1-3 | 392 | 24 | 20 | 19 | 4 | 5 | 7.01 | 6.83 | 50.31 | 6.30 |
| s2_w4 | 113 | 3 | 3 | 3 | 0 | 0 | 0.00 | 0.00 | 3.22 | 1.09 |
| s3_w5 | 152 | 11 | 10 | 10 | 1 | 1 | 3.41 | 3.32 | 15.69 | 2.56 |
| s4_w6 | 231 | 22 | 21 | 21 | 1 | 0 | 0.00 | 0.00 | 35.29 | 1.56 |
| s4b_w6small | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | 0.09 |
| s5_w7 | 200 | 9 | 8 | 8 | 1 | 1 | 3.76 | 3.67 | 14.56 | 3.08 |
| s6_w8 | 28 | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 | 0.00 | 0.41 |
| ALL | 1116 | 69 | 62 | 61 | 7 | 7.00 | 14.17 | 13.82 | 119.07 | 15.08 |

Gap = start of request k minus end of response k-1 (the cache clock restarts at each request). Hits and misses are tested on the cache read of the request that follows the gap.

### what ended the gaps over 5 minutes

| what arrived first | gaps > 5 min | of them > 1 h | summed gap (h) | USD re-written in the miss |
|:--|--:|--:|--:|--:|
| worker message/notification | 42 | 1 | 10.1 | 0.00 |
| user message | 18 | 5 | 13.7 | 10.77 |
| child-session note (reminder) | 6 | 0 | 0.9 | 0.00 |
| tool result | 2 | 0 | 0.5 | 0.00 |
| system reminder only (linked sessions / other) | 1 | 1 | 1.4 | 3.41 |

Gap percentiles over 1116 requests: median 5.4 s, p75 14.4 s, p90 144.3 s, p95 454 s, p99 1756 s, max 17019 s. Share of requests with a gap > 60 s: 14.7%; > 300 s: 6.2%; > 3600 s: 0.6%.

### what woke the PI: requests by trigger (the first thing that arrived after the previous response)

| trigger | requests | USD | of it cache read | requests with no tool call | USD of those | of them output < 200 tokens |
|:--|--:|--:|--:|--:|--:|--:|
| tool result | 722 | 75.95 | 48.21 | 138 | 14.28 | 52 |
| worker message/notification | 345 | 45.77 | 29.44 | 82 | 9.42 | 40 |
| user message | 29 | 14.22 | 1.70 | 1 | 1.07 | 0 |
| system reminder only (linked sessions / other) | 1 | 3.42 | 0.00 | 0 | 0.00 | 0 |
| first request | 7 | 3.13 | 0.00 | 1 | 0.24 | 1 |
| child-session note (reminder) | 19 | 1.98 | 1.80 | 19 | 1.98 | 17 |

## 5 what each lever would have saved (ESTIMATE; formulas below each table)

### (a) read by section

| scenario | items | USD those items cost over their life | saving | share of PI spend |
|:--|--:|--:|--:|--:|
| keep 50% of each document read over 1,500 tokens | 41 | 6.19 | 3.10 | 2.1% |
| keep 25% of each document read over 1,500 tokens | 41 | 6.19 | 4.64 | 3.2% |

Formula: saving = (1 - f) x sum of USD(write + reads + re-writes) over Read and `cat/sed/head/tail` items with more than 1,500 tokens. f is a stated assumption, not measured; the all-sizes total for these two sources is USD 7.14.

MEASURED: 6 Reads of a path already Read earlier in the same session (6 paths read twice or more); the later copies cost USD 0.94 over their lives (an upper bound of the saving from not re-reading; a file may have changed in between). Costliest: <id>.md x2 USD 0.80; <id>.md x2 USD 0.05; <id>.md x2 USD 0.05; <id>.md x2 USD 0.02.

### (b) delegate orientation reads to a Sonnet worker that returns a short summary

| session | first dispatch at request | orientation items before it | tokens | USD they cost over their life | USD of a 1,500-token summary carried to the end | USD of the Sonnet worker | saving |
|:--|--:|--:|--:|--:|--:|--:|--:|
| s1_w1-3 | 20 | 19 | 38k | 2.36 | 0.12 | 0.19 | 2.05 |
| s2_w4 | 21 | 27 | 50k | 1.46 | 0.04 | 0.23 | 1.19 |
| s3_w5 | 37 | 36 | 51k | 2.23 | 0.05 | 0.23 | 1.95 |
| s4_w6 | 18 | 17 | 32k | 1.67 | 0.08 | 0.17 | 1.43 |
| s4b_w6small | no dispatch |  |  |  |  |  |  |
| s5_w7 | 19 | 20 | 41k | 2.25 | 0.07 | 0.20 | 1.98 |
| s6_w8 | 22 | 25 | 39k | 0.47 | 0.01 | 0.19 | 0.27 |

Formula: orientation items = tool results (Read, Bash, search, MCP, ToolSearch) entering at or before the request of the PI's first dispatch (an Agent or SendMessage input). saving = cost(items) - summary - worker. summary = 1,500 x (8 + L x 0.20) / 1e6 with L the number of later requests; worker = (T x 2.5 + 15 x T/2 x 0.10 + 1,500 x 10 + 20,000 x 2.5) / 1e6 for T orientation tokens (15 requests, a 20k-token worker prefix; both ESTIMATE). Sum of positive savings: USD 8.87. It assumes the PI would not read the same documents again after the summary; a PI that does loses the saving, and the orientation reads that decide a brief may not delegate.

### (c) shorter hand-back messages

| scenario | hand-back messages | characters | USD they cost over their life | saving | share of PI spend |
|:--|--:|--:|--:|--:|--:|
| cap at 1000 characters | 187 | 993k | 12.55 | 10.30 | 7.1% |
| cap at 2000 characters | 187 | 993k | 12.55 | 8.08 | 5.6% |
| cap at 3000 characters | 187 | 993k | 12.55 | 5.99 | 4.1% |

Hand-back size: n = 187, median 5125 chars, p90 7717, max 21630.
Formula: saving = sum over hand-backs longer than the cap of USD(item) x (1 - cap / chars). Task notifications (about 900 characters each) are not counted here; they are in the table of section 2.

### (d) compaction, or a new session, when the context passes a threshold

| scenario | compactions | USD saved on later requests | USD of the compactions | net | share of PI spend | net per session / compactions |
|:--|--:|--:|--:|--:|--:|--:|
| trigger 200k, compact to 91k | 20 | 56.99 | 10.57 | 46.42 | 32.1% | s1_w1-3 25.11/8; s2_w4 1.25/2; s3_w5 4.76/3; s4_w6 6.24/3; s5_w7 9.06/4 |
| trigger 200k, compact to 136k | 32 | 52.13 | 16.91 | 35.22 | 24.4% | s1_w1-3 20.29/14; s2_w4 0.26/3; s3_w5 3.20/4; s4_w6 4.45/5; s5_w7 7.02/6 |
| trigger 300k, compact to 91k | 11 | 43.67 | 6.03 | 37.64 | 26.1% | s1_w1-3 20.39/5; s2_w4 0.83/1; s3_w5 3.81/1; s4_w6 4.96/2; s5_w7 7.64/2 |
| trigger 300k, compact to 136k | 12 | 41.20 | 6.58 | 34.62 | 24.0% | s1_w1-3 18.97/6; s2_w4 0.54/1; s3_w5 2.87/1; s4_w6 4.51/2; s5_w7 7.73/2 |

Formula: when the context of a request exceeds the trigger, compact to 91,500 tokens (the post-compaction context the lab measured at request 276 of s1, 966,526 -> 91,499 tokens) or, as a variant, to 136,500 (the same plus about 45k tokens the PI re-reads after the compaction, the median orientation size of table (b)); every later request then carries `drop` fewer tokens, saving drop x 0.20 / 1e6 (x 8 / 1e6 where the request was a cache miss, as the tokens would have been re-written). One compaction costs ctx x 0.20 + 8,000 output x 20 + 41,000 written x 8, all / 1e6 (the 41,043 written tokens of request 276; the 8,000-token summary is an assumption). Information lost by compaction is not priced. Sessions s2-s6 are one wave each, so for them the trigger acts inside a wave; a new session at a wave boundary is a trigger at the start of the next wave and is bounded by what the PI must re-read.

| session | context at request 0 | at the last request | max | mean over requests | mean cache-read USD per request |
|:--|--:|--:|--:|--:|--:|
| s1_w1-3 | 74k | 307k | 966k | 497k | 0.10 |
| s2_w4 | 74k | 361k | 361k | 242k | 0.05 |
| s3_w5 | 74k | 427k | 427k | 269k | 0.05 |
| s4_w6 | 46k | 522k | 522k | 313k | 0.06 |
| s4b_w6small | 29k | 29k | 29k | 30k | 0.00 |
| s5_w7 | 47k | 569k | 569k | 353k | 0.07 |
| s6_w8 | 50k | 136k | 136k | 99k | 0.02 |

### (e) fewer requests per dispatch batch

| session | requests that dispatch (Agent or SendMessage) | runs of consecutive dispatching requests | requests absorbed if each run were one | USD saved (their cache reads, and re-write premium after a miss) |
|:--|--:|--:|--:|--:|
| s1_w1-3 | 61 | 58 | 3 | 0.36 |
| s2_w4 | 22 | 18 | 4 | 0.20 |
| s3_w5 | 13 | 13 | 0 | 0.00 |
| s4_w6 | 29 | 28 | 1 | 0.05 |
| s4b_w6small | 0 | 0 | 0 | 0.00 |
| s5_w7 | 22 | 20 | 2 | 0.14 |
| s6_w8 | 1 | 1 | 0 | 0.00 |
| ALL |  | 138 | 10 | 0.75 |

Run lengths (consecutive requests each carrying an Agent or SendMessage call, nothing between): 1: 128, 2: 10.
Formula: absorbed request = every request of a run after its first; saving = its cache-read USD (the new tokens are still written once; its own output is still produced). It is an upper bound, since a dispatch may depend on the result of the previous one.

### (f) compact right before a pause that turns out to be longer than an hour

| session | request after the pause | gap | context before | USD re-written | USD of compacting before the pause | USD of writing the compacted 91.5k after it | net saving |
|:--|--:|--:|--:|--:|--:|--:|--:|
| s1_w1-3 | 289 | 71 min | 117k | 0.94 | 0.51 | 0.73 | -0.30 |
| s1_w1-3 | 290 | 8 min | 128k | 0.63 | 0.51 | 0.73 | -0.62 |
| s1_w1-3 | 304 | 74 min | 166k | 1.34 | 0.52 | 0.73 | 0.08 |
| s1_w1-3 | 354 | 85 min | 246k | 1.97 | 0.54 | 0.73 | 0.70 |
| s1_w1-3 | 363 | 90 min | 266k | 2.13 | 0.54 | 0.73 | 0.86 |
| s3_w5 | 150 | 86 min | 425k | 3.41 | 0.57 | 0.73 | 2.10 |
| s5_w7 | 148 | 284 min | 470k | 3.76 | 0.58 | 0.73 | 2.45 |
| ALL |  |  |  |  |  |  | 5.27 |

Formula: net = re-write USD - (ctx x 0.20 + 8,000 x 20 + 41,000 x 8) / 1e6 - 91,500 x 8 / 1e6. It assumes the PI knew the pause was coming; it can know only at the end of a wave or when it hands a decision to the user.

### (e2) dispatch bursts: dispatching requests within 120 s of each other, other requests between them counted

| session | dispatching requests | Agent calls | bursts | bursts with 2+ dispatching requests | requests inside those bursts after the first | USD of their cache reads (upper bound of the saving if each burst were one request) |
|:--|--:|--:|--:|--:|--:|--:|
| s1_w1-3 | 61 | 44 | 36 | 12 | 69 | 7.94 |
| s2_w4 | 22 | 16 | 13 | 6 | 21 | 1.08 |
| s3_w5 | 13 | 15 | 9 | 3 | 14 | 0.85 |
| s4_w6 | 29 | 17 | 21 | 4 | 20 | 1.17 |
| s4b_w6small | 0 | 0 | 0 | 0 | 0 | 0.00 |
| s5_w7 | 22 | 21 | 14 | 5 | 18 | 0.96 |
| s6_w8 | 1 | 5 | 1 | 0 | 0 | 0.00 |
| ALL |  |  |  |  |  | 12.01 |

Upper bound: it counts every request from the second to the last dispatching request of a burst, including requests that wrote the briefs or read results the next dispatch depends on.

