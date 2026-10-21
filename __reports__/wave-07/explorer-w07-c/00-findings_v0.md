---
type: findings
wave: wave-07
author: explorer-w07-c
date: 2026-10-22
version: v0
decision-required: none
---

# Hooks without a process per call: `async`, `http`, exec form, fewer siblings (findings v0)

No leaving of the brief, except one addition: the probes showed that the hook's start form (shell form against exec form with `args`) matters more than anything else tried, so I measured it too (`sib*` against `exec*`, and a local micro-benchmark).

Claude Code 2.1.304, macOS, `claude -p --model haiku`, default permission mode with `--allowedTools Bash` (no auto classifier, no bypass), `CLAUDE_CODE_SHELL=/bin/bash`, throwaway plugin `w7c` (built by `__instrumenta__/w07c_run.py@07cd64c`). 15 headless sessions, all used (about USD 0.11 as `claude` reports it). Machine load average was about 9 during the timing runs (other agents were running), so every absolute millisecond figure below is inflated and only the within-table comparisons are meaningful. Everything is `-p` mode: interactive-mode behaviour (what a human sees, what wakes an idle session) was not run.

## Result

- **`async: true` (MEASURED, n = 1 session, 10 tool calls)**: the tool loop does not wait. A 6.0 s async hook started 2.1 s after its tool call and the model made three further tool calls while it ran. Its `additionalContext` reached the model at the first tool boundary after the hook exited (about 3.4 s after it exited, because a 3 s sync hook was in the way), and the model quoted it. An async hook can neither deny nor block: an async `PreToolUse` deny and an async `PostToolUse` `decision: block` were recorded as `async_hook_response` and had no effect (the denied `echo` ran). An async hook that exits 1 with stderr leaves an `async_hook_response` record with `exitCode: 1` and the model did not see it (silent). An async hook still running when `-p` ends is cancelled and its output is lost (the 8 s hook started 0.4 s before the final answer: no end line, debug line `Hook PostToolUse:Bash (PostToolUse) cancelled`). Spawn cost of an async hook as the platform records it: "moved to the background" in 1 to 4 ms.
- **`asyncRewake` did not run in the background here (MEASURED, n = 1)**: the 2 s hook ran in the foreground (debug line "finished with status 2 (2572ms)", no "moved to the background"), the tool result waited for it (3.0 s against about 1.1 s), and exit 2 with stderr reached the model as a `hook_blocking_error` (the model quoted `REWAKE-NONCE`). The docs call it a background hook that wakes Claude. In `-p` there is no idle session to wake, so this may be a `-p` effect.
- **`http` hooks, latency (MEASURED, n = 17 fast calls, 3 sessions)**: the platform's own debug lines "HTTP hook POST" to "response status" give median 2 ms (3 for `/ok`), p90 5, max 10 (millisecond resolution); the server's own handling was 0.2 to 0.3 ms. The `mcp_tool` figures of w06-c6 were median 1 ms, p90 6, max 13 (n = 337). The two are the same within the clock. A command hook in the same sessions: 36 to 42 ms in exec form, 114 to 116 ms in shell form (platform "finished ... (N ms)", loaded machine). The client is axios (`User-Agent: axios/1.15.2`), JSON body, `Content-Type: application/json`.
- **`http` payload equals the command hook's stdin (MEASURED)**: 11 of 11 PreToolUse, 11 of 11 PostToolUse, 3 of 3 PostToolBatch, 1 of 1 SubagentStart, 2 of 2 SubagentStop pairs have identical key sets and identical values (the ground-truth command hook ran in the same session; pairs matched by `tool_use_id` or timestamp). `agent_transcript_path` is in the SubagentStop body, as with the command hook. Nothing needed to be substituted, unlike the `mcp_tool` templates of w06-c6.
- **`http` failure with `"onFailure": "block"` is loud to the model on the events that honour it, and the behaviour differs by event (MEASURED, one session per event, each failure mode once)**:
  - `PreToolUse`: the call is blocked and the model gets the error as the tool result (`is_error`): `PreToolUse:Bash hook error: [http://127.0.0.1:PORT/ok]: failed; blocking because onFailure is "block"` followed by the cause (`connect ECONNREFUSED`, `timed out`, `HTTP 500 from ...`, `HTTP 403 from ...`, `HTTP hook must return JSON, but got non-JSON response body: ...`). The same for server down, hanging (3 s `timeout`), garbage text, a JSON array, a 500 and a 403 from a missing token (a header variable not listed in `allowedEnvVars` is replaced by an empty string and the server answers 403).
  - `PostToolUse`: the tool has already run; the same text reaches the model as a `hook_blocking_error` (the model quoted it for all 8 failure and block cases).
  - `PostToolBatch`: a dead or hanging server ends the session: `terminal_reason: "hook_stopped"`, `result: ""`, `stop_reason: tool_use`, `is_error: false`, exit code 0, empty stderr (2 of 2 runs, dead and hanging). Only the transcript record `hook_stopped_continuation` and the JSON field `terminal_reason` say why. A worker would be stopped with no hand-back.
  - `SubagentStop`: `onFailure` has no effect (docs, and measured: dead server gives a `hook_non_blocking_error` record, the worker stopped normally, the model saw nothing).
  - Default (`continue`): the same six failure modes on Pre and Post (`http_ctl`, 10 of 10) let the tool run, the model sees nothing, and the transcript holds `hook_non_blocking_error` (with the cause in `stderr` and the status in `exitCode`) or `hook_cancelled` for a timeout. The same silence as the `mcp_tool` failed restart of w06-c6 (m4 b).
- **`http` can do what the lab's hooks do on the events tried (MEASURED, n small)**: PreToolUse deny (`permissionDecision`), PreToolUse and PostToolUse `additionalContext` (both quoted by the model), `SubagentStart` `additionalContext` (reached the worker), `PostToolBatch` `additionalContext` (reached the worker), SubagentStop `decision: block` once per `agent_id` (the worker got `HTTPBLOCK-NONCE-ONCE` as stop-hook feedback and continued), PostToolUse `decision: block` (the model saw it as a hook error).
- **Siblings of one event run concurrently but are started one after another (MEASURED, one session per arm, 8 calls each)**: 8 siblings each sleeping 0.5 s finished in 860 ms (shell form) or 645 ms (exec form) from the first start to the last end, not 4000 ms; but their start times are spaced 40 ms (shell form) or 14 to 15 ms (exec form) apart, steady across calls. So each added sibling delays the start of the last one and loads the machine; it does not queue behind the others' run time. This agrees with the docs' "run in parallel" and with the "+40 ms each" of the earlier waves, and says what the +40 ms is: the platform's launch interval.
- **Exec form is about 3 times cheaper to start than shell form (MEASURED in-session, one session per arm; corroborated outside by a micro-benchmark)**: `{"type":"command","command":"python3","args":["-S","-I","${CLAUDE_PLUGIN_ROOT}/scripts/hook.py","label"]}` ran the same script as the lab's string form; platform duration median 36 ms (p90 54) against 116 ms (p90 171) for the PostToolUse hook alone (N = 1); tool_use to tool_result of a whole call (Pre + Post hooks) 174 ms against 314 ms. Outside Claude Code (40 interleaved starts, load 9): `sh -c` 152 ms, `bash -c` 107, `zsh -c` 108, direct exec 54; a shell alone: `sh -c :` 81, `bash -c :` 40. So the shell is roughly half of a Python hook start on this machine. Whether the platform runs `sh -c` or the `CLAUDE_CODE_SHELL` shell for hooks was not isolated.
- **Per added sibling, tool call cost (ESTIMATE from the medians above)**: tool_use to tool_result median 314 ms (1 sibling) to 985 ms (8 siblings) in shell form, 174 to 444 ms in exec form; with N hooks on both Pre and Post that is about 48 ms (shell) and 19 ms (exec) per added hook start. [formula: (median at N=8 minus median at N=1) / 7 / 2; inputs `siblings_table.md`]

## Table

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| async loop wait | 6.0 s async hook, 3 further tool calls ran before it ended | MEASURED n=1 | `async_timeline.txt`, `runs/async/` |
| async result delivery | `additionalContext` attached at the first tool boundary after exit; model quoted it | MEASURED n=1 | `async_timeline.txt` line at 11481 ms |
| async deny, async block | no effect, recorded as `async_hook_response` | MEASURED n=1 each | `runs/async/transcript.jsonl` |
| async failure (exit 1, stderr) | record only; the model's answer: "ASYNC-FAIL: none" | MEASURED n=1 | `runs/async/run.json` |
| async at `-p` teardown | cancelled, output lost | MEASURED n=1 | `runs/async/dbg.log` (`cancelled`), `hooks.log` (no end line for Z-END) |
| asyncRewake in `-p` | ran foreground 2572 ms, tool result waited, exit 2 reached the model | MEASURED n=1 | `async_timeline.txt` 16698 to 18706 ms |
| http latency (platform POST to response) | median 2 ms, p90 5, max 10, n = 17 | MEASURED | `http_latency_table.md` |
| mcp_tool latency (for comparison) | median 1 ms, p90 6, max 13, n = 337 | CITED | `__pondus__/w06-c6.md` row m5 |
| http payload equals command stdin | 28 of 28 pairs identical (11 Pre, 11 Post, 3 Batch, 1 Start, 2 Stop) | MEASURED | `fields_table.txt` |
| Pre, block, 6 failure modes | blocked, error text to the model, 6 of 6 failure modes plus the deny and the block (the same text in 3 sessions: this one and the two with the design error described under the worst case) | MEASURED | `runs/http_pre/` |
| Post, block, 6 failure modes + decision block | model saw `hook_blocking_error`, 8 of 8 | MEASURED | `runs/http_post/` |
| PostToolBatch, block, dead or hanging server | session ends, `terminal_reason: hook_stopped`, empty result, exit 0 | MEASURED 2 of 2 | `runs/batch_dead/run.json`, `runs/batch_hang/run.json` |
| SubagentStop, block-on-failure, dead server | no effect, `hook_non_blocking_error` only | MEASURED 1 of 1; CITED docs | `runs/sub_stop_dead/`, docs `onFailure` section |
| default onFailure, 5 failure modes x Pre and Post | tool ran, model silent, transcript record only | MEASURED 10 of 10 | `runs/http_ctl/` |
| sibling launch interval | 40 ms (shell form), 14 to 15 ms (exec form) | MEASURED | `siblings_table.md` |
| sibling concurrency | 8 x 0.5 s sleepers: 860 ms (shell), 645 ms (exec) | MEASURED | `siblings_table.md` |
| shell vs exec start, in session | 116 vs 36 ms platform duration (PostToolUse, N=1) | MEASURED, one session per arm | `siblings_table.md` |
| shell vs exec start, outside | `bash -c` 107 ms, `sh -c` 152 ms, exec 54 ms (load 9) | MEASURED | `shell_vs_exec.md` |
| timeout default for http hooks | 600 s (30 s on UserPromptSubmit) | CITED | https://code.claude.com/docs/en/hooks (fetched 2026-10-22; copy `docs_hooks_2026-10-22.md`) |
| `async` only on command hooks; no timeout enforced; async deny/decision fields "have no effect" | as the docs say, and as measured | CITED / MEASURED | docs section "Run hooks in the background" |
| `onFailure` has no effect on `Stop`, `SubagentStop`, `TaskCompleted`, `TeammateIdle`, nor on async hooks | CITED; SubagentStop measured | CITED | docs section "Block the action when a hook fails" |
| PI environment: user-level `colgrep_policy` PreToolUse hook (`uv run`) | median 431 ms per Bash call, n = 10, max 583 (load 9) | MEASURED (default setting sources) | `runs/async/dbg.log` |

## Worst-fitting case

- **For "http with onFailure block is a safe, loud replacement for a resident server"**: it is loud on PreToolUse and PostToolUse only. On `PostToolBatch` it is too loud: it ends the worker's loop with an empty result and exit code 0, and the only trace is a transcript record and `terminal_reason: hook_stopped`. On `SubagentStop` and `SubagentStart` it does nothing. The lab's budget note rides on `PostToolBatch` and the 150% ceiling on `PostToolUse`, so the same server outage is a dead worker on one and a note that never comes on the other.
- **For "async is a background hook"**: `asyncRewake` ran in the foreground in `-p` (one session), against the docs.
- **For "failures of `http` hooks are visible in the transcript"**: yes, but the `continue` default leaves the model silent, the same as `mcp_tool` (`hook_non_blocking_error`); nobody's script reads it (w06-c6).
- **Data caveat**: my own first three attempts at the PreToolUse and PostToolUse tables (`runs/http_pre_run1_prefixbug`, `http_pre_run2_prefixbug`, `http_post_run1_prefixbug`) had a design error: my `if: Bash(echo H-DOWN*)` rule also matched `echo H-DOWNC`, so the "continue" controls fired the blocking hook too. The `X`-prefixed rows in `http_pre`, `http_post` and `http_ctl` are the corrected design. The corrected runs agree with the buggy runs on every blocking case (same message text). Three of the 15 sessions went to this.

## Not covered

- Interactive mode: what a human sees in the UI for a blocked or failed hook, how `asyncRewake` wakes an idle session, `Ctrl+O` verbose async notices. All runs are `claude -p`.
- Who starts a resident http server and who owns its lifetime and port (a SessionStart command hook could start a detached process; not built or tried), and the per-session token: headers take only environment variables listed in `allowedEnvVars`, and a plugin cannot set the environment of `claude` itself; not tested whether a SessionStart `CLAUDE_ENV_FILE` or a settings `env` block reaches the interpolation. A fixed port and a shared secret file are the alternatives; none tried.
- The real lab logic behind http (the server only logged and answered fixed JSON), two concurrent workers on one server, payloads over a few KB, `UserPromptSubmit`/`SessionStart` over http, resumed workers.
- `async` on SubagentStart, SubagentStop, PostToolBatch, UserPromptSubmit; async with `if`; whether an async hook that writes only a file races with a later hook that reads that file (the lab's `Agent` PreToolUse writes a brief file that SubagentStart reads: this ordering would break under async). Not run.
- `if` rules with brace alternation (e.g. `Write(**/*.{py,sh})`) to merge the lab's roughly 30 PreToolUse `if` rows: not tested (15-session limit reached). The docs say one rule per `if`; w06-c7 measured that identical commands are not merged and that a `$`-bearing Bash command starts every `if` row.
- Why the shell costs 40 to 80 ms (dyld, code-signing of `/bin/sh`, the platform's own wrapper): that is explorer-w07-a's question; I only show that dropping the shell halves the start under load.
- Whether the sibling launch interval of 40 and 14 ms depends on load (load average was about 9); one session per arm, 8 calls each.
- Which hooks of the lab could be `async`: by reading `scripts/budget.py`'s docstring, only log-only work qualifies; the 150% ceiling needs a sync `decision: block`, the start note and the `Agent` brief file need ordering. This is a reading, not a run.

## Steering questions

- [now] Exec form (`"command": "python3", "args": [...]`) for the ten registrations is a one-line-per-row change with a measured 2 to 3 times shorter start; should it be filed as a claim and measured on the lab's own scripts (the lab's guard and budget hooks, not my logging stub) before anything about `http` is built?
- [now] Should the resident-server line stay closed (user: "don't obsess")? The measurements say `http` has the same latency as `mcp_tool` and is louder on Pre and Post, but PostToolBatch failure kills the worker; a fail-open default with a transcript scan is the same weakness as w06-c6.

## Pointers

Commit 07cd64c holds everything below. Environment for every run: `W7C_PROJECT_ONLY=1` (`--setting-sources project`, so the user's own hooks and plugins did not run) except the `async` run, which used the default sources (user hooks were present: that is why its timings are slower).

- Helper code (`__instrumenta__/`): `w07c_run.py` (builds the plugin variant, starts the server by own pid, runs one `claude -p` session, stops the server by pid; `python3 __instrumenta__/w07c_run.py <variant>`, variants `async http_pre http_post http_ctl http_sub sub_stop_dead batch_dead batch_hang sib1 sib8 exec1 exec8`), `w07c_http_server.py`, `w07c_hook.py`, `w07c_records.py` (what the transcript recorded per call), `w07c_fields.py` (http against command payloads), `w07c_http_latency.py`, `w07c_siblings.py`, `w07c_async_timeline.py`, `w07c_shell_vs_exec.py`. Cite as `__instrumenta__/<file>@07cd64c`.
- Raw per-run folders: `runs/<variant>/` (hooks.json, prompt.txt, run.json, run.err, hooks.log, server.log, server.log.bodies.jsonl, truth.jsonl, transcript.jsonl, subagents/, dbg.log filtered to the lines that mention hooks).
- Derived tables (commands):
  - `siblings_table.md`: `python3 __instrumenta__/w07c_siblings.py runs/sib1 runs/sib8 runs/exec1 runs/exec8`
  - `http_latency_table.md`: `python3 __instrumenta__/w07c_http_latency.py runs/http_pre runs/http_post runs/http_sub`
  - `fields_table.txt`: `python3 __instrumenta__/w07c_fields.py runs/http_pre runs/http_post runs/http_sub`
  - `async_timeline.txt`: `python3 __instrumenta__/w07c_async_timeline.py runs/async`
  - `shell_vs_exec.md`: `python3 __instrumenta__/w07c_shell_vs_exec.py __instrumenta__/w07c_hook.py 40`
  - records per run: `python3 __instrumenta__/w07c_records.py runs/<variant>`
- Docs copy used for the CITED statements: `docs_hooks_2026-10-22.md` (fetched with `curl` from https://code.claude.com/docs/en/hooks.md on 2026-10-22; the WebFetch tool read only the first 100 000 of 269 866 characters, so the "Run hooks in the background" section was read from this copy).
- Prior work compared: `__pondus__/w06-c6.md` (mcp_tool m1 to m6), `__pondus__/w06-c7.md` (`if` rows), `__reports__/wave-06/explorer-w06-b/00-findings_v0.md` (S8 row on `async` with `mcp_tool`).
