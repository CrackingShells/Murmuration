---
type: findings
wave: wave-05
author: explorer-w05-f
date: 2026-10-21
version: v0
decision-required: confirm
---

# Auto-mode cost per Bash call and the first-call shell start: findings (v0)

I stayed inside the brief. The one addition: I also read the installed binary's strings (`strings` on `~/.local/share/claude/versions/2.1.304`, read only, no download) to name the cause, because the debug log shows only a silent gap.

## Result

- **Cause (CHECKED for the gap, CITED/inferred for the mechanism).** In auto mode the permission decision of a Bash call is a silent gap of about 0.45 to 0.75 s median between the PreToolUse hooks ending and tool dispatch. The debug log line `[Stall] tool_dispatch_start ... permissionDecisionMs=N` gives it directly: median 747 ms (p90 987, 35 calls) in the eight-command run and 448 ms (p90 632) in the lab-shaped run, against 2 ms in bypassPermissions (35 calls each). The binary contains a two-stage classifier with its own model, tokens, duration and `classifierCostUSD` fields in its telemetry events, and the docs say each check sends part of the transcript to a classifier model and counts toward token usage. So the gap is a classifier round trip, not a sandbox start. [source: `rows_main.jsonl`, `rows_lab.jsonl`, `timing_table.md`; docs CITED below; binary strings in `/private/tmp/murmuration-w05/explorer-w05-f/claude_strings.txt`] Not proven by packet capture; I saw no extra `api-request` record for it.
- **Nobody sees its cost.** Per run, auto against bypass: identical `api-request` count (10), cache-read tokens (412 956 vs 412 951 median), cache-creation (15 616 vs 15 614), `total_cost_usd` (USD 0.00776 both, mean of 5), and `modelUsage` lists only haiku. The classifier's tokens are in none of `usage`, `modelUsage`, the transcript's `cost-state` record, so lab_status and the harness's costs cannot see them. [source: `timing_table.md` run 1; transcripts of the 40 sessions] CHECKED, n = 5 per cell.
- **Lever that works: narrow allow rules.** With exact or prefix rules in `permissions.allow` the decision drops from about 700 ms to 1 to 3 ms: `Bash(ls *)`, `Bash(git log *)`, `Bash(git status*)`, `Bash(wc *)`, `Bash(sleep *)`, `Bash(grep *)`, `Bash(pwd)`, `Bash(date)`, `Bash(true)`, `Bash(echo *)`, and the exact string `Bash(python3 -c pass)` all gave 1 to 3 ms median per command (n = 5 each). [source: `rows_main.jsonl` cells `auto+exactallow`, `auto+globallow`; `rows_lab.jsonl` cells `auto+labrules`, `auto+flagrules`] CHECKED. Passed by `--settings` JSON or by `--allowedTools "Bash(...)"` flags, both work; nothing in `~/.claude/` was touched.
- **What does not work (and why my predecessor's null result was right).** `--allowedTools Bash` (blanket): 671 ms median, no gain (n = 35). `Bash(python3 *)` and `Bash(python3 -I ./hello.py *)`: no gain (463 to 540 ms; n = 5 per command). Compound `command -v python3; echo $SHELL` against a `command -v *` rule: no gain (about 475 ms). `cat /etc/hosts` against an exact rule: no gain (622 ms; a path outside the working directory). This matches the docs: on entering auto mode, blanket `Bash(*)` and wildcarded interpreters are dropped, narrow rules carry over. [source: same cells; docs CITED] CHECKED for the behaviour.
- **First Bash call (puzzle 3 settled).** The first Bash call of a headless session creates a shell snapshot: the debug log shows `Creating shell snapshot for zsh` then `Looking for shell config file: /Users/hacker/.zshrc`, and the snapshot script sources `~/.zshrc`. At idle (1 job) it took 4.9 to 7.4 s (median 5.7, n = 8, all succeeded) and the first call 4.9 to 7.5 s. With three runs in parallel, 17 of 35 zsh snapshots hit the 10 s execution timeout and failed ("Shell snapshot creation failed"), the first call then took 10.1 s. [source: `rows_serial.jsonl`, `rows_main.jsonl`, `rows_lab.jsonl`] CHECKED. Subsequent calls: 40 to 170 ms.
- **Documented way around it: `CLAUDE_CODE_SHELL=/bin/bash`** (an environment variable, set per run; the user has no `~/.bashrc` or `~/.bash_profile`, only a 284-byte `~/.profile`). Snapshot 0.15 to 0.45 s, first Bash call 0.18 to 0.61 s, all 14 of 14 serial and parallel runs succeeded, and no timeouts under three parallel jobs. Commands run in bash instead of zsh; `command -v python3; echo $SHELL` ran fine (38 to 69 ms) but I did not compare the PATH the two shells give, which matters for `python3` (miniforge) and `uv`. [source: `rows_serial.jsonl` cell `auto+bashshell`; `rows_lab.jsonl`] CHECKED for the speed; the PATH equivalence is CONJECTURE (untested).

## Table

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Auto-mode permission decision per Bash call | median 747 ms (p90 987), 35 calls; lab-shaped 448 (632); serial 609 (n = 28) | CHECKED | `timing_table.md` runs 1 to 3 |
| bypassPermissions, same | 2 ms (p90 3) | CHECKED | same |
| Auto, `disableAllHooks` | 1101 ms median (longer, not shorter, than with hooks at 747) | CHECKED, unexplained | run 1 |
| Auto, blanket `--allowedTools Bash` | 671 ms | CHECKED | run 1 |
| Auto, narrow exact or prefix allow rules | 2 ms for commands that match | CHECKED | runs 1, 2 |
| Auto, `Bash(python3 *)` or `Bash(python3 -I ./x.py *)` | 463 to 540 ms (dropped) | CHECKED | run 2 |
| Rule beside a path outside the working directory (`cat /etc/hosts`) | 622 ms despite an exact rule | CHECKED, n = 5 | run 1 |
| Tokens and USD, auto against bypass vs allow-rule cells | no difference: 412.9k cache-read, 15.6k cache-create, USD 0.0078 | CHECKED | run 1 |
| Cost of keeping the user's MCP servers | cache-read 517k, USD 0.0113 per run against 0.0078 (with `--strict-mcp-config`) | CHECKED | run 1 cell `auto+mcp` |
| First Bash call, zsh, idle | 5.7 s median snapshot (4.9 to 7.4, n = 8) | CHECKED | run 3 |
| First Bash call, zsh, 3 runs in parallel | 17 of 35 snapshots timed out at 10 s | CHECKED | runs 1, 2 |
| First Bash call, `CLAUDE_CODE_SHELL=/bin/bash` | 0.18 to 0.61 s, 14 of 14 ok | CHECKED | runs 1 to 3 |
| ESTIMATE: allow rules on the lab's usual commands | 0.45 to 0.75 s x 721 Bash calls = 5.4 to 9 min of worker time per wave, if every call matched a rule | ESTIMATE (formula: median ms x wave-4 call count; the share of calls that would match is unmeasured) | `__reports__/wave-05/explorer-w05-d/timing_table.md` F |
| ESTIMATE: bash shell for 137 headless runs of wave 4 | 5.7 s x 137 = 13 min serial, more with timeouts | ESTIMATE | same |

CITED (not verified against the vendor site; fetched through context7, library `/pjbrito/claude-code-docs`, a community mirror of the docs): `content/en/docs/claude-code/permission-modes.md` (decision order: allow/deny rules first, read-only and working-directory edits next, the rest to the classifier; "Classifier calls count toward your token usage"; blanket `Bash(*)`, wildcarded interpreters and `Agent` rules dropped on entering auto mode) and `.../env-vars.md` (`CLAUDE_CODE_SHELL`). Mark both UNVERIFIED against the official site.

## Worst-fitting case

The story "auto's cost is a classifier call that allow rules remove" fits worst here: `auto+nohooks` is slower (1101 ms) than `auto` with hooks (747 ms) over 35 calls each, although hooks should add time. An overlap (the classifier starting while PreToolUse hooks run, so the hooks' time hides inside it) would explain it, and my predecessor's 1.31 vs 0.93 s went the other way; I have no test of the overlap. Second: `permissionDecisionMs` is 0.45 s in run 2 and 0.75 s in run 1 for the same mode, and 0.61 s in run 3, so the "0.85 s" figure is not stable (API latency varies by hour and load). Typical case: bypass, 2 ms; exact-allow, 2 ms.

## Not covered

- Mechanism not proven: no capture of the classifier's request, no `classifierCostUSD` value seen (the telemetry events are not in the debug log); which model does the classifying is unknown.
- The share of the lab's real Bash commands that a safe rule list would match (wave 4's 721 calls were not replayed against rules); the safety side (which rules weaken auto mode's protection) is not assessed. Interpreter commands (`python3 scripts/...`) cannot be covered by a prefix rule in auto mode; only exact strings, which fit few lab commands.
- `autoMode.allow` natural-language rules (documented) were not tested for speed; they presumably still go to the classifier.
- No test with the Murmuration plugin loaded or with Sonnet; haiku, `--strict-mcp-config` except one cell.
- `CLAUDE_CODE_SHELL=bash`: PATH, conda, nvm differences not compared; behaviour after a failed snapshot (what environment the shell then has) not checked.
- Subagent first Bash calls in a live wave (explorer-w05-d saw about 1 s) not re-measured.
- Interactive Desktop sessions (the PI's own) were not measured; only `claude -p`.

## Steering questions

- [now] Add a vetted allow list (read-only: `ls`, `cat`, `git status/log/diff`, `wc`, `grep`, `sleep`, `date`, `pwd`, `echo`, plus exact lab-script command strings) to the project settings written by `/lab`? Evidence: 2 ms against about 0.5 to 0.75 s per matching call. Someone must judge the safety side.
- [now] Set `CLAUDE_CODE_SHELL=/bin/bash` in the env of headless probe runs (per-run env, not the user's rc files)? It saves about 5 s per run and removes 10 s snapshot timeouts under parallel starts, if the PATH you need is the same.
- [later] Tell the user that the classifier cost is invisible to `total_cost_usd`, `modelUsage` and the transcript, so lab_status's spend is a lower bound in auto mode.

## Pointers

Scratch (debug logs, which hold account identifiers, stay out of git): `/private/tmp/murmuration-w05/explorer-w05-f/{main,lab,serial}/dbg/*.log`, `dbg_auto1.log`, `dbg_bypass1.log`, `claude_strings.txt`.
- `timing_table.md`, `rows_main.jsonl`, `rows_lab.jsonl`, `rows_serial.jsonl` (session ids stripped), `table_serial.md` in this folder.
- Run 1: `python3 __instrumenta__/auto_mode_probe.py /private/tmp/murmuration-w05/explorer-w05-f/probe --reps 5 --jobs 3 --keep-debug .../main/dbg --out .../main/rows.jsonl` (haiku, 40 runs, about USD 0.40).
- Run 2: same with `--set lab --cells auto,auto+labrules,auto+pywild,auto+flagrules,auto+bashshell,bypass` (30 runs).
- Run 3: `--reps 4 --jobs 1 --cells auto,auto+bashshell,auto+exactallow` (12 runs).
- Tables: `python3 __instrumenta__/auto_mode_probe_table.py rows.jsonl`. Scripts: `__instrumenta__/auto_mode_probe.py`, `__instrumenta__/auto_mode_probe_table.py` (commit of this report).
- Single debug runs: `claude -p ... --permission-mode auto --debug-file dbg_auto1.log` (and bypassPermissions), 3 Bash calls each.
