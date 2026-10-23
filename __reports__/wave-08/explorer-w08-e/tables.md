# Tables for explorer-w08-e (compaction: platform, cost, what survives)

Claude Code 2.1.304 (`/Users/hacker/.local/share/claude/versions/2.1.304`, strings read with `strings -a`; `claude --version` on PATH says 2.1.304; the desktop app's copy is 2.1.308 and was not read). Docs fetched 2026-10-24 from `https://code.claude.com/docs/en/{hooks,env-vars,model-config,sub-agents,settings-reference}` (WebFetch, truncated at 100k-char windows) and the mirror `/pjbrito/claude-code-docs` via context7 (older wording).

## 1 platform: what sets the threshold, in order of precedence

| Lever | What it does | Source (CITED) | Measured here |
|:--|:--|:--|:--|
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW=<tokens>` (`200k` suffix needs 2.1.304+) | auto-compact window, 100,000 to 1,000,000, capped at the model's window; beats every other setting | env-vars, model-config; binary: `SP=1e5, CN=1e6`, `E4t` clamps | yes: c1-c5, d*, e2 (window 100k and 200k) |
| `--autocompact 200k` (CLI flag, one launch) | same, one launch; not overridden by managed settings | model-config | yes: e4_flag, compactions at 71,274 and 70,838 tokens with `--autocompact 100k` |
| `autoCompactWindow` (settings, any file) and `modelSettings.<model>.autoCompactWindow`; `/autocompact 500k` saves to the second | same, lower precedence | settings-reference, model-config; binary `HJt`, `Ibr` | window honoured (`effectiveWindow=80000`, `thresholdSource=settings`) in e3/e3b via `--settings`; the model quit after one file in both, so no compaction was driven: NOT demonstrated end to end |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=<1-100>` | percentage of (window - 20,000); can only lower the threshold | env-vars; binary `nQ`: `min(floor(e*pct/100), e-13000)` | yes: e5_pct, 10% on haiku 5.5 (980,000 effective) compacted at 103,329 tokens (threshold 98,000) |
| subagent frontmatter `autoCompactWindow: <int 100000-1000000>` | one subagent compacts earlier; the env var overrides it | sub-agents | not run |
| `DISABLE_AUTO_COMPACT`, `DISABLE_COMPACT`, `autoCompactEnabled` | off switches (DISABLE_COMPACT also manual `/compact`) | binary strings; settings-reference (index row) | not run |
| `idleCompaction` (default true) + `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` (default 200,000, floor 100,000) | compacts about 54 minutes after the last request, before the 1-hour cache lapses; only interactive terminal sessions on the 1-hour TTL with feature flags | settings-reference | not run; no `Compacted while idle` line in any of the six PI transcripts, whose entrypoint is `claude-desktop` (CONJECTURE: the desktop host is not a terminal session) |

Threshold arithmetic (binary `WY`, `nQ`): trigger = window - min(maxOutputTokens, 20,000) - 13,000, so window w gives a threshold of w - 33,000. Default for a 1M-token model: 1,000,000 - 33,000 = 967,000 (docs: "about 967K"); the lab's real compaction fired at 967,743 tokens (s1, `w08e_s1_compaction_probe.py`). Measured: window 100,000 -> `effectiveWindow=80000`, compactions at 71-83k; window 200,000 -> `effectiveWindow=180000`, compactions at 168-174k. To get a threshold T set the window to T + 33,000 (150k -> 183000, 250k -> 283000, 400k -> 433000).

| Question | Answer | Label | Source |
|:--|:--|:--|:--|
| Main thread and subagents alike? | yes for the window and the percentage; a subagent in e2 (env window 100,000) was compacted three times, ended in `Autocompact is thrashing` | CITED + MEASURED | env-vars ("Applies to both main conversations and subagents"); `runs/e2_subagent` (debug.log 3 `Forked agent [reactive-compact]`, hooks.log) |
| Can the model trigger a compaction? | no: no tool in the 147-tool init list; the Skill tool refuses it ("compact is a built-in CLI command, not a skill ... it cannot be invoked via the Skill tool"); `/compact` and `/autocompact` are user commands | MEASURED | `runs/c6_model_trigger/stream.jsonl`, `stream2.jsonl` (haiku) |
| `PreCompact`: block? | exit 2 or `{"decision":"block"}` blocks; a blocked proactive compaction is skipped, a blocked reactive one surfaces the API error; `systemMessage`/`continue` discarded | CITED | hooks page; binary `IPe` |
| `PreCompact`: inject into the summary? | yes: stdout of a succeeding PreCompact command is appended to the summarizer's custom instructions (binary: `newCustomInstructions`); the hook input holds `trigger`, `custom_instructions` (null on auto) | CITED + MEASURED | binary `IPe`; `runs/d1_precompact`, `d2_precompact`: summary holds 40 `fK=CODE` pairs against 0 in `d1_plain`, `d2_plain` (my hook printed "list every ref code as fK=CODE pairs") |
| `PreCompact`/`PostCompact` in a subagent | binary: in a subagent the PreCompact output is ignored except a block, PostCompact returns nothing; the hook commands themselves did run in e2 (hooks.log shows 3 PreCompact, 3 PostCompact, 3 SessionStart:compact) | CITED + MEASURED | binary `IPe`, `PLr`; `runs/e2_subagent/hooks.log` |
| `PostCompact` | gets `trigger`, `compact_summary`; no decision control | CITED + MEASURED | hooks page; `hooks.log` keys |
| `SessionStart` with source `compact` / `resume` | fires after every compaction and resume; stdout is added to the context | CITED + MEASURED | hooks page; every run: one per compaction, one per `--resume` |

## 2 the compaction request's own cost (haiku 5.5 runs, re-priced at Opus 5.5 list: input 4, output 20, read 0.20, write 8 per M)

All 13 compactions at a 200k window (c3, c4, c5, d1 x2, d2 x2, c5): `compactions.tsv` rows with window 180000.

| quantity | min | mean | max |
|:--|--:|--:|--:|
| context before (tokens) | 167,869 | 170,823 | 173,762 |
| context after, `post_tokens` | 23,423 | 24,089 | 24,658 |
| summary output tokens | 2,197 | 2,613 | 3,447 |
| summary size (characters, PostCompact) | 5,025 | 6,300 | 6,871 |
| uncached input of the compaction request | 12,393 | 12,655 | 14,178 |
| cache read of the compaction request | 150,582 | 153,171 | 156,386 |
| cache write of the compaction request | 93 | 104 | 144 |
| duration (ms) | 10,260 | 11,656 | 15,792 |
| USD at Opus 5.5 list | 0.126 | 0.134 | 0.157 |

The uncached input is the last step's growth (about 10.6k per file read) plus 1.8-1.9k of summarizer prompt: the request reads the whole cached prefix (`tengu_compact_cache_prefix`) and pays full input price (4, not the 8 of a write) for the rest. At the lab's real compaction: `preTokens` 967,743, `postTokens` 23,767, duration 57,265 ms, summary 15,015 characters (about 6.3k tokens at 2.39 characters per token, w07b) [`s1_compaction_meta.txt`].

After the compaction, the next main request (visible request after each boundary): read about 26.6k (system prompt and tools), write about 40.2k (haiku runs: about 66,800 - 26,635); the lab's real one wrote 41,043 and read 50,455 (the prefix is larger there). So the post-compaction context is prefix + about 40k, whatever the size before.

## 3 what the platform re-injects after a compaction (character counts, one boundary of `runs/d1_plain`)

| entry after the boundary | characters |
|:--|--:|
| skill listing (`skill_listing`) | 34,710 |
| deferred tools (`deferred_tools_delta`) | 28,613 |
| MCP instructions | 8,901 |
| agent listing | 8,168 |
| summary (as the first user message) | about 5,300 |
| `instructions`, `session_context`, `environment`, `model`, `hook_success` (incl. resume_brief), `date` | about 3,400 |
| `compact_file_reference` x5 | 5 x about 160 (paths only; contents are not restored) |

Script: `__instrumenta__/w08e_postcompact_items.py`. So about 80k characters (about 30k tokens at 2.4-2.9 characters per token) of the 40k-token post-compaction write are the preamble the platform re-sends (the same listings explorer-w08-d priced at USD 14.78 as "skill listing" etc.), not the summary.

## 4 what the lab's `resume_brief.py` does

| fact | value | Label |
|:--|:--|:--|
| fires on `SessionStart` source `compact` and `resume` | yes: debug.log `Hooks: SessionStart:compact [python3 .../resume_brief.py] finished with status 0 (75-79 ms)`; 1 per compaction, 1 on `--resume`, also in a compacted subagent (e2: 3) | MEASURED |
| injected text in the test lab | 394 characters (a one-line wave note and one puzzle) | MEASURED |
| injected text in this lab (real `__statera__` and `__scrupuli__`) | 15,977 characters: `printf '{"cwd":"<lab>","source":"compact"}' \| python3 scripts/resume_brief.py \| wc -c` (the whole `wave-08.md` plus open puzzles) | MEASURED (size), ESTIMATE (about 5-6k tokens) |
| does not carry | the PI's own conclusions, the user's last instruction, what it was waiting for; those live only in the summary | CONJECTURE |

## 5 what survived (synthetic prose, haiku 5.5; planted facts: number, path, quoted sentence, audit code; 28 files with a random 6-letter ref code; compactions at about 170k)

| test | result |
|:--|:--|
| three user facts + audit code, in the PostCompact summary and in the answer after `--resume`, 13 compactions in 9 runs (c1-c5, d1, d2 and their precompact twins) | 4 of 4 in every run, both places |
| ref code of each of 28 files, answered after `--resume` (no tool), runs d1_plain, d1_precompact, d2_plain (28 files read, 2 compactions) | 28 of 28 exact; files read before both compactions (11) all exact; summary text held 20 of 28 (the 8 absent were read after the last compaction and are still in context as messages) |
| d2_precompact (22 files read before the session ended) | 22 of 22 exact |
| 5th word of line 100 of f0..f9 (ordinary prose, read before the compactions), d1_plain and d1_precompact | 0 of 10 exact, 10 UNKNOWN, 0 wrong. Control `e1_control_nocompact` (10 files read, no compaction): 10 of 10 exact |
| `--resume` of a compacted session | all four plant facts correct; the test-lab brief injected once |
| session continued to its end after compaction | c1 and c4 ended right after a compaction with the word "ok" (and e3, e3b, with no compaction at all, ended after one file with "ok"): an instruction-following flake of haiku on "say only ok", not shown to be caused by compaction. c2 ended with `rapid_refill_breaker` (window 100k: post-compaction context 47-50k refilled to 67k inside 3 turns, 3 times) |
