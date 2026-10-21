---
type: findings
wave: wave-07
author: explorer-w07-g
date: 2026-10-22
version: v0
decision-required: none
---

# The per-call cost of a trivial Bash call in auto mode: classifier, hooks, shell, and what the loop could drop (findings v0)

Stayed inside the brief, with three additions from reading, not from sessions: the worker records re-cut by command shape (`w07g_trivial_split.py`), a cache-TTL break-even from explorer-w07-b's `requests.tsv`, and a read of the 2.1.304 binary. One deviation: the brief's "no plugin" arm still loads the user's enabled plugins, and one of them (`colgrep-mcp`) puts a `uv run python` hook on every Bash call; I made it a third factor (switched off per run with an inline `--settings` JSON, no file edited). 16 headless haiku sessions (the cap), serial, one batch, load average 2.97 to 8.16 (`loadavg.tsv`, one line per session). Labels: MEASURED, ESTIMATE, CONJECTURE, CITED, CHECKED. n per arm is two sessions of 7 calls; the paired differences below are small against the session-to-session spread, and I say where.

## Result

MEASURED (n = 14 Bash calls per arm, calls 2-8 of two sessions, haiku, scratch folder): the tool phase of a trivial Bash call (`ls`, `cat`, `pwd`, `date`, `echo`...) is median 55 ms in default mode with a narrow `--allowedTools` list (p90 83), 709 ms in auto mode (p90 1,142), and 1,054 ms in auto mode with the user's colgrep hook and the lab plugin both on (p90 1,282), the arm that looks like a worker. The auto-mode cost is the classifier wait: median 628 ms (p90 1,080) of the 709. The shell run is 51-74 ms in every arm. [source: `tables.md` section 1]

MEASURED, reconciles the "unexplained 0.6-0.9 s": the worker records' 1.49 s is not a trivial call. Re-cut by command shape (1,869 single-call classifier-decided Bash turns, results under 3,000 characters), bare `ls/cat/wc/...` is 1.02 s (n = 3), single grep/sed 0.99 s (n = 7), pipes of read-only words 1.24 s (n = 42), `cd dir && ...` 1.34 s (n = 47), `git` 1.47 s (n = 54), and 1,623 of the 1,869 run a program (python, uv, heredoc, sleep) at 1.72 s (p90 51 s). The w07b "trivial" set included `cd`, `git`, `grep`, `sed` as first words, so it carries the commands' own run time. The floor of about 1.0 s in the workers' records equals the worker-like headless arm (1.05 s). So the ledger closes: classifier about 0.63 s + PreToolUse hooks (partly hidden, below) + PostToolUse hook 0.07-0.08 s + run 0.06 s + about 0.05 s of plumbing = about 1.0 s. [source: `worker_command_shape.md`, `tables.md`]

MEASURED: the hooks. The user's settings have no hook on Bash; the only Bash hook outside the lab is the `colgrep-mcp` plugin's PreToolUse `colgrep_policy.py` run as `uv run --no-project --quiet python`: median 194 ms, p90 554, max 1,979 (n = 32). The lab's: PreToolUse `permission_guard.py` 108 ms (n = 32), PostToolUse `run_hook.py budget` 72 ms (n = 32), PostToolBatch `run_hook.py budget` 60 ms (n = 32). Per session once: user `tool_routing_policy.py` 150 ms and `reset_plan_directive_marker.py` 171 ms (SessionStart), `inject_plan_directive.py` 124 ms (UserPromptSubmit), colgrep SessionStart 258 ms, lab `user_words.py` 184 ms. [source: `tables.md` section 3]

CHECKED (n = 14 per arm, plus the trial's 8): in auto mode a PreToolUse hook runs concurrently with the classifier: the wait from the tool_use record to dispatch is 642 ms with the colgrep hook (median hook 215 ms) against 631 ms without; hook and the remaining classifier wait are negatively rank-correlated (-0.32 in arm A, -0.20 in arm C); in the trial a 1,383 ms hook was followed by a 4 ms classifier wait and a 1,979 ms hook by 9 ms. The PostToolUse hook is not hidden: dispatch end to the result record is 69-80 ms in the lab-plugin arms against 1-2 ms without. [source: `tables.md` sections 1 and 2; `calls.jsonl`] The two lab-plugin arms do not follow the clean picture (below, worst case).

MEASURED, mixed: the classifier wait does not show growth with the transcript at 42k to 102k tokens of context: early calls 710 ms (n = 8), late 840 ms (n = 10); by session L0 534 to 831 ms (+297), L1 978 to 885 ms (-93). Two identical sessions differ by more than that (B0 528 ms against B1 1,015 ms, median wait to dispatch). The smallest context I could run is 42k tokens (the user's tools and skills), so "early in a session" is not small. [source: `tables.md` section 4]

MEASURED, n = 1 per variant: four reads of four 20-line files. From the prompt to the last assistant record: four Reads in one message 2.83 s (2 requests, 0 classifier calls); one Bash chaining four `cat` 3.39 s (2 requests, 1 classifier call); four Bash calls in one message 3.79 s (2 requests, 4 classifier calls, which ran concurrently: waits sum to 4,589 ms but first tool_use to last result is 1.79 s against 1.17 s for the single chained call); four Reads in four messages 5.11 s (5 requests, 0 classifier calls). USD 0.0041, 0.0039, 0.0040, 0.0053. Reads never reach the classifier (phase 6-30 ms for a 20-line file; 257-317 ms for a 45 kB file). [source: `tables.md` section 5]

CHECKED by reading the 2.1.304 binary (not run): a subagent's prompt-cache TTL is 5 minutes by default, and there are four ways to change it, one of them per agent file. The main conversation (query sources `repl_main_thread*`, `sdk`, `auto_mode`, `memdir_relevance`) uses the 1-hour TTL on a subscription within its limits; everything else, "subagents, workflows, background and helper requests", gets 5 minutes unless set. Order of resolution in the binary's `ssn`/`Obe`: `FORCE_PROMPT_CACHING_5M` (forces 5m), then env `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` (main: `CLAUDE_CODE_PROMPT_CACHE_TTL`), then settings key `subagentPromptCacheTtl` (main: `promptCacheTtl`), then the agent file's `experimental: { cacheTtl: "5m" | "1h" }` frontmatter, then `ENABLE_PROMPT_CACHING_1H=1`, else 5m (the 1-hour default of the main thread is an allowlist delivered by the server flag `tengu_prompt_cache_1h_config`). The setting's own description: "1-hour cache writes are billed at a higher rate". [source: strings of `/Users/hacker/.local/share/claude/versions/2.1.304`, extract in `/private/tmp/murmuration-w07/explorer-w07-g/claude_strings.txt`, not copied; no docs fetched]

ESTIMATE (formula in `ttl_breakeven.md`): 1 hour for every worker is a wash. Re-writes after a cache drop: 23 (4.44M tokens; saved USD 10.65 at write minus read price 2.5 - 0.1), against an extra USD 10.23 on all other cache writes (11.26M write tokens x (4.0 - 2.5) per Mtok, prices from `scripts/lab_status.py` PRICES for Sonnet 5.5): net +USD 0.41 of USD 65.75. By type: authors +4.49 (13 workers, 17 of the 23 drops, USD 43.90 spend), reproducers -2.27, explorers -1.52. The frontmatter key is the lever that fits; whether a plugin agent file honors `experimental.cacheTtl` is not tested.

## Table

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Tool phase, trivial Bash, default + allow list (arm F) | 55 / 83 / 106 ms median / p90 / max, n = 14; classifier wait 1 ms; run 51 ms | MEASURED | `tables.md` s.1 |
| Same, auto (arm B, colgrep off, no lab plugin) | 709 / 1,142 / 1,448 ms, n = 14; classifier wait 628 / 1,080 / 1,358; run 60 | MEASURED | `tables.md` s.1 |
| Same, auto + colgrep hook (arm A) | 753 / 1,747 / 2,294 ms, n = 14; hook 215 / 1,135 / 1,979; tool_use to dispatch 642 | MEASURED | `tables.md` s.1 |
| Same, auto + colgrep + lab plugin (arm C, worker-like) | 1,054 / 1,282 / 1,756 ms, n = 14; to dispatch 877; PostToolUse 80; run 56 | MEASURED | `tables.md` s.1 |
| Same, auto + lab plugin, colgrep off (arm D) | 970 / 1,297 / 1,519 ms, n = 14; to dispatch 782; PostToolUse 69 | MEASURED | `tables.md` s.1 |
| Auto against default, per pair (B - F, rep 0 / rep 1) | +555 / +1,009 ms median phase | MEASURED | `tables.md` s.2 |
| Per-session spread inside one arm (median phase) | A 1,048 / 597; B 608 / 1,066; C 1,019 / 1,123; D 1,175 / 954; F 53 / 57 ms | MEASURED | `tables.md` s.1 |
| Hook and classifier overlap | A to-dispatch 642 vs B 631 ms; trial: hook 1,383 ms then wait 4 ms | CHECKED (n = 14 + 8); mechanism CONJECTURE | `tables.md` s.1; `calls.jsonl` |
| Hook durations per run | see Result; PreToolUse colgrep 194 ms (p90 554), guard 108, PostToolUse 72, PostToolBatch 60 | MEASURED | `tables.md` s.3 |
| Worker records by command shape | bare 1.02 s (n 3), grep/sed 0.99 (7), pipes 1.24 (42), cd 1.34 (47), git 1.47 (54), programs 1.72 (1,623), all 1.66 (1,869) | MEASURED | `worker_command_shape.md` |
| Classifier cost over the three waves | 2,348 classifier-decided calls x 0.63 s = 1,480 s = 1.9% of 76,439 s summed wall (w07b's differential 3,100 s counted run time too) | ESTIMATE: n x median wait of arm B | `__reports__/wave-07/explorer-w07-b/00-findings_v0.md` for n and wall |
| Lab hooks' visible cost over the three waves | PostToolUse 72 ms x 2,883 calls + PostToolBatch 60 ms x about 2,625 tool requests = 208 + 158 = 366 s = 0.48% of summed wall; the PreToolUse guard assumed hidden under the classifier | ESTIMATE: n x median; hidden-guard is CONJECTURE | this report; w07b for n |
| Context length | early (42k tokens) wait 710 ms n 8; late (102k) 840 ms n 10; L0 +297 ms, L1 -93 ms | MEASURED | `tables.md` s.4 |
| Four ways (n = 1 each) | Reads x4 in one message 2.83 s, 2 requests, 0 classifier; chained `cat` 3.39 s, 2, 1; 4 Bash in one message 3.79 s, 2, 4; Reads in 4 messages 5.11 s, 5, 0 | MEASURED, n = 1 | `tables.md` s.5 |
| Subagent cache TTL | default 5 m; levers: env `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`, setting `subagentPromptCacheTtl`, agent frontmatter `experimental.cacheTtl`, `ENABLE_PROMPT_CACHING_1H=1`; main thread 1 h on a subscription by server allowlist | CHECKED by reading the binary, not run | binary 2.1.304 strings |
| 1 h for all workers | saves USD 10.65, costs 10.23, net +0.41 of 65.75; authors only +4.49 of 43.90 | ESTIMATE | `ttl_breakeven.md` |
| Allow rules remove the classifier wait | 1-3 ms in auto mode with narrow rules (wave 5, n = 5 per command) | CITED: `__reports__/wave-05/explorer-w05-f/00-findings_v0.md` | not re-run |

## Worst-fitting case

The story that fits best: the classifier is the per-call cost (about 0.63 s), PreToolUse hooks hide inside it, the PostToolUse and PostToolBatch hooks do not (about 0.13 s per call), and nothing else is left.

Fits worst, in three parts.

1. The same configuration is not the same twice. Arms B0 and B1 (identical command line) have median wait to dispatch 528 ms and 1,015 ms; L0 and L1, 581 and 909 ms. That 0.4-0.5 s swing is larger than every effect except auto against default. Arms C and D (lab plugin) ran under load 5.3-8.2, arms A and B under 3.4-4.5, so the lab plugin's cost cannot be read from arm differences: D - B is +150 ms and C - A is +236 ms in the to-dispatch medians, bigger than a guard that is hidden in the classifier should add (A - B is +11 ms). The estimates of hook cost therefore come from the hook durations the log records, not from arm differences. [source: `tables.md` s.1, s.2, s.6]
2. The overlap is read from medians and a rank correlation of n = 14; in the trial the classifier wait after a long hook was 4 and 9 ms, which fits overlap, but the three auto arms with hooks all show a wait of 640-880 ms, so the classifier is not always finished when the hook is. A direct test would start the classifier and hook timestamps in one record; the debug log only holds the hook's finish and the dispatch.
3. Within L0 the classifier wait rises monotonically over the session (498, 519, 494, 550, 549, 581, 809, 849, 831, 929 ms) as the context grows 42k to 103k; in L1 it does not (904 ... 941, with a dip at 738). Typical case: the median of the late calls is only +130 ms over the early ones. [source: `tables.md` s.4]

Also against the story: the Read of a 45 kB file takes 257-317 ms in these sessions where the worker records give 0.16 s median; the workers' Reads are small files.

## Not covered

- Subagent cache lifetime was read in the binary, not run (no session was left; 16 used). Not tested: whether `experimental.cacheTtl` in a plugin agent file is honored, and what query source a subagent request carries.
- Sonnet and workers in parallel: all sessions are haiku, one at a time, one scratch folder that is not a git repository (`git_state.root` is null there; in the worker records, trivial calls with a root set take 1.06 s, n = 12, so I saw no sign that git state costs, but I could not run a repo cwd).
- The classifier's own duration is still not in any record; "classifier wait" is `permissionDecisionMs` from the debug log, the time from the last PreToolUse hook's end to dispatch, which under overlap understates the classifier call.
- Replicates: two sessions per arm, one per four-ways variant, two for the context test. Per-pair spread is shown, effects under about 0.4 s are not resolved. No claim here about the plugin's hooks from arm differences.
- Allow rules in auto mode were not re-run (CITED from wave 5). The permission layer is the user's, so no rule was proposed as a change.
- The `PostToolBatch` hook's place in the loop (after the tool phase, before the next request) is inferred from timestamps; its 60 ms is not in any tool phase.
- Reads outside the working directory in auto mode, and large Bash outputs, were not tried.

## Steering questions

- [now] Allow rules for read-only commands (wave 5: 1-3 ms instead of about 630 ms) would be the only large per-call lever (about 1.9% of worker wall at 100% coverage; ESTIMATE). It is the permission layer, which is the user's. Shall the PI hand the user the list of command shapes from `worker_command_shape.md` (bare read-only commands are 3 of 1,869 calls: most worker Bash calls run a program, and rules for `python3 ...` are not safe), or leave it?
- [now] Shall one headless session test `experimental.cacheTtl: 1h` in an author agent file (the estimate says authors +USD 4.49 of 43.90 over three waves, reproducers and explorers lose)?
- [later] The colgrep `uv run` hook (194 ms median, 1,979 ms max) is hidden under the classifier in auto mode, but would be the floor if allow rules removed the classifier; it belongs to the user's plugin.

## Pointers

Scripts (committed, cited as `__instrumenta__/<file>@e68caab`): `w07g_run.py`, `w07g_parse.py`, `w07g_table.py`, `w07g_ctx_git.py`, `w07g_trivial_split.py`, `w07g_ttl_breakeven.py`. Raw records in `__reports__/wave-07/explorer-w07-g/`: `calls.jsonl` (119 Bash/Read calls, one row each, message ids dropped), `sessions.jsonl` (16 sessions), `loadavg.tsv` (label, start epoch, load1/load5 before, load1/load5 after, wall s), `tables.md`, `worker_command_shape.md`, `ttl_breakeven.md`. Debug logs, run JSON and the binary's strings stay in `/private/tmp/murmuration-w07/explorer-w07-g/` (`dbg/`, `runs/`; they hold account identifiers, not committed). The trial session (arm A, rep 0) was run by hand with the same command line; its load was not logged by the runner (`uptime` read 5.99 a few minutes earlier).

Commands (cwd `/private/tmp/murmuration-w07/explorer-w07-g/work`, `CLAUDE_CODE_SHELL=/bin/bash`, all `--model haiku --output-format json --strict-mcp-config`, no budget flag):
- plan, run in order B0, then seed 7: `python3 -I __instrumenta__/w07g_run.py /private/tmp/murmuration-w07/explorer-w07-g --only <labels>`; about 20 s per session, USD 0.004-0.065 each (the 13-call context sessions 0.064).
- parse and tables: `python3 -I __instrumenta__/w07g_parse.py <S> <S>/parsed; python3 -I __instrumenta__/w07g_table.py <S>/parsed <S>/runs/loadavg.tsv > tables.md`.
- worker records: `python3 -I __instrumenta__/w07g_trivial_split.py w4=<T4> w5=<T5> w6=<T6>`, `python3 -I __instrumenta__/w07g_ttl_breakeven.py __reports__/wave-07/explorer-w07-b/requests.tsv`.
- Arms: A auto; B auto + inline `--settings '{"enabledPlugins":{"colgrep-mcp@cracking-shells":false}}'`; C auto + `--plugin-dir <git archive of HEAD 0d39197>`; D = B + plugin; F `--permission-mode default --allowedTools "Bash(ls *),Bash(cat *),Bash(head *),Bash(wc *),Bash(echo *),Bash(pwd),Bash(date),Bash(ls),..."`; W1-W4 the four ways; L0, L1 the 13-step context test (5 Bash, three 40 kB Reads, 5 Bash).
