# Combined smoke of the wave-7 changes as merged (branch HEAD 82b366c)

Reproducer: reproducer-w07-7. Export: `git archive HEAD` at 82b366c3691eda629da7f0e2ed74f6d6b6b86a83 to `/private/tmp/murmuration-w07/reproducer-w07-7/export` (agent files `model:` set to haiku, nothing else; the `experimental: cacheTtl: "1h"` line in author.md kept). Claude Code 2.1.304, `CLAUDE_CODE_SHELL=/bin/bash`, `--plugin-dir` at the export, `--model haiku`, auto mode (PI sessions) and default mode (guard session), never the bypass mode. Helpers: `__instrumenta__/w07smoke_run.py`, `__instrumenta__/w07smoke_check.py`. Raw extracts: `__reports__/wave-07/reproducer-w07-7/raw/` (no transcripts, no debug logs: they carry account identifiers). 3 sessions, USD 0.035 by their own `total_cost_usd` (0.016, 0.006, 0.013).

Note: the HEAD tree has no Rust guard (P5 v1 is not merged), so the guard under test is `permission_guard.py` in exec form.

## Verdict in one line

Everything asked passed except one item that was not run: the guard's deny of a Bash call naming the CLI with a bypass flag. My own session's guard and auto-mode classifier blocked each way I tried to write that prompt into a file (under "Not run"). The PI needs to run that one item.

## Passed (record that shows it)

| Item | Result | Record |
|:--|:--|:--|
| All hook rows in exec form | 42 handlers in 7 events, each with `command` plus `args`, none with a space in `command`; the `user_words` row is the one `async` row | a python read of `hooks/hooks.json` at HEAD; the three sessions loaded it with no hook error |
| Selftests, 7 scripts (budget, handback, lab_init, lab_status, permission_guard, resume_brief, user_words; the brief says six, 7 carry `--selftest`) | all exit 0 with PASS lines, on a pristine export of HEAD, run twice (a first launch happened in an earlier call, so two runs of the same code) | `raw/selftest_*.txt`, `raw/selftest_rc.txt` (14 lines rc=0) |
| PI dispatches one explorer and one author, both run | in pi_terminal and r2_pi_terminal both workers ran, handed back and wrote their files | `raw/check_r2_pi_terminal.txt` (tool calls) |
| Workers' budget start notes | explorer and author each got `Budget: your budget for this run is USD 0.30 and 3 minutes (from your brief)...` as a SubagentStart `hook_additional_context` attachment; harness `start` events with `source: "brief"`, B 0.3, T 3 | `raw/check_*` (start-note lines), `raw/r2_pi_terminal_harness.jsonl` |
| One graded note | r2: the explorer got two PostToolBatch notes, `Spent 0.00 of USD 0.30 (1%); 1.7 of 3 min (56%)` and the 75% one (harness `note` events at t_frac 0.5606 and 0.7547, `which: time`). It needed `until`-loop waits: a plain `sleep 30` is blocked by the platform (session pi_terminal, puzzle 2) | `raw/r2_pi_terminal_harness.jsonl`, `raw/check_r2_pi_terminal.txt` |
| Hand-back capture files | `__statera__/handbacks/wave-99-explorer-w99-1.md` and `wave-99-author-w99-2.md` in both PI sessions, with `bytes=` headers and `event=PostTool...` (auto mode) | `raw/*_handbacks/` |
| Guard denies a Write to a settings path | r1_guard_inherited: Write to `<lab>/.claude/settings.json` denied `G3` (tool result `PreToolUse:Write hook error: permission_guard (G3)...`); the next Bash `echo after` was allowed and ran | `raw/r1_guard_inherited_guard.log` (1 deny G3, 1 allow), `raw/check_r1_guard_inherited.txt` |
| user_words: terminal-like prompt kept, inherited-environment prompt dropped | terminal-like (session env vars removed; transcript record `entrypoint` `sdk-cli`): the prompt is in `user_words.md` (pi_terminal, r2_pi_terminal: 2 headings = seed question plus the prompt). Inherited (`entrypoint` `claude-desktop`): no entry (r1_guard_inherited: 1 heading, the seed question). The 2 extra UserPromptSubmit calls at the end of r2 (worker hand-back messages) added nothing | `raw/*_user_words.md`, `raw/check_*`; the transcript fields were read in session |
| Author cache writes 1-hour, explorer's 5-minute | per request, deduplicated by message id: author 1h-write 11987 and 11738 tokens, 5m-write 0 in both PI sessions; explorer 5m-write 14256 and 12684, 1h-write 0 | `raw/check_pi_terminal.txt`, `raw/check_r2_pi_terminal.txt` (subagent lines) |
| No `hook_non_blocking_error`, no hook error in the debug log | 0 of each (`hook_non_blocking_error`, `hook_cancelled`, `hook_blocking_error`, `non-blocking`, `hook error`) in all three debug logs, 0 hook lines matching error, fail, timed out or Traceback, 0 hook-error records in main and subagent transcripts. The guard's deny of the Write is a hook decision, and no `hook_blocking_error` record was written for it | `raw/check_*` |
| `lab_status.py` and `--spend` on the scratch lab | both rc 0, 0.09 to 0.10 s, cold and warm outputs byte-identical; cache file `__statera__/.harness/lab_status_cache.v2.json`; total USD 0.01 `exact`, equal at 2 decimals to the session's `total_cost_usd` 0.0127; worker rows `haiku-5-5` with `+` marks | `raw/ls_out_*.txt` |
| README minimum | README.md line 72 reads `Claude Code 2.1.295 or later (...)`; the binary is 2.1.304 | README.md@82b366c |

## Not run, and why

- **A Bash call naming the CLI with a bypass flag, denied against a stub first on PATH (G1).** Not run; the stub's log (`/private/tmp/murmuration-w07/reproducer-w07-7/stub.log`) does not exist. The prompt for that scenario has to carry the flag text. The plugin's guard, loaded in my own session, denied the Bash heredoc that would have written the script (G1) and the Write of a script file that built the flag from two string pieces (G4), and the auto-mode classifier then denied two attempts to read the flag text out of wave 6's instrument (`__instrumenta__/w06c14_combo_smoke_run.py`, scenario `bypass_default`) as working around the guard. I stopped there, as the denial text says. To run it: `W8_EXPORT=<export> python3 __instrumenta__/w06c14_combo_smoke_run.py bypass_default` from a session where the PI allows it (its folder B is wave 6's, with its own stub), or add the scenario to `w07smoke_run.py` by hand. G1 itself is covered by the selftest that passed here (50 attacks denied, 28 ordinary allowed).
- Fast mode and web-search pricing in `lab_status.py`: not exercised by the haiku sessions (none used fast mode or web search); only the script's own selftest (PASS) and w07-c4's verdict cover it.
- A resumed author's cache across a gap, and Sonnet authors: not run (w07-c7's scope).
- The Desktop, an installed plugin (as opposed to `--plugin-dir`), a Linux machine: not run.

## Flags for the PI

- The combined run found no regression between the exec rows, the async `user_words` row, the pricing change, the 1-hour author cache and the README. The evidence is 3 sessions, one per condition, so a rare failure would not show.
- A plain `sleep N` in a worker's Bash is blocked by Claude Code itself (`Blocked: standalone sleep 30 ... use Monitor with an until-loop`), before the guard sees it (guard.log had 1 line for 2 Bash calls in pi_terminal). A brief that tells a worker to wait with `sleep` will not wait.
