---
type: findings
wave: wave-06
author: explorer-w06-a
date: 2026-10-21
version: v0
decision-required: confirm
---

# What a do-nothing hook costs as the platform records it, by language: findings (v0)

I stayed inside the brief. Two additions: I also stamped the script's own clock inside each hook (to find where the gap sits), and I read the platform's own debug log once (`--debug-file`).

## Result

- **The platform's `durationMs` is almost entirely the time before the script's first instruction runs.** In 167 stamped records (python and Rust hooks, a `nowms` stamp in the sh variant), `durationMs` minus the lag from the platform's clock start to the script's first instruction has a median of about 3 ms (python) and 0 ms (Rust); the script body itself takes 0.1 ms (python, Rust) or 20-60 ms (stamped sh, which forks two helper processes). The record is written 0-3 ms after the script ends in most cells. So the gap between 322-605 ms and a script's own 42-82 ms is spawn-side, not exit-side. MEASURED [source: `hook_lang_probe_table.md`, columns "start lag" and "record lag"; `__instrumenta__/w06_hook_lang_probe.py`]. The platform's debug log shows the same number ("finished with status 0 (182ms)") for a hook whose body began 178 ms after the recorded start, so it is not the transcript's measure that is off. MEASURED, one run [source: `/private/tmp/murmuration-w06/explorer-w06-a/out/dbg2.log`, lines "Hooks: UserPromptSubmit [... noop.py py1] finished with status 0 (182ms)"; not committed].
- **Alone, in a warm session, language moves the platform's number by about 25 ms, not by the 300 to 500 ms that is on the record.** One hook alone, no other plugin's hooks, PreToolUse calls 2-4 of a run: Rust 100 ms median, python 129, sh 112 (n = 12 each; p90 128 / 133 / 125). Outside the platform, the same three commands cost 52 / 82 / 70 ms (n = 40 each, same machine, same minute). So the platform adds a roughly constant 30-45 ms to every language, and the Rust-versus-python difference (about 30 ms in both measures) survives. MEASURED [source: `hook_lang_probe_table.md`, second table; `hook_bare_cost_n40.md`].
- **What makes 100 ms into 300-600 ms is not the language. Three things, each measured here:**
  1. *Side by side.* Eight hooks of one event started together finish at 152, 306, 319, 322, 367, 408, 444, 466 ms (Rust, medians of 4 runs); python 209 ... 456; sh 336 ... 638. The k-th finisher pays about 40 ms more than the (k-1)-th, whatever the language, and last minus first is 291 / 284 / 306 ms. At eight hooks a Rust binary and a python script finish within 10 ms of each other (466 against 456). MEASURED, n = 4 runs per language [source: `hook_x8_order_stats.md`]. This reproduces explorer-w05-d's finding that starts do not parallelise (N = 1 / 3 / 5 / 8: 79 / 140 / 192 / 259 ms for budget.py) with a no-op in three languages.
  2. *The first hook of a session.* UserPromptSubmit fires about 0.2 s after startup. With no siblings, Rust alone is 108 ms, python 124, sh 198 (n = 4 runs each); in a warm session (PreToolUse, calls 2-4) 98 / 126 / 112. Startup adds nothing for Rust and python in this probe and an unclear amount for sh (n = 4, p90 220). The effect is small next to item 3. MEASURED, small n.
  3. *The user's own configuration.* The same single hook on UserPromptSubmit in the user's normal configuration (plugins on, settings hooks on) against `--setting-sources project,local` (no user settings, no other plugin's hooks): Rust 204 against 108 ms, python 261 against 124, sh 290 against 198 (n = 4 runs each). The extra 100-140 ms is the sibling hooks of that event, which on this machine for UserPromptSubmit is `~/.claude/hooks/inject_plan_directive.py` (one python start, silent) [source: stream-json run, one `UserPromptSubmit` hook_started before my plugin loaded]. CONJECTURE that spawn serialisation explains it fully: one python start is about 82 ms bare; the extra is 96-137 ms.
- **`CLAUDE_CODE_SHELL` and `.zshrc` do not touch hook spawns.** A diagnostic hook run with `CLAUDE_CODE_SHELL=/bin/bash` and with it unset has the `claude` process itself as parent (`ps -o command= -p $PPID` gives `claude -p ...`), and the script's `$-` is `hB` (a non-interactive `/bin/sh`), with no zsh and no shell snapshot between. The timing cells agree: unset against `/bin/bash`, Rust alone 258 against 204 ms, python 264 against 261, sh 296 against 290 in the normal config; 106 / 160 / 174 against 108 / 124 / 198 isolated (n = 4 each): no consistent sign. MEASURED (parent chain, 2 runs) and MEASURED at n = 4 (timings) [source: `/private/tmp/murmuration-w06/explorer-w06-a/out/probe0.log`, `probe1.log`; cells `*-zsh` in `hook_lang_probe_table.md`]. The earlier 4.4 s first-Bash-call cost from `.zshrc` is the tool shell, a different spawn path.
- **Reading for the lab (ESTIMATE, applied to wave-4 counts).** Rewriting the hooks in Rust saves about 30 ms per start in the platform's measure (52 against 82 ms bare; 98 against 126 ms recorded) [source: tables above]. At wave 4's 1788 starts that is 54 s of serial machine time in an 88-minute wave (1788 x 30 ms), about 1 %. It does not shrink the 40 ms per extra sibling hook that is the larger term; fewer simultaneous hooks does. The 322-605 ms of the old record are reproduced by contention (item 1 and 3), not by the language. The same 1788 starts at the platform's cost of a Rust no-op (about 100 ms each) are 179 s; the number of starts, not their language, sets that.

## Table

All cells: haiku, `claude -p`, plugin passed with `--plugin-dir`, `CLAUDE_CODE_SHELL=/bin/bash` unless named `-zsh` (unset), load average 5-6 (12 cores; other Claude sessions were running), run order shuffled over cells, 4 runs per cell (UserPromptSubmit: 1 record per run per hook; PreToolUse: 4 Bash calls per run). `iso` = `--setting-sources project,local`. Medians of `durationMs`, ms.

| Cell | Rust | python3 | sh | n per language | Label |
|:--|--:|--:|--:|:--|:--|
| bare, outside the platform (`sh -c`, posix_spawn) | 52 | 82 | 70 | 40 | MEASURED |
| PreToolUse alone, iso, calls 2-4 | 100 | 129 | 112 | 12 | MEASURED |
| PreToolUse alone, normal config, calls 2-4 | 102 | 126 | 143 | 12-13 | MEASURED |
| PreToolUse, 3 hooks side by side, iso | 186 | 178 | 174 | 16 | MEASURED |
| PreToolUse, 3 hooks side by side, normal | 211 | 186 | 196 | 16 | MEASURED |
| UserPromptSubmit alone, iso | 108 | 124 | 198 | 4 | MEASURED, small n |
| UserPromptSubmit alone, normal config | 204 | 261 | 290 | 4 | MEASURED, small n |
| UserPromptSubmit 3 side by side, iso | 296 | 214 | 240 | 4 | MEASURED, small n |
| UserPromptSubmit 8 copies, iso, last finisher | 466 | 456 | 638 | 4 | MEASURED, small n |
| `CLAUDE_CODE_SHELL` unset, UserPromptSubmit alone, iso | 106 | 160 | 174 | 4 | MEASURED, small n |
| Start lag (platform clock start to first instruction), median | = `durationMs` within 3 ms | = within 3 ms | not stamped (stamped variant: 153-278 ms against 172-304 recorded) | see table | MEASURED |

Full rows: `hook_lang_probe_table.md` (all 28 cells), `hook_x8_order_stats.md`, `hook_bare_cost_n40.md`.

## Worst-fitting case

The story "language is a small term, contention is the large one" fits worst in two places.

- **Three hooks side by side, UserPromptSubmit, isolated: Rust 296 ms against python 214 ms** (n = 4 runs each; p10-p90 199-357 against 192-223). The compiled binary is slower than the interpreter there, the reverse of every other cell. At n = 4 and a loaded machine I cannot tell whether it is noise or an effect of which hook the platform starts first (in the stamped variant of the same cell python finished first in all 4 runs). The PreToolUse version of the same cell (n = 16) shows Rust 186 against python 178, within the spread. The typical case it contradicts: alone, Rust 98-108 against python 124-129.
- **sh is not a clean floor.** Alone in the iso UserPromptSubmit cell it is 198 ms, slower than python (124), though bare it is faster (70 against 82). n = 4, p10 121, so one or two slow runs drive the median; I did not repeat it.

Other limits: load was 5-6 (9-10 for part of the first, lost run), so absolute numbers are inflated against an idle machine; bare costs were taken at load 3-5. All headless runs: the Desktop app's session (Claude Code 2.1.299; this probe ran 2.1.304) may differ. Four runs per cell is a probe, not a table to quote to the millisecond.

Prior work: nothing fetched. The comparison figures 322-605 ms and the concurrency scaling are the lab's own record in `__reports__/wave-05/explorer-w05-d/00-findings_v0.md` (CITED as the lab's record).

## Not covered

- **Murmuration's own hooks were not run inside this probe.** I measured do-nothing scripts, not `budget.py` (which reads a transcript) or `handback.py`; the in-script work of those is on top of the start cost. Their bare cost is in explorer-w05-d.
- **What happens in the 100 ms before the first instruction.** It is the same for Rust, python and sh (alone: 98-129 ms against 52-82 bare), so it is the platform's spawn path plus the kernel's exec, but I did not separate the two. The debug log shows the platform's own `sh` process ("`$.process.run (cc-plugin-telemetry): sh ... exited 0 in 101ms`") running at the same moment as the hooks start, a possible contender for the spawn lock; not tested. A `dtruss`-level trace was not tried.
- **The cost of a binary's compile and the second-order costs of moving to Rust** (cargo build in a plugin install, a binary per platform, loss of the plain-text scripts a human reviews, Rust's maintenance): not measured; the user's guardrail on legibility is the PI's question.
- **A single binary for all hook events** (SA1's shape: one start, dispatch by argument) would remove the sibling term for Murmuration's hooks but not for other plugins' hooks on the same event. Not run; the number to expect from this data is one start (about 100 ms) instead of k side by side (about 100 + 40 (k-1) ms for the last).
- **SubagentStart, PostToolUse, PostToolBatch**: only UserPromptSubmit and PreToolUse were run (cheap to fire repeatedly; SubagentStart needs a spawned worker per sample). PostToolUse/PostToolBatch are the events with 1646 starts a wave; they should behave like PreToolUse calls 2-4.
- **The Desktop app, the PI's long session, MCP servers connecting at the same time** (the debug log shows five connectors completing during the first second): not tested.

## Steering questions

- [now] Land the "fewer simultaneous starts" change before any language change? The data say the per-start saving of Rust is about 30 ms and the cost per extra side-by-side hook about 40 ms; one dispatcher process per event (python or Rust) removes the second without a rewrite. This needs a claim with a paired run (one dispatcher against k hooks) on the shipped hooks.
- [now] Is a Rust rewrite of `budget.py` and `handback.py` worth pricing on its own terms (they parse JSON transcripts, so their body time, not the start, may dominate)? The in-script time of `budget.py` on a 5 MB transcript was 110 ms against 80 bare in explorer-w05-d; Rust on the same parse is not measured.
- [later] Tell the user that on this machine `sh -c true` costs 33 ms and a no-op Rust binary 52 ms bare (the exec floor is high, probably endpoint scanning; CONJECTURE), which is why a compiled hook cannot go below about 100 ms recorded.

## Pointers

Scratch (not committed; raw rows carry session ids): `/private/tmp/murmuration-w06/explorer-w06-a/` with `out/main_rows.jsonl` (platform records joined with the script clocks, 112 runs), `out/main_crashed.job.log` (46 runs lost to a sort bug, fixed; their printed durations agree with the rerun), `out/bare_n40*.jsonl`, `out/probe0.log`, `out/probe1.log`, `out/dbg2.log`, `plug/`, `cells/`.

Committed, in `__reports__/wave-06/explorer-w06-a/`:
- `hook_lang_probe_table.md`: `python3 __instrumenta__/w06_hook_lang_table.py /private/tmp/murmuration-w06/explorer-w06-a/out/main_rows.jsonl`.
- `hook_x8_order_stats.md`: inline python over `main_rows.jsonl` (k-th finisher of the 8-copy cells).
- `hook_bare_cost_n40.md`: `python3 __instrumenta__/cmd_cost_interleaved.py /private/tmp/murmuration-w06/explorer-w06-a/out/cases_bare.json --n 40 --seed 11`.
- `src/`: the do-nothing hooks (`noop.sh`, `noop_s.sh`, `noop.py`, `noop.rs`, `nowms.rs`, `probe_spawn.sh`); build: `rustc -O -o noop-rs noop.rs`, `rustc -O -o nowms nowms.rs` (std only, rustc 1.99.0).
- The run: `python3 __instrumenta__/w06_hook_lang_probe.py /private/tmp/murmuration-w06/explorer-w06-a --reps 4 --seed 7 --cells <28 cells> --out out/main_rows.jsonl` (112 runs, about 18 minutes; every run haiku, one prompt, about USD 0.005-0.01).
- Scripts: `__instrumenta__/w06_hook_lang_probe.py`, `__instrumenta__/w06_hook_lang_table.py` (at the commit of this report); reused `__instrumenta__/cmd_cost_interleaved.py`.
