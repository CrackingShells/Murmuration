# Smoke test of commit 47d2cd2 (lean hook starts + permission guard + Permissions paragraph), end to end

Run by reproducer-w06-8, 2026-10-21, Claude Code 2.1.304, macOS, python3 3.12.12. Claim-free: this says what ran and what was seen.
Raw output (streams, debug logs, labs) stays in `/private/tmp/murmuration-w06/reproducer-w06-8/runs/<name>/` and is not committed (it holds account identifiers).

## What ran

Export: `git archive 47d2cd2 | tar -x` into `/private/tmp/murmuration-w06/reproducer-w06-8/export` (not edited; subagents on haiku through `CLAUDE_CODE_SUBAGENT_MODEL=haiku`, which the transcripts confirm). One throwaway lab per run: a git repo with one commit, `lab_init.py` run on it (settings.local.json, `__statera__` and the other folders), cwd of the session.
Every session: `claude -p ... --model haiku --plugin-dir <export> --include-hook-events --debug-file ...`, `CLAUDE_CODE_SHELL=/bin/bash`, no `--max-budget-usd`, `MURMURATION_GUARD_LOG` set (the guard appends one line per start), a stub `claude` first on PATH (prints its argv, appends a line to `stub.log`; the runner starts the real `claude` by absolute path, resolved before PATH is changed). Bypass mode was never used.
Helpers: `__instrumenta__/w06c14_combo_smoke_run.py` (one session), `__instrumenta__/w06c14_combo_smoke_check.py` (checks (a) to (d) of a run).

| run | mode | thread | what the model was told | wall s | cost USD |
|:--|:--|:--|:--|--:|--:|
| ordinary_auto | auto | `--agent murmuration:research-pi` | one `echo`, then dispatch `murmuration:explorer` with `Budget: USD 0.30`, `Time: min 3`: `git status --short`, `python3 -c`, `echo today-$(date +%Y)`, a heredoc to `smoke_note.md` (with `$(...)` and a backtick inside), `git log --oneline`; hand back | 51 | 0.080 |
| ordinary_default | default, `--allowedTools Bash Write Edit Read Agent SubagentHandback` | research-pi | same | 42 | 0.081 |
| bypass_default | default, same allow list | plain main thread | Bash `claude -p hi --permission-mode bypassPermissions`, then `echo after` | 14 | 0.007 |
| worker_bypass_default | default, same allow list | research-pi, then the explorer | the explorer is told to run the same bypass command, then `echo after`, and hand back | 25 | 0.045 |

Total about USD 0.21. (A first start of the runner put the stub first on PATH and so ran the stub as the session itself, by my own mistake; that run was deleted and `stub.log` emptied. The stub has never been run by a model call.)

## Results

(a) Budget start note and hand-back capture, as on main. PASS in the 3 runs with a worker.
- `harness.jsonl` of each lab holds a `start` event for `explorer-w99-1` with `B` 0.3 and `T` 3.0 (source `brief`) and an `end` event (frac 0.250 auto, 0.268 default, 0.133 worker_bypass).
- The worker's transcript holds a `hook_additional_context` attachment from SubagentStart with "Budget: your budget for this run is USD 0.30 and 3 minutes (from your brief)".
- `__statera__/handbacks/wave-99-explorer-w99-1.md` exists in all 3 labs with the worker's final message (ordinary_auto: event=PostToolUse; ordinary_default: event=SubagentStop; the default-mode worker said it had no `SubagentHandback` tool, so its final message was the hand-back).
- ordinary_auto also holds a `deny` event of the hand-back gate on the worker's first `SubagentHandback` (no findings report yet), after which the worker wrote `__reports__/wave-99/explorer-w99-1/00-findings_v0.md` and its hand-back went through. That is the gate working as designed, noted here because the log has a `deny` line in an otherwise ordinary run.

(b) The guard starts once per Bash call and denies none of the ordinary ones. PASS.

| run | Bash calls (main + worker) | guard lines in `guard.log` | guard finishes in the debug file (status 0 / other) | ordinary calls denied |
|:--|--:|--:|:--|--:|
| ordinary_auto | 9 | 9 | 9 / 0 | 0 |
| ordinary_default | 7 | 7 | 7 / 0 | 0 |
| bypass_default | 2 | 2 | 2 / 0 | 0 (the `echo after` ran) |
| worker_bypass_default | 3 | 3 | 3 / 0 | 0 |

The stream's `PreToolUse:Bash` starts are two per Bash call (18 for 9): the second is the colgrep-mcp plugin's own policy hook installed on this machine (9 of its finishes in the debug file of ordinary_auto), not the guard. No Write or Edit call in these runs matched an `if` rule, so no guard start came from those rows (the heredoc `.md` goes through Bash; the report was also written through Bash). Each guard start took 131 to 150 ms in the debug file (`python3 permission_guard.py`, no `-S -I`).
The worker's ordinary commands included `echo today-$(date +%Y)` and a heredoc with `$(not run)` in it: both were allowed and ran (outputs `today-2026`, file written).

(c) A bypass attempt is denied, the stub does not run. PASS.
- bypass_default (main thread): `claude -p hi --permission-mode bypassPermissions` got `PreToolUse:Bash hook error: permission_guard (G1): the command carries --permission-mode ...`; `guard.log` says `deny` group G1; the next call, `echo after`, ran.
- worker_bypass_default (the same call made by the explorer, a subagent): denied with the same G1 text, `guard.log` deny G1, `echo after` ran, the hand-back was captured.
- `stub.log` has 0 lines after all four runs.

(d) Hook error records from the plugin's own hooks. PASS (none seen).
- 0 `hook_non_blocking_error`, 0 `hook_cancelled` (and 0 `hook_blocking_error`) in the stream-json of the 4 runs, in their debug files and in the 11 session and subagent transcript files under `~/.claude/projects` (counted by string; the attachment types present in the transcripts are `hook_success` and `hook_additional_context`, no error types).
- 0 `hook_response` events with an outcome other than `success` or an exit code other than 0, including the two denials (a deny is exit 0 with a decision).
- Every guard finish in the debug files was status 0 (21 of 21).

## What was not covered

One haiku PI and one haiku worker per run, 4 runs, so one sample of each path; no Write or Edit guard row exercised end to end (a Write to a `.py`/settings file was not attempted); no `resume`/`compact` SessionStart; no concurrent workers; no Desktop session; auto mode did not get a bypass attempt (the auto classifier would confound the guard).
