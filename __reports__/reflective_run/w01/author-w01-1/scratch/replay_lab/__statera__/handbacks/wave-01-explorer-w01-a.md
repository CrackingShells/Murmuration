# Hand-backs of wave-01-explorer-w01-a

Final messages, verbatim, appended by the lab's hook. Read it; never edit it.

## hand-back 1 | 2026-10-19T11:29:03+09:00 | agent_id=af01bccf4de2a3706 type=murmuration:explorer event=PostToolUse bytes=15093 sha256=24b04bddd8e6

# explorer-w01-a report: per-run profile from transcripts, and what a ledger (SA3, SA6) would add

First line, as the rules ask: I stayed on the brief. Two additions:
- I also read the other two combinatorics sessions (`3ccc590f`, `2947f9dc`), because `lab_status.py` sums them into the same project.
- I used Claude Code's own `cost-state` record as ground truth.

**`report.md` was not written.** The harness refused the Write ("Subagents should return findings as text"), so this message is the report. The script, the CSVs and the puzzle file are on disk.

Snapshot: 2026-10-19 about 11:50 local. This run's transcripts were still being appended, so every `this_run` number is as of that moment.

## Files
Under `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/`:
- `__reports__/reflective_run/w01/explorer-w01-a/profile_runs.py` is the script.
- Same folder, written by the script:
  - `runs.csv`: 55 rows. These are 5 main threads plus 50 agent files, which are 41 distinct runs once 9 byte-identical copies are removed.
  - `tools_by_run.csv`
  - `by_role.csv`
  - `resume_segments.csv`
  - `parent_view.csv`
  - `crosschecks.csv`
  - `dup_messages.csv`
- Same folder, written by hand from those: `ledger_fields.csv` (28 rows).
- `__scrupuli__/wave-01-explorer-w01-a.md` holds six puzzles, `S-w01-explorer-w01-a-1` to `-6`.

**MEASURED command:** `cd __reports__/reflective_run/w01/explorer-w01-a && python3 -I profile_runs.py`. It takes about 1 s, uses the stdlib only, and is read-only on `~/.claude/projects`.

Method notes:
- A "turn" is a distinct assistant `message.id`. This matched `maxTurns` in the one case where a limit was hit.
- Each assistant message is counted once across all files. A message id present in two files belongs to the earliest.
- USD is an [assumption]. I share Claude Code's own per-session, per-model `costUSD` (from `cost-state`) over the runs of that model. The weight is input + 1.25 cache-write + 0.1 cache-read + 5 output. The total is Claude Code's number; the split among runs is mine.

## 1. The profile table (v5 `run` event, rebuilt)

Tokens are exact except subagent output (section 3). Source: `by_role.csv`.

| group | role | model | runs | turns mean / max | wall max s | tool calls | tool errors | USD (alloc.) | USD per turn |
|:--|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| genesis | PI (main) | opus-5-5 | 1 | 267 | 76,393 | 280 | 9 | 58.77 | 0.22 |
| genesis | workers (general-purpose) | sonnet-5-5 | 9 | 54.2 / 89 | 3,788 | 617 | 16 | 30.59 | 0.063 |
| genesis | counsel | fable-5-1 | 1 | 17 | 569 | 71 | 0 | 6.24 | 0.37 |
| design | PI (main, forked from genesis) | opus-5-5 | 1 | 170 | 79,275 | 192 | 5 | 36.32 | 0.21 |
| design | workers (general-purpose) | sonnet-5-5 | 12 | 30.4 / 103 | 2,187 | 486 | 20 | 20.05 | 0.055 |
| design | counsel / reviews | fable-5-1 | 3 | 9 / 11 | 444 | 69 | 2 | 8.98 | 0.33 |
| design | web-fetch (built in) + a review | opus-5-5 | 3 | 7.5 / 9 | 175 | 32 | 0 | 2.51 | n/a |
| design | claude-code-guide | haiku-5-5 | 1 | 3 | 81 | 9 | 0 | 0.22 | n/a |
| this run | `murmuration:research-pi` | opus-5-5 | 1 | 33 | 959 | 37 | 5 | none yet | n/a |
| this run | `murmuration:explorer` x6 | sonnet-5-5 | 6 | about 49 / 63 | about 650 | about 308 | 11 | none yet | n/a |

- **Session USD from `cost-state`** (the record is CITED; reading it is MEASURED): genesis 95.62, design 68.08, `3ccc590f` 0.46, `2947f9dc` 60.70.
- **This run has no `cost-state` yet.** The record is written once, at session end.
- **Per-run detail** is in `runs.csv`. It has name, description, model, effort, wall / active / idle / tool-wait seconds, thinking seconds, turns, four token classes, tools by name, errors, permission decisions, resumes, ended-by and hooks seen.
- **This run's explorers:**
  - Bash is 43 to 60 calls of each run's 46 to 63.
  - No explorer called an MCP tool.
  - Five of six used `Read` 1 to 8 times and `Write` 1 to 5 times.
- **Typical case:** the genesis Sonnet worker `a200b6a79` (Foundations theory).
  - Its input, cache and tool numbers equal Claude Code's.
  - Wall time is 2841 s against the notification's `duration_ms` of 2,840,799.
  - Tool uses are 51 against 51.
- **Worst-fitting case:** the same agent's output tokens and its USD.
  - Output is 19,188 recorded in all.
  - Its USD exists only inside the session total.

## 2. Which ledger fields can be recovered post hoc (full table: `ledger_fields.csv`)

| v5 field | From transcripts? |
|:--|:--|
| ts, run_id, agent_type, model, mode | Yes, exact. `agent_type` comes from `meta.json`, which is missing for the 9 copies among the 28 design-session agent files. |
| tokens in, cache_read, cache_write | Yes, exact, but only if deduplicated by message id across all files. They equal `cost-state` to the token in all 8 session x model cells that have transcript rows. |
| tokens out | Main thread: exact. Subagent: no (section 3). |
| wall_s | Yes (first to last record). It includes the idle time of resumed agents: `a04ebecba` has 3600 s wall and 2414 s active. |
| tool_calls, tool errors, permission decisions | Yes: count of `tool_use` blocks, `tool_result.is_error`, `permissionDecision`. API errors and retries leave no record. |
| turns, deliverable | Yes. The deliverable is the `SubagentHandback` input or the last text. |
| resumes `(agent_id, n)` | Partly, fragile (below). |
| exit / ended cleanly | Partly, fragile (below). |
| hit a turn limit | Partly: observed once, recorded only in the parent's notification (section 4). |
| wave, claim_id | No. Neither is in any record; only the brief text carries a name. |
| cpu_s, energy_wh_est | No. `tool_wait_s` is derivable; CPU and energy are in no record. |
| USD | Only per session x model, only for ended sessions. Per run it is an allocation. |
| haiku helper calls (WebFetch / WebSearch summaries) | No, `cost-state` only. |

- **Resumes** are inferred from wake-ups after a stop plus the `SubagentHandback` count minus one.
  - A wake-up is a user record with `origin` coordinator, peer or task-notification.
  - **Check on one run:** for `a04ebecba`, the parent's SendMessage results give 1 resume and 2 messages queued mid-run. The file shows 1 wake-up and 2 queued.
  - It depends on the `origin` field and on the `SubagentHandback` tool. Per probe #24 that tool exists only in auto mode.
- **Exit status:** `stop_reason` is null on 88 to 97 percent of subagent messages. The best signal is the last record. A killed, cut or in-flight run looks the same.
- **Haiku helper spend:**
  - Design: 930,594 input tokens, USD 0.22.
  - Genesis: 29,584 input tokens, USD 0.02.
  - None of it is in any transcript.

## 3. The output-token gap (MEASURED, the main finding)

**What the agent files record.** In every `agent-*.jsonl`, the usage stored for a message is the value from the start of the stream.
- Messages with `stop_reason` null:
  - genesis: 444 of 505
  - design: 813 of 907
  - this run: 203 of 210
- The median `output_tokens` of those messages is 7, and the maximum is 110.
- Messages with a stop reason have a median of about 480.
- A message with a 56,741-character thinking block records 5 (`agent-a200b6a79312b3850.jsonl`).
- Main-thread files are complete. For the genesis PI, the sum of `output_tokens_details.thinking_tokens` is 107,358, which equals `cost-state` `thinkingTokens`.

**Output tokens, transcripts / Claude Code** (`crosschecks.csv`):

| session, model | transcripts | `cost-state` | factor |
|:--|--:|--:|--:|
| genesis Sonnet | 282,217 | 1,075,475 | x3.8 |
| design Sonnet | 117,542 | 693,339 | x5.9 |
| genesis Fable | 18,111 | 36,807 | x2.0 |
| design Fable | 38,147 | 68,359 | x1.8 |

- Opus main threads equal exactly.
- Input, cache read and cache write equal in every cell.

**Consequence for v5 row 260.** A ledger fed from `agent_transcript_path` at SubagentStop would inherit the fault.
- **CONJECTURE:** the hook sees the same file. I did not probe it.
- The only per-run true usage is in a foreground `Agent` result, and it is absent for background runs. CITED: `__reports__/platform_probes/01-findings_v1.md` rows 18 and 86. I read the report file; I did not re-run the probe.

**The notification's `subagent_tokens` is a size, not spend.**
- For `a200b6a79` it is 181,649. That is the last message's input + cache read + cache write (181,529), within 0.07 percent.
- Three design-session runs agree within 0.1 to 0.7 percent.
- That run's billed work is 5.55 M cache-read and 0.33 M cache-write tokens.
- Foreground `Agent` results report a similar size, 3 to 11 percent more than the last context.

## 4. Tuning targets (`reflective_run.md`)

| Target | Finding | Label |
|:--|:--|:--|
| `maxTurns` per role | **It was hit once.** See below. | MEASURED (one hit) |
| `maxTurns`, other roles | The nearest analogues without a limit are genesis workers (13 to 89 turns, median 44, 10 runs) and design workers (3 to 103, median 10, 19 runs). Author, reproducer and proof-adversary have no limit and no data. | CONJECTURE |
| effort per role | There is nothing to learn from: `effort` and `perTurnEffort` are `high` on all 6,065 assistant messages of every transcript read, all models. No agent file sets `effort`. | MEASURED |
| cost per role | Per turn: Opus about 0.21 to 0.22 USD, Sonnet 0.055 to 0.063, Fable 0.33 to 0.37. Cost is dominated by cache reads and cache writes, not output. | MEASURED turns and tokens; split is [assumption] |
| resume cost | See below. | MEASURED |
| allowlists, `omitClaudeMd`, `autoCompactWindow`, `cacheTtl`, brief length, parked puzzles | Not answered by this table. `tools_by_run.csv` holds tools by role. | n/a |

**The `maxTurns` hit.**
- explorer-w01-c was stopped after its 60th assistant message, a Bash call. Its file ends on that call's result, with no marker.
- The parent's notification says `status: completed` and "stopped at its 60-turn limit (partial result; SendMessage to task-id to continue)", at 02:11:59Z.
- The PI resumed it ("write the report now").
- At snapshot the other explorers had used 61 (b, probably also stopped and resumed, not checked), 49, 49 (me), 46 and 46.
- Bash is 43 to 60 of each explorer's calls. A limit of 60 is at the edge for probes that extract with scripts.

**Resume cost.** Resuming rewrites the whole context to the cache once it has expired (`resume_segments.csv`).
- `a200b6a79` was woken after finishing by the completion notice of a background shell job. That one turn, with 62 output tokens, wrote 146,568 cache tokens.
- `a04ebecba`'s second segment wrote 968,045 cache tokens, against 263,124 for its whole first segment.
- So the per-resume context re-cache dwarfs the SubagentStart `additionalContext` that v5 worried about.

## 5. Where `lab_status.py`'s spend reading fails

I ran `lab_status.py --project <root>` and `spend()` on three roots. Results are in `crosschecks.csv`, rows `lab_status.spend`.

| Case | What happens |
|:--|:--|
| Worktree project folder | It works only if `CLAUDE_PROJECT_DIR` or cwd is the worktree path. From the main checkout it reports "no usage records" (S-w01-research-pi-3). From this worktree it reads the PI and 6 explorers, but gives no USD. |
| Work stored under another project | The Murmuration design and build session is under `-Users-hacker-Documents-explore-combinatorics-on-binary`. `/lab-status` in this repository never sees its USD 68. |
| Forked session and copied agent files | `82e8a947` was forked from `566fa912`: 98 messages in common, 49 of them also in `3ccc590f`. It holds 9 byte-identical copies of genesis agent files. `lab_status` on the combinatorics project returns x1.32 (cache write) to x1.44 (output) the deduplicated total (cache read 609,217,767 against 453,573,992). It lists the copies as agent type "subagent" because they have no `meta.json`. |
| Subagent output | Understated 1.8 to 5.9 times. |
| Resumed agents | One file counts as one "run", so the resume count and per-resume spend are invisible. |
| In-flight runs | Counted at the moment of reading, and a killed run cannot be told from a running one. |
| Main thread type | Genesis and design main files have no `agent-setting` record, so they show as "main thread". |
| USD | Not computed, although `cost-state` holds it. |
| Haiku helper spend | Invisible. |

## 6. What a hook would capture that the transcript lacks

Probe facts are CITED to `01-findings_v1.md`. My reading of them is CONJECTURE.
- **`SubagentStart`** fires on every resume (row 3). That gives an exact resume count and start time. A hook script can read the lab for wave and claim id.
- **`SubagentStop`** carries `effort`, `permission_mode`, `background_tasks`, `session_crons` and `last_assistant_message` (row 4). Permission mode is not in the transcript, though an `auto_mode` attachment is.
- **`PostToolUse(Agent)`** carries `usage` and `totalTokens` for foreground runs only (row 18).
- **A hook cannot give:**
  - true subagent output tokens, if it reads the same file
  - USD, because no hook event carries `cost-state`
  - haiku helper spend
  - API retry counts. `cost-state` has `totalAPIDuration` against `totalAPIDurationWithoutRetries`, 12,330,170 against 12,315,959 ms for genesis.
- **Already in the transcript, no hook needed:** everything marked yes in section 2, plus permission decisions and tool errors. `PostToolUseFailure` would duplicate those.
- **CONJECTURE:** tokens in and cache, wall, tools, turns, model and agent type are a pure function of the transcripts. Reading them on demand as v6 does, plus `cost-state` for USD and true output at session end, loses little. The loss is the per-run output figure.
- **Only a hook or the lab knows** the wave and claim tag, and the exact stop time of each resume.

## Not done
- I fetched no price list (no download).
- I did not probe a SubagentStop hook on a turn-limit stop.
- I did not check whether explorer-w01-b also hit the limit.
- Re-run `profile_runs.py` after this session ends: it fills `usd_alloc_assumed` for this run once `cost-state` exists.

## Three puzzles to look at next (full text in `__scrupuli__/wave-01-explorer-w01-a.md`)
1. **`S-w01-explorer-w01-a-1`:** subagent transcripts hold only start-of-stream output tokens. What source gives per-run output for a background subagent?
   - refs: `crosschecks.csv`; `runs.csv` columns `out` and `out_adj`.
2. **`S-w01-explorer-w01-a-2`:** forked sessions and copied agent files double-count spend, and the design session is stored under the wrong project for this repository.
   - refs: `dup_messages.csv`; `crosschecks.csv`.
3. **`S-w01-explorer-w01-a-4`:** the first `maxTurns` hit leaves a trace only in the parent's notification, and the resume re-caches the whole context (also `-3`).
   - refs: `runs.csv`; `resume_segments.csv`.

Also in the puzzle file:
- **`-5`:** USD per run does not fit one list-price ratio.
- **`-6`:** `name` appears only in this run's `meta.json`; unexplained `.prefix.json` files; haiku helper spend appears only in `cost-state`; `advisorModel` appears on every record but no advisor iterations exist.

