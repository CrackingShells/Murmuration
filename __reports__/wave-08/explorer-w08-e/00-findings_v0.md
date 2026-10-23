---
type: findings
wave: wave-08
author: explorer-w08-e
date: 2026-10-24
version: v0
decision-required: confirm
---

# What a compaction costs and keeps, and what sets its threshold (findings v0)

Stayed inside the brief, with three scope notes. (1) Headless cells were run on a trimmed export of this branch (`git archive HEAD` into `/private/tmp/murmuration-w08/explorer-w08-e/plugin`, then `hooks/hooks.json` replaced by the real `SessionStart` row `resume|compact` -> `scripts/resume_brief.py` plus my logger rows), not the full plugin, because the full hooks need the Rust guard binary and a download. (2) The test lab is a tiny scratch lab (`__statera__` with one wave note, one puzzle), so `resume_brief.py`'s output there is 394 characters; its output in this lab is measured separately. (3) The PI's sessions run on Opus 5.5 with a 1M window; every headless cell ran on haiku 5.5, which also has a 1M window (`contextWindow: 1000000` in the run's `modelUsage`), so the threshold arithmetic carries over, the summary text and its quality do not. Cost figures are tokens re-priced at the lab's Opus 5.5 list price (input 4, output 20, read 0.20, 1-hour write 8 USD per million, `scripts/lab_status.py` `PRICES`).

## Result

(1) Platform, CITED + MEASURED. The threshold is settable: `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `--autocompact`, and `autoCompactWindow` / `modelSettings.<model>.autoCompactWindow` in settings (100,000 to 1,000,000 tokens); a compaction fires when the context passes window - 33,000 (window - 20,000 reserved for output - 13,000 buffer). The default for a 1M-token model is 967,000, and the lab's one real compaction fired at 967,743 tokens. `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` only lowers it (percent of window - 20,000). Both apply to the main thread and to subagents (a subagent compacted in my cell). The model cannot trigger a compaction (no tool; the Skill tool refuses `compact`). `PreCompact` can block (exit 2) and its stdout is appended to the summarizer's instructions: with a hook that printed "list every ref code", the summary held 40 `fK=CODE` pairs against 0 without it. `PostCompact` can only observe. Idle compaction (about 54 minutes after the last request, context over 200k, before the 1-hour cache lapses) is on by default but only for interactive terminal sessions; none of the six PI sessions, all `claude-desktop`, shows one [source: `tables.md` sections 1, 5].

(2) Cost, MEASURED. At a 200k window, 13 compactions at 168-174k tokens: the compaction request reads the cached prefix (about 153k), pays 12.4-14.2k tokens of uncached input at the input price (the last step's growth plus 1.8-1.9k of prompt) and writes 2.2-3.4k tokens of summary; USD 0.126-0.157 at Opus prices (mean 0.134), 10-16 s. The context after is 23.4-24.7k (`post_tokens`) and the next request writes about 40.2k tokens (the lab's real one wrote 41,043): of those, about 80k characters (about 30k tokens) are the skill listing, deferred-tool, MCP and agent listings the platform re-injects in full after every compaction, not the summary [source: `compactions.tsv`; `tables.md` sections 2, 3].

(3) Survival, MEASURED on synthetic prose. User-stated facts (a number, a path, a quoted sentence) and a code seen in a file were in the last summary of all 9 runs (19 compactions) and in the model's answer after `--resume` in all 8 runs that were resumed; 28 of 28 random 6-letter file codes were still exact after two compactions, with or without the PreCompact instruction. Ordinary prose detail did not: the 5th word of line 100 of 10 files read before the compactions came back 0 of 10 (all UNKNOWN, none wrong) against 10 of 10 in a control with no compaction [source: `tables.md` section 5; `runs_analysis.md`].

(4) Recomputed net, ESTIMATE (explorer-w08-d's per-request tables, six PI sessions, USD 144.47; my model reproduces its 46.42 and 37.64 at 200k and 300k exactly before the changes). With the measured compaction cost (summary 6,000 output tokens, 41,000 written, uncached tail), net saving by threshold and by what the PI re-reads afterwards (R tokens per compaction, written once and carried):

| threshold | window to set | R = 0 | R = 10k | R = 45k | R = 90k | break-even R |
|--:|--:|--:|--:|--:|--:|:--|
| 150k | 183,000 | 42.65 (40 compactions) | 33.78 (48) | not workable | not workable | none below the thrash limit R = 22k |
| 250k | 283,000 | 44.78 (13) | 42.15 (14) | 31.27 (17) | 11.37 (25) | 103k |
| 400k | 433,000 | 33.90 (5) | 32.57 (5) | 27.74 (6) | 23.04 (6) | 199k |

"Not workable": the post-compaction context (91,500 floor of the real compaction plus R) plus three turns of growth is over the threshold, so the platform's `rapid_refill_breaker` stops the loop (my window-100k cell hit it: "Autocompact is thrashing: the context refilled to the limit within 3 turns of the previous compact, 3 times in a row"). The one real post-compaction record (s1, 12 requests after request 276) grew by 3.3k tokens more than the 100 requests before it, so R is near 0-10k there; with R = 0-10k the net is USD 32-45 (22-31% of PI spend) at all three thresholds, 250k best, the pattern the brief's USD 35-46 shows. The information loss is not priced [source: `net_estimate.md`; `recovery_growth.txt`].

## Table

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Threshold settings | env `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, flag `--autocompact`, settings `autoCompactWindow`; window 100,000-1,000,000; trigger = window - 33,000; default 1M model 967,000; env var beats flag beats settings | CITED (`https://code.claude.com/docs/en/model-config`, `env-vars`, `settings-reference`, fetched 2026-10-24; binary `/Users/hacker/.local/share/claude/versions/2.1.304` functions `XS`, `WY`, `nQ`) | `tables.md` section 1 |
| Threshold measured | window 100k: `effectiveWindow=80000`, compactions at 70.8-83k; window 200k: `effectiveWindow=180000`, compactions at 167.9-173.8k; `--autocompact 100k`: 71.3k and 70.8k; `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=10` on the 1M model: threshold 98,000, compaction at 103,329 | MEASURED | `compactions.tsv`; `runs/e4_flag`, `runs/e5_pct` |
| `autoCompactWindow` in settings | the window was applied (`effectiveWindow=80000`, `thresholdSource=settings`) via `--settings`, but the model ended after one file, so no compaction was driven | MEASURED (window), NOT shown end to end | `runs/e3_settings_key`, `runs/e3b_settings_key` |
| Subagents | the env window applied to a subagent: 3 compactions, then `Autocompact is thrashing`; resume_brief fired 3 times in the subagent | MEASURED | `runs/e2_subagent` |
| Model-triggered compaction | none: no tool in the init list (147 tools); `Skill` with `compact` returns "compact is a built-in CLI command, not a skill" | MEASURED | `runs/c6_model_trigger` |
| PreCompact / PostCompact | PreCompact: block by exit 2 or decision block; stdout appended to the summary instructions; `systemMessage` discarded. PostCompact: `compact_summary` in input, no control. In subagents PreCompact output is ignored except a block (binary) | CITED (`https://code.claude.com/docs/en/hooks`; binary `IPe`, `PLr`), injection MEASURED | `runs/d1_precompact`, `d2_precompact` vs `d1_plain`, `d2_plain` |
| Compaction request, 200k window | input 12.4-14.2k uncached, read 150.6-156.4k, write 93-144, output 2.2-3.4k; USD 0.126-0.157; 10.3-15.8 s | MEASURED (n = 13) | `compactions.tsv` |
| Compaction request, real, 967k | `preTokens` 967,743, `postTokens` 23,767, 57.3 s, summary 15,015 characters | MEASURED | `s1_compaction_meta.txt` |
| Cost of one compaction at Opus prices (R = 0) | 150k 0.52; 250k 0.54; 400k 0.57; 967k 0.69 (read of prefix + 11.8k uncached x 4 + 6,000 x 20 + 41,000 x 8) | ESTIMATE | `net_estimate.md` last table before the sessions |
| Re-injected after a compaction | skill listing 34.7k chars, deferred tools 28.6k, MCP instructions 8.9k, agent listing 8.2k, summary 5.3k, five `compact_file_reference` of about 160 chars (paths, not contents) | MEASURED | `tables.md` section 3 |
| resume_brief | fires on `compact` and `resume`, 75-79 ms; 394 chars in the test lab; 15,977 characters in this lab; the same script fires in a compacted subagent | MEASURED | `runs_analysis.md`; `printf ... | python3 scripts/resume_brief.py | wc -c` |
| What survives | user facts and file codes 100% (19 compactions in 9 runs, 28 of 28 codes after two); prose detail 0 of 10 (control 10 of 10) | MEASURED, one synthetic task, haiku | `tables.md` section 5 |
| Net at 150k / 250k / 400k | see the table in Result (4) | ESTIMATE | `net_estimate.md` |

## Worst-fitting case

The story that fits best: compaction is cheap (about USD 0.5-0.7 each), keeps what the user said and what looks like an identifier, and the lever is worth USD 32-45 over the six PI sessions.

Fits worst, in five parts.

1. The survival tests are the easiest case. A summarizer that is told in the first message to "remember three things" and sees a 6-letter code in each file keeps them; I did not test what the PI actually holds: the conclusions drawn from a 33k-character report, which worker said what, why a claim was withdrawn. The one result that shows loss (prose detail 0 of 10) is also the one that matters for a re-read: whatever the PI would quote from a file it must re-read. R is therefore the unknown, and the table is flat in R only up to about 10k and falls fast after that (250k: 42 at 10k, 31 at 45k, 11 at 90k). [source: `tables.md` section 5; `net_estimate.md`]
2. The one real post-compaction record points the other way from my 45k and 90k columns: 12 requests after s1 request 276 added only 3.3k tokens over the usual growth. But that compaction came in the middle of a stream of tool results and was followed by a 70-minute pause and a 128,612-token cache re-write (request 289), so it says little about what a PI needs when it resumes after a pause. [source: `recovery_growth.txt`; `__reports__/wave-08/explorer-w08-d/s1_w1-3_requests.tsv` rows 276-289]
3. Three sessions ended early after a compaction with the word "ok" (c1 after the third, c4 after the first, d2_precompact after 22 of 28 files) while five went on to the end (c3, c5, d1_plain, d1_precompact, d2_plain). I first took this for loss of the task state. The control cells e3 and e3b, which never compacted, also ended after one file with "ok": it is haiku's reading of "say only ok after each", not a compaction effect. It stays a flag because a PI that stops with "ok" after a compaction costs a human a prompt. [source: `runs/c1_window100k/stream.jsonl`, `runs/c4_codes_w200k/stream.jsonl`, `runs/d2_precompact/stream.jsonl`, `runs/e3b_settings_key/stream.jsonl`]
4. The docs disagree with each other. The context7 mirror (`/pjbrito/claude-code-docs`, older text) says a default local session compacts only when the conversation "reaches the model's context limit" and that the percentage override works only for proactive compaction; the official page (`https://code.claude.com/docs/en/model-config`, fetched today) says native-1M models "compact before the window fills, at about 967K". The lab's own compaction at 967,743 and my runs (reactive path, `thresholdSource=env`/`settings`) agree with the official page; the settings key is shown only as an applied window. [source: `tables.md` section 1]
5. The prior estimate and mine differ little where the cost is concerned (USD 0.54 against 0.54 at 250k), so the measurement mostly confirms explorer-w08-d's cost model and leaves its weakest assumption, R, as it was. s1 alone is USD 23-24 of the 42-45. [source: `net_estimate.md`]

## Not covered

- The compaction of an Opus 5.5 main thread at 250k-400k was not run: haiku's summary length (5.7-6.9k characters) and its choices of what to keep are not Opus's; the real summary was 15,015 characters.
- What the PI loses in practice (R) is assumed in the table and bounded by one real record; no PI-like task (dispatch bookkeeping, claims, who is waiting for whom) was run through a compaction.
- `autoCompactWindow` as a project settings key was not driven end to end; the Desktop entrypoint (the PI's) was not run: whether the env var, the flag or the settings key reaches a Desktop-launched session is open. I read the 2.1.304 binary, the desktop app carries 2.1.308.
- Idle compaction and `precomputeCompactionEnabled` were not run; subagent frontmatter `autoCompactWindow` was not run.
- Cache behaviour at a miss: the compaction request's price when the cache is cold (written at 8, or read as input at 4) is not measured; the table prices it as a write.
- Workers: the lab's workers rarely reach a threshold (explorer-w08-a's context ceilings); the compaction of workers was only shown in a subagent cell.

## Steering questions

- [now] Shall the PI's session carry a threshold of about 250k (window 283,000 via `autoCompactWindow` in the settings the lab writes, or via the Desktop's environment)? ESTIMATE USD 42-45 at R of 0-10k (29-31% of PI spend), 31 at R = 45k. The settings route is not shown end to end, the Desktop route not at all.
- [now] Shall a `PreCompact` hook print a standing instruction (the open claims and who is waiting, the last user sentence, file paths read)? It is measured to reach the summary at no cost beyond a few hundred tokens; it does not make the summarizer keep prose detail.
- [later] Shall `resume_brief.py` stop injecting the whole wave note (15,977 characters here) after each compaction and resume, and in compacted subagents?

## Pointers

Scratch: `/private/tmp/murmuration-w08/explorer-w08-e/` (runs, transcripts and logs stay there; nothing from a transcript is committed, only counts). Report folder: `__reports__/wave-08/explorer-w08-e/`.

- `tables.md`: platform table, compaction request table, re-injection table, resume_brief, survival tests.
- `compactions.tsv`: `python3 -I __instrumenta__/w08e_collect.py /private/tmp/murmuration-w08/explorer-w08-e` (one row per compaction, with its request usage and USD).
- `runs_analysis.md`: `python3 -I __instrumenta__/w08e_compact_analyze.py runs/<run>` for c1, c2, c3, c4, c5, d1 x2, d2 x2, e1.
- `net_estimate.md`: `python3 -I __instrumenta__/w08e_compaction_net.py __reports__/wave-08/explorer-w08-d`; `recovery_growth.txt`: `python3 -I __instrumenta__/w08e_recovery_growth.py __reports__/wave-08/explorer-w08-d/s1_w1-3_requests.tsv`; `s1_compaction_meta.txt`: `python3 -I __instrumenta__/w08e_s1_compaction_probe.py`.
- Headless runs: `python3 __instrumenta__/w08e_compact_run.py /private/tmp/murmuration-w08/explorer-w08-e <name> CLAUDE_CODE_AUTO_COMPACT_WINDOW=200000 --nfiles 28 [--precompact-text "..."]` (haiku, default permission mode, Read only, no budget flag; seeds: filler `random.Random(7)`; model non-deterministic); detail probe `w08e_detail_probe.py runs/<run>`; items after a boundary `w08e_postcompact_items.py <transcript>`. Cells c6, e2-e5 were run by hand with `claude -p ... --model haiku --permission-mode default` (commands in `tables.md` sections 1; env `CLAUDE_CODE_SHELL=/bin/bash`).
- Scripts cited as `__instrumenta__/w08e_compact_run.py@fc2d2ef`, `w08e_compact_analyze.py@fc2d2ef`, `w08e_collect.py@fc2d2ef`, `w08e_compaction_net.py@fc2d2ef`, `w08e_postcompact_items.py@fc2d2ef`, `w08e_recovery_growth.py@fc2d2ef`, `w08e_detail_probe.py@fc2d2ef`, `w08e_s1_compaction_probe.py@fc2d2ef`.
- Binary reading: `strings -a /Users/hacker/.local/share/claude/versions/2.1.304` (read only, one search helper in scratch).
- Docs fetched: `https://code.claude.com/docs/en/hooks`, `/env-vars`, `/model-config`, `/sub-agents`, `/settings-reference` (all via WebFetch, partial windows); context7 `/pjbrito/claude-code-docs` (medium reputation mirror).
