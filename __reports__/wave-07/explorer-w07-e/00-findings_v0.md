---
type: findings
wave: wave-07
author: explorer-w07-e
date: 2026-10-22
version: v0
decision-required: confirm
---

# The PI's skills listing and the workers' allowlists: what can be excluded (v0)

I stayed inside the brief. One deviation of method: the headless PI is haiku on the CLI (not Opus on Desktop), so its request 0 is 31.4k, not 46.7k; savings transfer only as a CONJECTURE.

## Result

Denying the `Skill` tool in the PI's `disallowedTools:` removes the whole skills listing and the Skill tool schema: request 0 fell from a mean of 31,544 (three baselines, range 31,409–31,738) to 19,591 and 19,889 (two cells), a drop of about 11.7–12.0k tokens (37%), and the PI still got `research-loop` by reading `${CLAUDE_PLUGIN_ROOT}/skills/research-loop/SKILL.md`; `/lab-status` still ran. Every other lever tried (`skillOverrides`, `Skill(name)` deny rules, disabling plugins) left most of the listing in place. For the workers, no allowlisted MCP server is worth dropping for tokens: MCP schemas are deferred in workers, so each server costs only its tool names (all four together 951–1,118 characters, ESTIMATE 200–380 tokens), and the one server no worker ever called, Wolfram, is 548 characters of names.

## Table

PI cells, headless haiku, `--agent murmuration:research-pi`, Claude Code 2.1.304, `--permission-mode auto`, fresh lab per cell, prompt P1 (P3 in v6, P4 in v7), `CLAUDE_CODE_SHELL=/bin/bash`. Request 0 = input + cache write + cache read of the first `assistant` record. [source: `__reports__/wave-07/explorer-w07-e/pi_table.md`, `cells/*/summary.json`, `__instrumenta__/w07e_pi_cell.py`, `__instrumenta__/w07e_pi_table.py`]

| Cell | What changed (export only) | Request 0 tokens | vs baseline mean 31,544 | Listing (skills, chars) | `research-loop` reached | `/lab-status` | Label |
|:--|:--|--:|--:|:--|:--|:--|:--|
| base, base_rep1, base_rep2 | nothing (three replicates; rep1 and rep2 were meant as v1 and v2 but a shell word-splitting slip put the flags into the cell name, so the flags never applied) | 31,409 / 31,738 / 31,485 | noise range 329 | 86, 29,957 | Skill tool | listed | MEASURED |
| v1_deny_skill | `Skill` appended to `disallowedTools:`; `skills:` frontmatter kept | 19,591 | -11,953 | 0, 0 | by Read (path in the prompt) | listed | MEASURED, n = 1 |
| v2_deny_skill_nofm | `Skill` denied, `skills:` frontmatter removed | 19,889 | -11,655 | 0, 0 | by Read (path in the prompt) | listed | MEASURED, n = 1 |
| v6_pluginroot_path | v2, plus one body line: "The research-loop procedure is the file `${CLAUDE_PLUGIN_ROOT}/skills/research-loop/SKILL.md`. Read it first." | 20,561 | -10,983 (includes the body line and a longer P3 prompt) | 0, 0 | by Read; the path in the system prompt is resolved (no literal `${...}`) | listed | MEASURED, n = 1 |
| v7_deny_skill_labstatus | v1; prompt is `/lab-status` | 21,701 (holds the expanded command, not comparable) | n/a | 0, 0 | not asked | the command ran (Bash `lab_status.py`, output returned) | MEASURED, n = 1 |
| v3_overrides_off | `--settings` with `skillOverrides: "off"` for all 91 other skills | 29,614 | -1,930 | 54, 25,382 | Skill tool | listed | MEASURED, n = 1 |
| v4_skill_rules | `--settings` with `permissions.deny: ["Skill(<name>)", ...]` for the 91 others | 31,394 | -150 (inside noise) | 86, 29,957 | Skill tool | listed | MEASURED, n = 1 |
| v5_plugins_off | `--settings` with `enabledPlugins: false` for 19 of the user's 20 installed non-builtin plugins (colgrep-mcp kept) | 29,200 | -2,344 | 41, 22,235 | Skill tool | listed | MEASURED, n = 1 |

Other numbers:

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Skill listing in the headless baseline vs the Desktop PI | 29,957 chars (86 skills) vs 30,072 chars (90) | MEASURED | `pi_table.md`; `__reports__/wave-06/research-pi/request0_breakdown.md` |
| Characters removed by denying `Skill` | listing 29,957 + Skill tool schema 1,877 = 31,834 chars for about 11.8k tokens, i.e. 0.37 tokens per character, above the 0.21–0.34 band of w05-c3 | MEASURED (tokens), derived ratio | `cells/base/loaded_tools.json`, `cells/v1_deny_skill/summary.json`; script below |
| Tools loaded at request 0 | baseline 11 (tools JSON 22,256 chars); with `Skill` denied 10 (20,377 chars) | MEASURED | transcripts via `w07e_pi_table.py` |
| `skills: [research-loop]` frontmatter on the main-thread PI | not applied: with it kept (v1), the SKILL.md text first occurs after the first assistant record, as a tool result; request 0 differs from v2 (frontmatter removed) by 298 tokens, inside the 329 baseline range | MEASURED, n = 1 each | `cells/v1_deny_skill`, `cells/v2_deny_skill_nofm` |
| Same frontmatter on a worker | applied: SKILL.md text sits in a user record before the first assistant record (3 of 3 explorers checked) | MEASURED | `worker_req0.tsv` files, check in this report's method |
| SKILL.md via the Skill tool vs via Read | the Skill tool substitutes `${CLAUDE_PLUGIN_ROOT}` in the text (`/private/tmp/.../plugin/skills/research-loop/references/working_defaults.md`); a Read leaves the literal `${CLAUDE_PLUGIN_ROOT}` (lines 99, 176–179 of SKILL.md) | MEASURED | `cells/base` and `cells/v6_pluginroot_path` transcripts |
| `${CLAUDE_PLUGIN_ROOT}` in an agent body | substituted in the system prompt (v6: resolved absolute path, literal absent) | MEASURED, n = 1 | v6 `api-request-shape` system |
| Skills the PI called, 6 PI sessions in the worktree project dirs | `murmuration:research-loop` 5; `writing-history:writing-history` 1; `dataviz` 1 | MEASURED | `pi_tools_used.tsv` (run), Skill inputs scan in the shell |
| MCP/other tools the PI called, same 6 sessions | colgrep `search` 4, `list_indexes` 2, `index_status` 1, `index_prune` 1 (one session); the rest Desktop's own (`ccd_turn`, `ccd_session`, `terminal`) | MEASURED | `pi_tools_used.tsv` |
| Docs: `skillOverrides` | "Plugin skills are not affected by `skillOverrides`"; hides user/project skills only | CITED https://code.claude.com/docs/en/skills (fetched; the first 100,000 of 110,500 characters read) | matches v3: 32 skills dropped, all plugin skills kept |
| Docs: stop a subagent invoking skills | "omit `Skill` from the `tools` list or add it to `disallowedTools`" | CITED https://code.claude.com/docs/en/sub-agents (first 100,000 of 109,896 characters) | v1 confirms for the main thread |
| Docs: `Skill(name)` rules | "`Skill(name)` for exact match, `Skill(name *)` for prefix" as permission rules | CITED skills page | v4: rules did not shrink the listing (86 listed); whether a call to a denied skill is refused was not tested |
| Docs on `--agent` and `skills:` | the page "doesn't say whether the `skills` field preloads skills in `--agent` mode" | CITED sub-agents page | v1 answers it: no, in 2.1.304 headless |

Workers, waves 1–6 (all subagent transcripts of the `murmuration:*` types on this machine; "wave" = project dirs of the Murmuration worktrees, "probe" = scratch and headless dirs; calls of the tool, subagents using it). [source: `worker_tool_calls.tsv`, `worker_subagents.tsv`, `__instrumenta__/w07e_worker_tools.py`]

| Type (class, n subagents) | Allowlisted but never called | Called, with counts |
|:--|:--|:--|
| explorer (wave 24, probe 299) | Wolfram (0 of 323), arxiv in wave (0 of 24; probes 2 calls of `search_papers` in 2 subagents), Glob, Grep | Bash 1024 (24), Read 56 (16), Write 29 (13), WebFetch 27 (4), context7 `query-docs` 20 (7) and `resolve-library-id` 6 (6), colgrep `search` 8 (7), WebSearch 2 (1), Edit 3 (3); probes: WebFetch 35 (6), WebSearch 6 (3) |
| author (wave 25, probe 70) | Wolfram (0 of 95), Glob (1 call, probe), Grep; arxiv wave 0 (probes 1 call) | Bash 2043 (25), Write 130 (17), Read 71 (21), Edit 53 (6), SendMessage 45 (24), colgrep `search` 4 (2), `doctor` 1 |
| reproducer (wave 47, probe 7) | Wolfram (0 of 54), Glob, Grep, Edit (2 calls) | Bash 1478 (47), Read 92 (39), SendMessage 51 (46), colgrep `search` 10 (6), Write 7 (4), Edit 2 |
| proof-adversary (probe 19, wave 0) | Wolfram (0), Glob, Grep, colgrep (0) | Bash 56 (19), Read 51 (19), SendMessage 2 (2); no wave run of this type exists |

Worker request 0 (2.1.304; the newest 4 explorers and the newest 3 each of reproducer and author among the wave subagent transcripts): 14,163–14,925 tokens, 8 loaded tools (tools JSON 9,366 chars, identical across types), MCP tools all deferred. Deferred-name cost per server, from the first `deferred_tools_delta`: [source: `worker_req0.tsv`, `__instrumenta__/w07e_worker_req0.py`]

| Server (names in the worker's deferred list) | Names | Characters of names | Tokens at 0.21–0.34 | Label |
|:--|--:|--:|:--|:--|
| WolframToolkit (all worker types) | 15 | 548 (from the PI-session listing; the worker listing carries the same 15 names) | about 115–186 | ESTIMATE |
| plugin colgrep (all four) | 9 | 391 (headless listing) | about 82–133 | ESTIMATE |
| arxiv (explorer, author) | 4 | not split out; the explorer total is 1,118, reproducer 951, author 1,051 | under 100 | ESTIMATE |
| context7 (explorer) | 2 | 60 | about 13–20 | ESTIMATE |
| whole deferred list of a worker | explorer 1,118, author 1,051, reproducer 951 chars | | explorer 235–380, reproducer 200–323 | ESTIMATE |

Other worker facts:

- 61 of the 72 reproducer and author wave subagents (42 of 47 reproducers, 19 of 25 authors) issue a `ToolSearch` for `SendMessage`, the first or an early call (`worker_subagents.tsv`): one extra request per worker, because `SendMessage` is deferred in workers (MEASURED counts; the token cost of that request is not computed here; it re-reads a cache of at least 14k tokens).
- 4 of 25 wave authors searched for context7 by keyword (`ToolSearch` queries "context7 ..."), though the author allowlist has no context7 (MEASURED queries; whether they then found it was not read).
- `Monitor` was called in wave transcripts by 1 explorer, 2 authors and 6 reproducers although it is in no allowlist (`worker_subagents.tsv`); `Skill` once by 1 author. The allowlist is not a closed set in every transcript; those could be agent files of earlier waves (CONJECTURE).
- The `skills: [research-loop]` frontmatter injects the 9,974-character SKILL.md into every worker before its first request: ESTIMATE 2.1k–3.4k tokens, 15–23% of a 14.2–14.9k request 0 (characters from `wc -c skills/research-loop/SKILL.md`). Not a candidate for removal here (workers need the labels), but it is the largest single lever inside a worker.

## Worst-fitting case

1. The story "denying Skill is free" fits worst in two places. (a) `SKILL.md` read by Read keeps the literal `${CLAUDE_PLUGIN_ROOT}` in its table of references (5 lines), while the Skill tool substituted it; v6 never followed a reference, so whether the PI resolves them by itself is untested. (b) The PI did call `writing-history` and `dataviz` once each in 6 sessions; with `Skill` denied those become unreachable unless the PI reads their files by path.
2. The headless numbers do not equal the Desktop numbers: haiku headless 11 tools and 31.4k; the Desktop PI 23 tools and 46.7k. A bare drop of 11.8k tokens is a measured headless value. Opus tokenisation could differ.
3. For the workers, "drop Wolfram" saves about 115–186 tokens of a 14k request, the same size as the 329-token noise between replicates; and nothing in 323 + 95 + 54 subagents ever called it. Cheap to drop, nearly worthless to drop.

## Not covered

- Desktop. All PI cells are headless CLI. Whether `disallowedTools: Skill` removes the listing in a Desktop session is untested (Desktop injects other skills, e.g. via `SuggestSkills`; the denylist there already removes `SuggestSkills`).
- A default-mode (not auto) session: the Read of the SKILL.md outside the working directory may prompt in default mode; I ran auto only.
- `Skill(name)` deny rules: only the listing was measured; whether a denied call is refused at call time was not tested. The user's request for "permission rules `Skill(...)`" is therefore half answered (no effect on the listing).
- `/lab` (user-only, writes files) with `Skill` denied; only `/lab-status` was run.
- Per-server schema cost when a worker loads an MCP server through ToolSearch: ToolSearch results in the transcripts are 56–600 characters of references; the schemas are not in them and the later request sizes are mixed with tool results. The brief's "loaded schemas against deferred names" is answered only for the deferred side.
- Sonnet workers: the 14.2–14.9k figures are from existing wave transcripts; I ran no worker session. The MCP-instruction block (8,652 characters of server instructions in the headless PI: context7, colgrep, svelte, claude.ai connectors) and the agent-type listing (8,168 characters) are the two next-largest PI blocks I saw; I did not test denying them (`mcp__svelte__*`, `Agent(...)` restriction).
- n = 1 per variant; 10 of 10 headless sessions used.

## Steering questions

- [now] Land `Skill` in the PI's `disallowedTools:` plus one body line that gives `${CLAUDE_PLUGIN_ROOT}/skills/research-loop/SKILL.md` and the resolved root, accepting the loss of `writing-history`/`dataviz` by name? Or keep `Skill` and trim the listing to the skills the PI uses, which only plugin disabling does (v5, -2.3k)?
- [now] Should the research claim for this be one claim (PI request 0 with and without the line, on Desktop, n >= 3 each, as for w06-c1), or is the headless pair enough to register the rule?
- [now] Is leaving the workers' allowlists as they are the decision, given the numbers (200–380 tokens for all deferred MCP names)?

## Pointers

All under `__reports__/wave-07/explorer-w07-e/` unless stated. Scratch: `/private/tmp/murmuration-w07/explorer-w07-e/` (export, runs with full stdout.jsonl).

- `pi_table.md`: `python3 -I __instrumenta__/w07e_pi_table.py /private/tmp/murmuration-w07/explorer-w07-e`.
- `cells/<cell>/summary.json, init_lists.json, loaded_tools.json`: one per headless cell; produced by `python3 __instrumenta__/w07e_pi_cell.py <scratch> <cell> <scratch>/export [--deny Skill] [--noskillsfm] [--settings cfg_*.json] [--appendbody TEXT] [--prompt P1|P3|P4]` (`runv.sh` holds the v1–v5 launch; v6 and v7 were single calls; the export is `git archive HEAD` at bb7a713 with every agent file's `model:` set to haiku). Cost of the ten sessions: about USD 0.06 in total (`cost_usd` in each summary).
- `cfg_overrides.json`, `cfg_skillrules.json`, `cfg_plugins_off_keep_colgrep.json`: the three `--settings` files (scratch settings, never a repo file).
- `worker_tool_calls.tsv`, `worker_subagents.tsv`: `python3 -I __instrumenta__/w07e_worker_tools.py <out>`.
- `worker_req0.tsv`: `python3 -I __instrumenta__/w07e_worker_req0.py 4`.
- `toolsearch_results.tsv`: `python3 -I __instrumenta__/w07e_toolsearch_cost.py`.
- `pi_tools_used.tsv`: `python3 -I __instrumenta__/w07e_pi_tools_used.py <transcript of a headless base cell>` (6 PI sessions in the worktree project dirs).
- Helpers: `__instrumenta__/w07e_pi_cell.py`, `w07e_pi_table.py`, `w07e_worker_tools.py`, `w07e_worker_req0.py`, `w07e_toolsearch_cost.py`, `w07e_pi_tools_used.py` (commit given by the commit that adds them).
- Docs fetched (WebFetch, truncated at 100,000 characters each): https://code.claude.com/docs/en/skills, https://code.claude.com/docs/en/sub-agents. https://code.claude.com/docs/en/settings was fetched but returned only the page about scopes; I did not read `settings-reference`, so its skill keys are UNVERIFIED here.
