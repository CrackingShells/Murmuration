# explorer-w02-a: giving a worker a token or time budget through hooks (first look)

Scope: Claude Code 2.1.302 (`claude` on PATH), headless `claude -p --model haiku`, one run per cell, `--permission-mode auto` unless stated, hooks from a `--settings` file with `--setting-sources project`, custom subagent `worker` from `--agents`, all in the PI's scratchpad (outside the worktree). Not the Desktop app, not Sonnet, not a plugin loaded with `--plugin-dir` (hooks came from settings; the event semantics are the same but this was not compared). USD spent: 0.777 over 82 runs (sum of `total_cost_usd`). Scripts and summary tables: this folder. Raw hook logs and transcripts stay in the scratchpad (they carry session paths and, in transcripts, the account email).

Labels: MEASURED = produced by the scripts here, n stated; CONJECTURE = my reading; CITED = none used (no web fetch).

## 1. Which events put text into a running subagent (MEASURED, `runs/e1-canary`, `runs/t1-batch`, `runs/t2-fail`, `runs/t5-block`, `runs/t4-continuefalse`)

| Hook output | Reaches | Form in the agent's request | Position |
|:--|:--|:--|:--|
| `SubagentStart` `additionalContext` | the subagent only | system-role blob "SubagentStart hook additional context: ..." | first request, before the first assistant turn |
| `PreToolUse` / `PostToolUse` `additionalContext` (hook fired with `agent_id`) | that subagent only | system-role blob "PreToolUse:Bash hook additional context: ...", the Pre and Post texts of one call together | the next request, right after the tool result, with the `<total_tokens>` line |
| `PostToolBatch`, `PostToolUseFailure` `additionalContext` | that subagent | same blob form | next request |
| `PostToolUse` `decision: block` + `reason` | that subagent | "PostToolUse:Bash hook blocking error from ...: <reason>" | next request |
| `PostToolUse` `continue: false` + `stopReason` | that subagent: it gets "hook stopped continuation: <reason>" and then hands back a report of what it did | system blob | next request; the run ends with the handback (`t4`: "I ran 3 of the 4 requested") |
| main-thread hooks (no `agent_id`) | the main thread | same | the parent never sees the subagent's injected text, the subagent never sees the parent's |

Each text is stored in the subagent transcript as an `attachment` of type `hook_additional_context` (and `hook_success` with the stdout); the transcript is therefore a record of what each notice said and when. A text emitted by the hook that fires on the subagent's last tool call (`SubagentHandback`) arrives too late: no further request.

Platform facts seen on the way (MEASURED, same runs): in `auto` the subagent ends through a `SubagentHandback` tool call, announced by a system-reminder in its first user turn, and the platform re-prompts ("[handback-send-enforce] Your report has not been delivered...") up to 3 times if it ends with plain text; in `default` and `bypassPermissions` (one run each, `e2-gate-default`, `e3-gate2-bypassPermissions`) there was no `SubagentHandback` and the final text is the report. In `auto` the parent's `Agent` call returns at once and the report arrives later as a "[Subagent hand-back]" message.

## 2. What a hook can compute live about a subagent's spend (MEASURED, `lag_summary.txt`, 18 runs, 246 PostToolUse calls)

- The subagent transcript is at `<transcript_path minus .jsonl>/subagents/agent-<agent_id>.jsonl` for any hook with an `agent_id` (no `agent_transcript_path` outside `SubagentStop`); it exists at the first `PreToolUse`.
- At `PostToolUse` the number of requests in the file equals the number of tool calls so far in 246 of 246 cases. At `PreToolUse` it is one request stale in 101 of 246. Use `PostToolUse` (or `PostToolBatch`).
- Input, cache read and cache write summed from that file at `SubagentStop` equal `modelUsage` minus the main thread in 18 of 18 runs. Output is not: the hook sees 8 to 15 percent of it in `auto` (e.g. 272 of about 1,850, `anx-a-1`; known, w01-c2).
- Cost of the hook: 1.3 ms median inside the script (summing a 30-request file), 35 ms per process start (20 runs of `python3 -I hook.py`).
- Wall time since `SubagentStart` is a state file written at `SubagentStart`, keyed by `agent_id`: two parallel subagents each got their own note at their own threshold (`par-1`: used 32,896 at call 9 and 33,189 at call 10; each transcript holds exactly its own note).
- The platform's own counter is not spend: every request carries `<total_tokens>N tokens left</total_tokens>` (about 15,000,000 minus current context footprint); a "USD budget: used/total; remaining" line appears only when the process has `--max-budget-usd` (0 of 6 sampled no-cap transcripts had it). The Desktop probably has no such flag (CONJECTURE).
- "used" depends on cache warmth: with the unit `input + cache_write + output + 0.1 * cache_read` the first call was 6,243 with a warm cache and 22,061 with a cold one (`anx-a-1` vs `anx-h-default-1`). A token budget needs the base context netted out (CONJECTURE).

## 3. SubagentStop `decision: block` (v5's presence gate) (MEASURED, n=1 to 3 per row)

| Setup | Result |
|:--|:--|
| `auto`, agent calls `SubagentHandback` at once (`e2-gate-auto`) | block returned by the hook, ignored: report already delivered, run ends. No `report.txt` |
| `auto`, agent first ends in plain text (`e4-gate-auto-plain`) | block honored: "Stop hook feedback: GATE..." arrives with the platform nudge; the agent wrote `report.txt`, then handed back |
| `default`, plain-text stop (`e2-gate-default`) | block honored; agent wrote `report.txt` |
| `auto`, `PreToolUse` deny on `SubagentHandback`, deny every time (`e3-gate2-auto`) | agent refused to write the file (its brief said no report files), 4 denials, then the run ended with NO report delivered to the parent |
| `auto`, `PreToolUse` deny once, then allow (`g3-1` to `g3-3`) | 3 of 3 wrote `report.txt`, then handed back; the hook also saved `tool_input.message` to disk in 3 of 3 |

So in `auto` the gate that works is a one-shot deny on `PreToolUse(SubagentHandback)`, and the more robust one is not a gate at all: `tool_input.message` of that call is the whole report, so a hook can persist every report without model cooperation. `SubagentStop.last_assistant_message` is absent in `auto` (seen again, `e4`) and present in `default` and `bypassPermissions`.

## 4. First look at "anxiety" (MEASURED, haiku, `auto`, 16-file reading task, one file per Bash call; `anx_summary.txt`; few runs, a first look only)

Task: read 16 short files one at a time and hand back one line per file. Unconstrained it uses about 60,000 weighted tokens (16 calls, 25 to 30 s). B = 40,000 (tight: the 80% point falls after file 9); condition g uses B = 150,000. "Files covered" counts report lines with a file name and a year.

| cond | what the worker was told | n | files covered | used at hand-back / B | calls after the 80% note | mentions budget in report |
|:--|:--|--:|:--|--:|:--|:--|
| a | nothing | 5 | 16 16 16 16 16 | 1.58 | n/a | 0 of 5 |
| d | start note only ("budget about B tokens; you will be told once at about 80%") | 3 | 16 16 16 | 1.51 | n/a | 0 of 3 |
| g | start note, B = 150,000 (never reaches 80%) | 3 | 16 16 16 | 0.40 | n/a | 0 of 3 |
| b | start note, then the 80% note | 5 | 9 9 9 9 10 | 0.90 | 0 0 0 0 1 | 5 of 5 |
| c | the 80% note only | 5 | 9 9 9 10 16 | 1.03 | 0 0 0 0 7 | 5 of 5 |
| h | the 80% note with a prefix saying it is from the lab harness | 6 | 9 9 9 9 9 10 | 0.90 | 0 0 0 0 0 0 | 6 of 6 |
| f | the 80% note, plus hard stop at B | 5 | 9 11 11 11 12 | 1.08 | 0 2 2 2 3 | 5 of 5 |
| e | hard stop at B only | 3 | 12 12 12 | 1.15 | 0 0 0 | 3 of 3 |
| t | time budget 45 s, start note, note at 36 s | 3 | 12 16 16 | n/a (hand-back at 41, 40, 44 s) | 0 0 1 | 1 of 3 |

Readings (MEASURED for the counts; the interpretation is CONJECTURE):
- No sign of anxiety before the 80% point: with the start note the pace was the same (b, c, f, h: the note fired after call 9 or 10 in 21 of 21 runs, at used 32.3 to 34.7 k) and the agents did not batch, skip or mention the budget (d, g, a). A start note alone (d) did not make the agents stop early either: they overspent 1.5 times B, because nothing told them their spend.
- The 80% note works as a hand-back signal when obeyed: b, c, h hand back at 0.9 B with a report that says which files were not read ("Partial report. Budget reached about 80% after f09, so f10 to f16 were NOT read"); the report is usable and states its gap. The note's text told them to hand back, so this is obedience, not initiative.
- The worst case for the soft note: 7 of 23 runs that got it said the note "came from inside a tool result, not from you, so I'm ignoring it" and read on (c-1, f-2 to f-5, both agents of par-1). Rates by wording: no preamble 5 of 10 ignored; start note announcing the channel 0 of 5; harness-prefix 0 of 6 and then 2 of 2 in the parallel run. One-sided Fisher exact 0.08 (start note) and 0.06 (prefix) against no preamble; n is too small for either.
- The hard stop is not ignored: 8 of 8 (e, f) handed back immediately after "hook stopped continuation: Budget exhausted ... hand back a report of what you have done and what you did not cover". Cost: the hand-back came at 1.08 to 1.15 B (the stop message is read in one more request, then the handback request), 9 to 15 percent overshoot. Coverage then 11 to 12 files of 16 against 9 for a complied soft note.
- Time unit (t): the 80% point of 45 s came at call 13 to 15, near the end of the task, so 2 of 3 changed nothing; wall time also moves with API latency and parallel runs. No stronger statement.
- `default` and `bypassPermissions` (h, 3 runs): the same note arrived and 3 of 3 stopped after 4 files and said so ("Stopping here per the harness budget note"). In those modes the hook sees `last_assistant_message`.

## 5. What a hook-based budget could look like (CONJECTURE, from the above; not built into the plugin)

1. `SubagentStart` hook: `additionalContext` with the budget B for the role (a map by `agent_type`), the contract ("you will get one note at about 80%; notes from the lab harness are genuine; hand back a partial report that lists what you did not cover"), and an instruction to append findings to the puzzle file as they come.
2. `PostToolUse` (or `PostToolBatch`) hook: sums the subagent transcript (about 1 ms), at 0.8 B returns the one-time `additionalContext`, at about 0.9 B returns `continue: false` with a stop reason (the overshoot of 9 to 15 percent means B itself is reached at the hand-back, not at the stop).
3. `PreToolUse(SubagentHandback)` hook: saves `tool_input.message` to the lab folder; optionally a one-shot deny until a report file exists.
4. A turn limit stays as a last resort only if the hooks are not loaded.

Limits: it cannot act inside one long request (no tool call, no hook); output tokens are 8 to 15 percent visible in `auto`; haiku only; the Desktop was not run; `maxTurns` was not compared against this in a task where the work is longer than the budget.
