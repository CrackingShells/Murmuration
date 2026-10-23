---
type: findings
wave: wave-08
author: explorer-w08-a
date: 2026-10-24
version: v0
decision-required: none
---

# Where worker context USD sits, by source: lab scripts, documents, shell commands rtk knows (findings v0)

Stayed inside the brief. Two scope notes. (1) "Worker context USD" is the input side of every request (cache reads, cache writes at the 5-minute or 1-hour rate as recorded, uncached input) at list price; output tokens are left out because the transcripts store the output count at the start of the stream (3 to 8 tokens per request), so generation cost is not recoverable. (2) The rtk text below comes from two WebFetch calls of the GitHub page, which returns a summary written by a small model, not the README verbatim; every rtk statement is CITED with that caveat.

## Result

MEASURED/ESTIMATE: over all 68 workers of waves 4-7 (3,685 requests, USD 83.69 of context) a lab script's output is **3.7%** of context USD (USD 3.07, 470 results) and a lab document, whether by Read or by `cat`/`sed`/`head`/`tail`, **14.3%** (USD 11.98, 589 results); the largest block is the worker's own earlier turns, **41.6%** (thinking blocks 22.5%, tool-call text 19.0%). Capping every lab-script output at 2,500 tokens saves at most USD 0.45 (0.5% of context USD); capping every document at 2,500 tokens, or reading by 2,500-token sections, at most USD 5.74 (6.9%); both at 5,000 tokens USD 2.85 (3.4%) (ESTIMATE, ceilings). The shell commands rtk lists (git, grep/find, ls, cat) hold 11.7% of context USD, of which 8.8 points are `cat` of documents, source and data, and 2.9 points git, grep, find and ls (CITED list, MEASURED shares); its hook does not see Read results or the lab's scripts. [source: `__reports__/wave-08/explorer-w08-a/tables.md`, `bash_by_command.tsv`]

## Method (how an item gets its USD)

1. Per worker, requests are the distinct assistant message ids; each request's context size is C = cache read + cache write + input. The items that entered between two requests (tool results, hook text, messages) are listed from the transcript.
2. Tokens per item: the growth of C between consecutive requests is regressed on the characters of the new items by class, the characters of the previous turn's tool-call inputs, its thinking blocks (signature plus text) and its text (OLS, 3,544 intervals without a ToolSearch result; R2 = 0.989). The fit gives about 0.43 tokens per character for documents and source (2.3 characters per token), 0.51 for script output, 0.42 for tool-call text, 0.29 for thinking characters. The growth is then shared exactly: items and the agent's own parts are scaled so that they sum to the measured growth; a ToolSearch result takes what the fit leaves over (the schemas). Result: item sizes add up to C at every request (0 of 3,685 requests off by more than 2%) [source: `check.txt`].
3. Money: the tokens of C are laid out in order; the first `cache read` tokens are billed at the read price, the next `cache write` tokens at the write price (5-minute and 1-hour rates mixed as the request recorded), the rest at the input price. An item's USD is the overlap summed over every request that carried it: the request where it entered (first write), later reads, and later requests where it fell inside the written part (a re-write after a pause over the cache lifetime). The attributed sum equals the recorded input-side USD (83.6934 = 83.6934) by construction, and the reads of waves 4-6 are USD 34.58 against explorer-w07-b's 34.59 from a different method (a check, not an independent proof) [source: `check.txt`, `__reports__/wave-07/explorer-w07-b/00-findings_v0.md`].
4. Class: Read by path; Bash command parsed per pipeline segment, priority script run, then document or source read (`cat`, `sed`, `head`, `tail`, `wc`, `awk`, `cut`, `jq`, `diff`), git, shell search, other. A command that reads several files takes the kind of the first path (this put one report under "claim file", row 17 of the old list; see puzzles).

Waves: w4 `c533f1c6` 15 workers, w5 `6b0e1f2a` 15, w6 `74fa512e` 17, w7 `f023f552` 21 (including one general-purpose helper from a wave-6 prompt).

## Table

### Share of worker context USD by source class (all 68 workers) [MEASURED counts, ESTIMATE tokens and USD]

| Source class | Elements | Est. tokens | USD | Share | of which re-writes after a pause |
|:--|--:|--:|--:|--:|--:|
| agent's own turns: thinking blocks | 3,617 | 2,160,867 | 18.82 | 22.5% | 3.46 |
| agent's own turns: tool calls (input text) | 3,617 | 2,129,127 | 15.92 | 19.0% | 2.84 |
| cat/sed/head/tail of a document in Bash | 472 | 850,450 | 7.22 | 8.6% | 0.83 |
| worker's own code run (scratch script, inline python) | 1,083 | 934,625 | 7.28 | 8.7% | 1.14 |
| cat/sed/head/tail of source code in Bash | 373 | 636,386 | 6.70 | 8.0% | 1.09 |
| Read of a lab document | 115 | 440,912 | 4.31 | 5.1% | 0.69 |
| messages, resume prompts, task notices | 344 | 422,340 | 3.34 | 4.0% | 0.40 |
| other tool results (edits, mkdir, ls ...) | 859 | 402,694 | 3.09 | 3.7% | 0.52 |
| lab script output (`scripts/`, `__instrumenta__/`) | 470 | 437,618 | 3.07 | 3.7% | 0.48 |
| harness text at start (instructions, session context, tool lists) | 628 | 322,096 | 2.77 | 3.3% | 0.33 |
| Read of source code | 23 | 190,305 | 2.53 | 3.0% | 0.52 |
| system prompt and tool schemas (base) | 68 | 337,454 | 1.81 | 2.2% | 0.01 |
| hook-injected text (additionalContext, `total_tokens` reminders) | 3,692 | 209,621 | 1.76 | 2.1% | 0.27 |
| search results (colgrep, grep, find) | 241 | 246,007 | 1.73 | 2.1% | 0.20 |
| ToolSearch results (tool schemas) | 74 | 150,274 | 0.92 | 1.1% | 0.09 |
| git output | 171 | 123,763 | 0.85 | 1.0% | 0.10 |
| the brief (first prompt) | 68 | 85,394 | 0.71 | 0.8% | 0.06 |
| Read of a non-lab document (a persisted tool-result file) | 2 | 62,973 | 0.45 | 0.5% | 0.07 |
| web or MCP results | 67 | 137,980 | 0.38 | 0.4% | 0.02 |
| the agent's text and per-turn wrapper | 3,617 | 8,287 | 0.04 | 0.1% | 0.01 |
| total | 19,601 | | 83.69 | 100% | 13.12 (15.7%) |

By wave (share of that wave's context USD, USD 17.28 / 15.03 / 29.99 / 21.39 for w4..w7): lab script output 5% / 3% / 3% / 4%; lab documents Read + Bash 13% / 16% / 12% / 16%; own turns 42% / 36% / 45% / 39% (thinking plus calls, from `tables.md` section 1b). Totals by source: tool results 46.0% (USD 38.53), of which documents 31%, source code 24%, the worker's own code 19%, lab scripts 8%.

### Lab documents, by kind and route [MEASURED/ESTIMATE; `tables.md` section 2]

| Kind (route) | Results | Mean est. tokens | USD | Share |
|:--|--:|--:|--:|--:|
| report (Bash) | 102 | 2,447 | 2.10 | 2.5% |
| claim file (Bash) | 157 | 1,560 | 2.08 | 2.5% |
| claim file (Read) | 24 | 5,206 | 1.36 | 1.6% |
| report (Read) | 32 | 3,717 | 1.26 | 1.5% |
| framing (Read) | 34 | 3,662 | 1.06 | 1.3% |
| framing (Bash) | 20 | 4,572 | 0.96 | 1.2% |
| wave note (Read + Bash) | 23 | 3,840 / 4,538 | 0.79 | 0.9% |
| synthesis (Bash) | 4 | 4,025 | 0.25 | 0.3% |
| brief protocol (Read + Bash) | 34 | 1,100 / 1,594 | 0.37 | 0.4% |
| puzzle file (Read + Bash) | 45 | 374 / 1,614 | 0.21 | 0.2% |
| user_words (Bash) | 2 | 967 | 0.01 | 0.0% |
| other lab/non-lab documents, report data, statera/harness files | 112 | | 1.53 | 1.8% |
| all documents | 589 | | 11.98 | 14.3% |

Route: Read 117 results USD 4.76 (5.7%), Bash 472 results USD 7.22 (8.6%): `cat` 275 results USD 4.15, `sed` 108 USD 1.75, `head` 32 USD 0.73. No document Read used `offset`/`limit` (0 of 117 Reads of documents carry "(section)"; `tables.md` section 2, last column). 71% of document USD entered in the first four requests of a worker's life. Repeat reads of one path by one worker: 131 results, USD 1.08 (1.3% of context USD).

### The 20 costliest documents and scripts [MEASURED/ESTIMATE; `top_refs.tsv`, `tables.md` section 3]

| # | Type | What | Results | Workers | USD | Share |
|--:|:--|:--|--:|--:|--:|--:|
| 1 | worker's own code | inline python / heredoc | 841 | 65 | 5.41 | 6.5% |
| 2 | document | `__design__/framing.md` | 52 | 50 | 1.93 | 2.3% |
| 3 | worker's own code | scratch script run | 136 | 24 | 0.95 | 1.1% |
| 4 | worker's own code | inline `python -c` | 106 | 43 | 0.91 | 1.1% |
| 5 | document | `__pondus__/w04-c5.md` | 9 | 5 | 0.86 | 1.0% |
| 6 | document | wave notes `__statera__/wave-NN.md` (all waves) | 20 | 16 | 0.63 | 0.8% |
| 7 | document | `blgpdcaey.txt` (persisted tool result, read by Read, 26,304 tokens) | 1 | 1 | 0.45 | 0.5% |
| 8 | document | `__reports__/wave-06/explorer-w06-b/00-findings_v0.md` | 4 | 4 | 0.38 | 0.5% |
| 9 | document | `__reports__/reflective_run/w04/00-experiment_protocol_v0.md` | 16 | 10 | 0.35 | 0.4% |
| 10 | document | `__pondus__/w03-c1.md` | 1 | 1 | 0.32 | 0.4% |
| 11 | document | `__statera__/synthesis.md` | 4 | 4 | 0.25 | 0.3% |
| 12 | document | `__reports__/wave-05/explorer-w05-d/00-findings_v0.md` | 3 | 3 | 0.20 | 0.2% |
| 13 | document | `__pondus__/w05-c4.md` | 7 | 3 | 0.20 | 0.2% |
| 14 | lab script | `__instrumenta__/w06c7_e3_report.py` | 3 | 1 | 0.19 | 0.2% |
| 15 | document | `__pondus__/w06-c3.md` | 6 | 3 | 0.17 | 0.2% |
| 16 | lab script | `__instrumenta__/e3_measure.py` | 7 | 1 | 0.17 | 0.2% |
| 17 | document | `__reports__/wave-07/explorer-w07-c/00-findings_v0.md` (filed under "claim file": command named a claim file first) | 1 | 1 | 0.17 | 0.2% |
| 18 | document | `__pondus__/w03-c2.md` | 1 | 1 | 0.15 | 0.2% |
| 19 | document | `__pondus__/w06-c9.md` | 6 | 4 | 0.14 | 0.2% |
| 20 | lab script | `__instrumenta__/w07f_binary_window.py` | 11 | 1 | 0.14 | 0.2% |

Lab scripts alone, top 5 (of USD 3.07; `__instrumenta__/` 2.94, plugin `scripts/` 0.13): `w06c7_e3_report.py` 0.19, `e3_measure.py` 0.17, `w07f_binary_window.py` 0.14, `w06c9_timing.sh` 0.13, `hook_cost_summary.py` 0.12; the costliest plugin script is `scripts/check_guard_equal.py` at USD 0.027. Lab-script output is small: median 540 tokens, 90th percentile 2,271, largest 10,257 (470 results).

### Ceiling savings by cap, or by section [ESTIMATE; `tables.md` section 4]

Formula: for an element with t tokens and context USD c, a cap of K tokens leaves c x min(1, K/t) (all later requests carry the element, so its cost is proportional to t at the same position and pauses); saving = sum of c x max(0, 1 - K/t). Ceiling: the cut text was not needed, no extra call is made, nothing else changes. "By section only" is the same with K = the section read.

| Group | USD now (share) | K = 1,000 | K = 2,500 | K = 5,000 | K = 10,000 | Elements above 2,500 |
|:--|:--|:--|:--|:--|:--|--:|
| lab script output | 3.07 (3.7%) | 1.14 (1.4%) | 0.45 (0.5%) | 0.12 (0.1%) | 0.00 | 35 |
| documents, Read | 4.76 (5.7%) | 3.74 (4.5%) | 2.46 (2.9%) | 1.37 (1.6%) | 0.51 (0.6%) | 79 |
| documents, Bash | 7.22 (8.6%) | 5.24 (6.3%) | 3.28 (3.9%) | 1.35 (1.6%) | 0.10 (0.1%) | 125 |
| all documents | 11.98 (14.3%) | 8.98 (10.7%) | 5.74 (6.9%) | 2.73 (3.3%) | 0.61 (0.7%) | 204 |
| lab scripts + all documents | 15.05 (18.0%) | 10.13 (12.1%) | 6.19 (7.4%) | 2.85 (3.4%) | 0.61 (0.7%) | 239 |
| source code (Read + Bash) | 9.23 (11.0%) | 6.53 (7.8%) | 4.16 (5.0%) | 2.20 (2.6%) | 0.73 (0.9%) | 104 |
| every tool result | 38.53 (46.0%) | 22.82 (27.3%) | 13.06 (15.6%) | 5.89 (7.0%) | 1.42 (1.7%) | 542 |

(percentages in brackets are shares of all context USD 83.69). The "every tool result" row at K = 1,000 is not a realistic lever; it shows that the whole pool of tool results is 46% and that capping the large ones is bounded by 27%. Cost of one token of a tool result over a worker's life: about USD 0.0072-0.0094 per 1,000 tokens whatever the entry time (mean 36-51 later requests; re-write share 13-22%); a 23,000-token document read at request 2 costs about USD 0.20 per worker (ESTIMATE: 23 x 0.0088). The wave notes of waves 4-7 averaged 3,840 tokens when read; the 52 KB wave-08 note is outside these data.

### rtk (https://github.com/rtk-ai/rtk, fetched 2026-10-24 by WebFetch, summary of the page) [CITED, shares MEASURED]

- CITED: rtk is a PreToolUse hook (`rtk init -g`) that rewrites Bash commands (`git status` becomes `rtk git status`) so the output arrives compressed; "The hook only fires on Bash tool calls"; "Built-in tools like `Read`, `Grep` and `Glob` do not pass through it" (use `rtk read`, `rtk grep`, `rtk find` instead). "100+ commands" without a full list: git (`status`, `diff`, `log`, `add/commit/push`, gh), `cat`/`read` ("Smart file reading: signatures and structure over full bodies"), `ls`/`tree`, `grep`/`rg`/`ast-grep`/`find`, test runners (cargo, npm, pytest, go test, vitest, jest, Playwright), linters and type checkers, build tools, docker/kubernetes/aws/terraform, package managers. Claimed savings: "60-90% on common dev commands", "up to 90% smaller", measured on bash output only, tokens = bytes/4. The page does not say what happens to unlisted commands, whether `rtk read` is lossy, or how to recover hidden output (only `rtk bypass <cmd>`). A separate proxy for provider API traffic exists (BUSL-1.1 binary) and is not part of the hook.
- MEASURED shares of context USD (68 workers, `bash_by_command.tsv`): all Bash results USD 29.35 (35.1%). Listed by rtk: `cat` of documents 4.15, of source 2.88, of data 0.33 (7.36, 8.8%); `grep` 1.27 and `find` 0.14; git 0.85; `ls` 0.18; together **USD 9.81, 11.7%**; without `cat` **USD 2.44, 2.9%**. Test runners, linters, docker, gh: none appear (a count of Bash inputs for `pytest`, `cargo test`, `npm test`, `ruff`, `mypy`, `docker ps`, `kubectl`, `gh` over 3,335 Bash calls found 0). Not known to rtk, as far as the page says: `sed`/`head`/`tail`/`wc` of files USD 7.62 (9.1%), the lab's scripts USD 3.07 (3.7%), the worker's own inline python and scratch scripts USD 7.27 (8.7%), and every Read result (USD 7.29, 8.7%, plus the agent's own turns 41.6%), which the hook cannot touch.
- ESTIMATE of the ceiling: rtk-listed output USD 9.81 x claimed 60-90% = USD 5.9-8.8 (7-10% of context USD), only if `cat` of a claim file or report could be compressed by that much, which is the case a verifier cannot accept (its purpose is to see the text). On the part with no such conflict (git, grep, find, ls, USD 2.44): USD 1.5-2.2 (1.8-2.6%). Formula: listed USD x compression rate; compression is lossy, so the saving also carries the risk that a worker re-reads with `rtk bypass`.

## Worst-fitting case

The story is "scripts are small, documents moderate, the worker's own turns dominate". The case that fits it worst: **explorer-w06-b**, where documents were 35% of the worker's context USD (USD 0.35 of 0.99), and **reproducer-w04-4**, where lab scripts were 22% (USD 0.10 of 0.44); neither is a large worker. The costliest workers (author-w06-5, USD 9.09, 241 requests; author-w04-4, USD 5.60, 122 requests) are 67% and 53% own turns, with lab scripts 8% and 15% and documents 2-3%: for them cost follows the number of requests (every earlier turn is re-read by every later request), not what the tools returned. The largest single result, a 26,304-token Read of a persisted tool-result file (`blgpdcaey.txt`, USD 0.45, 0.5%), also fits "documents" poorly: it is not a lab document and one worker read it once. The thinking blocks (22.5%) are an inference from the fit (signature characters correlate with context growth, R2 0.989); their text is redacted in the transcripts, so their token count is not seen directly.

## Not covered

- Output (generation) cost: not recoverable from these transcripts (output_tokens is stored at stream start). Context USD here is 83.69 against a recorded all-in worker cost that includes output; shares are of context only.
- PI sessions; waves 1-3 and 8; the PI's own scripts. Waves 4-7 only, 68 workers.
- Whether a cap or a section read would lose information a worker needed: the savings are ceilings with no measure of the re-reads a cap would cause. A probe of caps on a task would be the next step.
- rtk: nothing installed or run; its hook cost per call, compression on real lab output, and loss were not measured. The page was read through a fetch summary, not the README text.
- Token estimates are from a fit (R2 0.989 on context growth), not from a tokenizer; per-item error not bounded. Items are laid out in transcript order, so the first-request cache-region boundary is exact only to the item.
- Hook-injected text and `total_tokens` reminders (2.1%) are measured as characters of attachment records; text a hook adds inside a tool result is counted with that result.

## Steering questions

- [now] The bulk is the worker's own turns (41.6%: thinking 22.5%, tool-call text 19.0%) and inline python the worker writes and runs (8.7% as output plus the code text in the call): should the next wave test fewer requests per worker (a stop rule or a smaller brief) rather than shorter outputs?
- [now] Is a ceiling of 6.9% (documents capped at 2,500 tokens) enough to justify a probe, given that scripts offer 0.5%?
- [now] rtk lists `cat`; the verifiers' documents are 8.6% of context in Bash. Do you want a probe of rtk on a copy of the lab (a download, so yours to approve), or drop it given a 2.9% non-conflicting ceiling?

## Pointers

All in `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-8-928ebd/__reports__/wave-08/explorer-w08-a/` (transcripts read only; per-worker JSON in `/private/tmp/murmuration-w08/explorer-w08-a/items/`, not copied: it holds call classes; `items.tsv` holds one row per context element with class, kind, lab-relative path or basename, tokens, USD; no transcript text). Each command runs in about 1-3 s. Scripts cited as `__instrumenta__/<file>@<commit>` (commit given at the commit of this report):

- `python3 -I __instrumenta__/w08a_items.py /private/tmp/murmuration-w08/explorer-w08-a/items w4=<c533f1c6>.jsonl w5=<6b0e1f2a>.jsonl w6=<74fa512e>.jsonl w7=<f023f552>.jsonl` (the four main transcripts under `~/.claude/projects/*wave-4-3417be`, `*lab-system-optimization-1aa673`, `*blissful-villani-34edd8`, `*xenodochial-franklin-bc67fb`): 68 workers, 3,685 requests, 8,682 items.
- `python3 -I __instrumenta__/w08a_cost.py /private/tmp/murmuration-w08/explorer-w08-a/items __reports__/wave-08/explorer-w08-a`: `items.tsv`, `check.txt`.
- `python3 -I __instrumenta__/w08a_tables.py __reports__/wave-08/explorer-w08-a`: `tables.md`, `by_class.tsv`, `top_refs.tsv`.
- `python3 -I __instrumenta__/w08a_bash_rtk.py __reports__/wave-08/explorer-w08-a`: `bash_by_command.tsv`, the rtk line.
- Reused: `scripts/lab_status.py` (PRICES, `message_usd`). `w07b_loop_parse.py` was read, not reused: it keeps per-call result sizes but not the order of items inside a request, which the position-based attribution needs.
- Seeds: none. Prices: `scripts/lab_status.py` PRICES (Sonnet 5.5: input 2, read 0.10, write 5m 2.5, write 1h 4 USD per million tokens; list price of 2026-10-19), ESTIMATE.
