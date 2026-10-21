---
type: findings
wave: wave-06
author: explorer-w06-b
date: 2026-10-21
version: v0
decision-required: confirm
---

# Waste the plugin causes in a wave, and SA1 as the larger move: findings (v0)

Left the brief once, in part 2: I ran a headless platform probe (about USD 0.25 in 40 haiku runs, under `/private/tmp/murmuration-w06/explorer-w06-b/`) because the wave note named "the platform-visible cost of a do-nothing hook" as the first thing to measure and no number for it existed for a compiled binary or for `mcp_tool`. A file `__instrumenta__/w06_hook_lang_probe.py` by another writer (the PI, I assume) does a similar probe; I did not run or read its results, so the two are independent.

## Result

- **Language is not the lever; residency is.** Per hook event, the platform recorded (interleaved in one session, n = 16 to 31 per cell): `sh :` 38 ms, an sh gate that reads the payload 39 ms, a std-only Rust binary 58 to 70 ms, `python3 -S -I -c pass` 65 ms, `python3 -c pass` 75 ms, the shipped `budget.py` 104 ms, and an `mcp_tool` hook on a resident (Python!) MCP stub **2 ms** (n = 18; max 3). Rust beats the shipped script by about 35 to 45 ms per start and ties lean Python (`-S -I`). The only handler that is not a process start is `mcp_tool`; it is also the only one that moves by an order of magnitude. MEASURED [source: `__reports__/wave-06/explorer-w06-b/inter_partial_table.md`, `__instrumenta__/hook_platform_floor.py --interleaved`; the file is one session cut at 72 calls by my timeout, plus a 6-per-variant session in `rows3_try.jsonl` that agrees].
- **Bare process starts agree** (n = 60 per cell, `sh -c` by `posix_spawn`, load 4.6 to 5.7): `sh :` 33 ms wall / 3.5 ms CPU; Rust std binary 51 / 5.9; `python3 -S -I -c pass` 58 / 12; `budget.py` 90 / 42. A Rust binary starts **slower** than `sh :` (18 ms more) and only 7 ms faster than the bare lean-Python floor; against `budget.py` it saves 39 ms wall and 36 ms CPU per start. MEASURED [source: `bare_n60.jsonl`; `python3 -I __instrumenta__/cmd_cost_interleaved.py cases_bare.json --n 60`].
- **Wave 4, re-priced** (1788 starts, 193 of them main-thread, serial wall): current 160.9 s; sh gate on the main thread 150.1 s; plus one dispatcher for the hand-back/SubagentStop starts 145.4 s; every start a compiled binary 91.2 s (CPU 75 to 11 s); compiled plus sh gate 87.8 s; every per-call and lifecycle hook as `mcp_tool` about 3.6 s. ESTIMATE [formula: starts per registration of wave 4 x the per-start medians above; source: `option_sums.md`, `__instrumenta__/w06b_hook_option_sums.py`]. For scale: 160.9 s is 0.66% of wave 4's 20 053 s of worker span, and about 1% of one 88-minute chain at two starts per tool call (ESTIMATE [source: `explorer-w05-d` counts]). By the user's rule it is still reclaimable waste.
- **Neither lean build failed on its idea.** w04-c5 kept every output (291 replay runs equal, 197 distinct transcripts) and failed one pre-registered wall threshold: long-worker median down 48.4% against 50% (pooled 0.516, 420 pairs), a figure the platform's own spawn floor sets, which the rule's author had not measured. w05-c4 failed because it **changed behaviour** (check moved to PostToolUse: 11 of 197 transcripts get an extra message in true batches; failed calls are not covered), and on a payload size (500 KB) the platform was never seen to send. CITED [source: `__pondus__/w04-c5.md`, `__pondus__/w05-c4.md`, verdicts SUPPORTED]. Both builds shrank a Python start; neither asked whether a start is needed (resident server) or removable by registration.
- **A behaviour-identical-by-construction set exists, and is small** (item list in the Table, rows B1 to B4): the sh gate on the two per-call registrations (w04-c5 item 1, with `p=$(</dev/stdin)` for large payloads as in w05-c4), a `^murmuration:` matcher on SubagentStart/SubagentStop, one dispatcher process for the events that start two scripts. Together: 160.9 to 145.4 s (-10%) in wave 4. It cannot remove the 1580 worker starts (88%), which return nothing in at least 99.4% of cases and are the product (the check).
- **SA1 sized, not built.** A compiled binary replaces 2273 production lines of the six scripts (1909 code lines; 1481 more are selftests) and adds a CLI, a JSON layer and, if an MCP server is wanted, a server. ESTIMATE 3 000 to 4 500 Rust lines (1.3 to 2x; no port was written, so this is a rule of thumb, CONJECTURE). It removes the per-start CPU (75 to 11 s) and about 70 s of serial wall of 161, and nothing that `mcp_tool` residency does not remove better. What it costs is in the Table (rows S1 to S7). My reading, labelled CONJECTURE: the cheapest large move is not Rust but **one resident MCP server called by `mcp_tool` hooks**, which could be the existing Python (3 ms measured by the platform probe with a Python stub, 2 ms here); Rust would then only be a later choice for that server's speed, and the build/ship/legibility costs of binaries stay out.

## Table

Part 1: inventory, wave 4's counts (1788 starts; `starts_wave4_pi_session.json`). "Advantage" is what the hook buys when it fires; "reclaimable" is what can be removed without changing a message.

| # | Registration (event, matcher) | Starts per wave 4 | What it does when it has nothing to do | Advantage when it fires | Reclaimable without changing a message | Label |
|:--|:--|--:|:--|:--|:--|:--|
| 1 | PostToolUse, no matcher, `budget.py` | 843 (104 main, 739 worker) | main thread: reads stdin, resolves lab root, role_of, returns (about 90 ms wall, 42 ms CPU); worker: lock, state read, transcript scan from the start (old build), usually no output | the hard ceiling at 1.5 of budget (`decision: block`): rare (14 `stop`, 11 `halt` lines in 291 replay runs) | main thread 104 starts by an sh gate (B1); worker starts only by residency or a cheaper start | ESTIMATE counts; MEASURED per-start |
| 2 | PostToolBatch, no matcher (the event has none), `budget.py` | 803 (89 main, 714 worker) | same; prints in 0.6% (10 records in the PI session) | the budget notes at 50/75/87.5/93.75% and from 100%; the note that made workers hand back (w02-c8, w03 budget arms: cited, not re-read) | 89 main starts (B1) | same |
| 3 | SubagentStart, no matcher, `budget.py` | 23 | non-murmuration agent: returns; murmuration: state file + start note | the start note with the budget (a resumed worker gets none: platform) | a `^murmuration:` matcher (B2): 0 of 23 in wave 4 (all were murmuration); helps sessions that use other subagents | ESTIMATE |
| 4 | SubagentStop, `handback.py` then `budget.py`, one registration, two commands | 23 + 23 | handback: writes `missing`/`draft` section or returns; budget: one `end` line, closes the run clock | the hand-back file in non-auto mode, the active-minutes figure for a resumed worker | one process for both (B3): 23 starts; matcher (B2) | ESTIMATE |
| 5 | PreToolUse `Agent|Task`, `budget.py` | 15 | main thread dispatch: writes the pending file with the brief's figures; other tools never match | the dispatch record that gives a new worker its figures at SubagentStart | nothing (matcher is exact) | CHECKED by reading `hooks.json` |
| 6 | PreToolUse `SubagentHandback`, `handback.py` | 29 | non-explorer or report present: returns; else one deny | the report check (denied once, 133 `deny` lines in the replays) | merge with row 7 (B3) | ESTIMATE |
| 7 | PostToolUse `SubagentHandback`, `handback.py` (plus rows 1 and 2 also fire for that tool) | 29 (+ 29 of row 1, + the batch of row 2) | auto mode: writes the section; else returns | the hand-back file in auto mode (the only copy of the delivered text) | a dispatcher folds row 7 with row 1 (B3) | ESTIMATE |
| 8 | UserPromptSubmit, `user_words.py` | not counted by explorer-w05-d (0 in its table); it fires per user prompt and per queued task notification | skips platform-injected text, writes the user's words | `user_words.md`, the lab's only record of the user's words | not reclaimable by matcher (the event has none); a task notification is a prompt too: a gate on the payload's first characters would skip them | CONJECTURE for the count |
| 9 | SessionStart `resume|compact`, `resume_brief.py` (imports `lab_status.py`) | 0 in wave 4 as counted; once per resume or compaction | prints nothing outside a lab | the wave note and open puzzles after a compaction: no other path restores them | nothing: matcher already exact; it pays an import of `lab_status` (40 ms CPU) that `-S -I` and lazy imports halve (w04-c5 note) | CITED w04-c5 |
| 10 | `lab_status.py` (skill `/lab-status`, `--spend`, called by the PI) | about 38 calls per wave (explorer-w05-d, ESTIMATE) | none: always parses | the spend and claim states | the w05-c5 cache (835 to 261 ms warm) is already built; whether it is worth 147 lines is item 24 | CITED w05-c5 |
| 11 | the two process starts at a hand-back | per hand-back attempt: handback Pre, handback Post, budget Post, budget Batch (the hand-back call is itself a tool call), handback Stop, budget Stop = 6 starts, ~0.5 s serial | all but one are no-ops in the common case | each of the files and the end line has a reader | B3 merges 3 of the 6 into others; the two per-call starts (row 1, 2) need residency | ESTIMATE |
| 12 | not the plugin's, same fires: colgrep-mcp PreToolUse Bash (119 ms, 721 calls = 86 s), user's tool-routing policy at SubagentStart | 721 | `uv run` start per Bash call | the colgrep search policy | out of scope: the user's plugin (S-w05-explorer-w05-d-4) | CITED |

Part 1b: options, wave 4 (ESTIMATE, `option_sums.md`).

| Option | Serial wall s | CPU s | Same messages by construction? |
|:--|--:|--:|:--|
| current | 160.9 | 75.1 | yes |
| B1 sh gate on rows 1 and 2, main thread | 150.1 | 67.7 | yes if the gate never misses a worker (w04-c5 verdict: tested on 8 payload shapes, a key renamed is missed by old and new alike) |
| B1+B2+B3 | 145.4 | 65.5 | yes if the dispatcher calls the two `handle`s in the old order (both silent at SubagentStop; not built, not tested) |
| compiled binary for every start | 91.2 | 10.7 | only by a port tested with the 291-run replay; not by construction |
| compiled binary + B1 | 87.8 | 10.2 | same |
| resident server, `mcp_tool` hooks | 3.6 | ~0 plus the server's own CPU (not measured) | not by construction: a new transport, a new failure mode (server down: `mcp_tool` errors without blocking, so the ceiling and the deny vanish silently) |

Part 2: SA1.

| # | Item | Observed or estimated | Label | Source |
|:--|:--|:--|:--|:--|
| S1 | What it replaces | production lines: budget 539, handback 233, user_words 215, resume_brief 82, lab_status 825, lab_init 379 = 2273 (1909 not blank and not comment); selftests 325+79+223+111+491+252 = 1481 | MEASURED (line counts at 9e4c055) | `scripts/*.py`, rule: lines outside `def selftest`..`def main` |
| S2 | Size in Rust | 3 000 to 4 500 production lines; JSON via `serde_json` (1.0.154 is in the offline cargo cache; `cargo build --release --offline` of a 10-line stdin parser took 4.7 s and gave 319 KB with `opt-level = "z"`, LTO, strip); std-only needs a hand-written JSON reader (w04-c5 already needed 60 lines for a subset) | ESTIMATE / MEASURED for the spike | `spike_serde_main.rs`, `spike_Cargo.toml` |
| S3 | Per-start gain | 39 ms wall, 36 ms CPU against `budget.py`; 7 ms against `python3 -S -I`; negative against `sh :` | MEASURED | `bare_n60.jsonl` |
| S4 | Shipping | CITED: a marketplace plugin is cloned into the cache (`${CLAUDE_PLUGIN_ROOT}`, a new directory per version); Claude Code auto-installs Node dependencies for a plugin, nothing for Rust; `bin/` of a plugin is on the PATH of the Bash tool (v2.1.90 and later, not installed by claude.ai or Cowork); a hook command is a shell string, `"shell": "powershell"` exists per hook. So a binary must be **committed per platform** (or built on SessionStart, which needs cargo on every user's machine). Targets installed here: aarch64 and x86_64 apple-darwin, x86_64 linux-gnu; none for Windows or linux arm64, and no cross linker was tried. One std-only binary is 342 KB unstripped (`rustc -O`), 319 KB with serde_json at `opt-level z`: five targets about 1.5 MB of binaries per version in git | CITED (docs below) / MEASURED sizes | context7 `/websites/code_claude` pages `plugins/components`, `plugins/loading`, `hooks`; not fetched at primary source: UNVERIFIED beyond context7's quotation |
| S5 | Windows | hooks.json is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/x.py"` today: POSIX quoting; the probe report `__reports__/platform_probes/01-findings_v1.md` has no Windows row. Python is no more portable than a binary there (`python3` may be the Store stub). A binary per target needs a per-OS command line in `hooks.json` (no OS conditional in a matcher: not found in the docs I queried) | CONJECTURE | grep of the probe report |
| S6 | Legibility (framing item 3) | the hand-back files, wave notes, claim files stay markdown either way. What changes is the harness: a reviewer reads `budget.py` today (539 lines, one language, a docstring that states the contract); a committed binary cannot be reviewed from a git diff, and a Rust reviewer pool is smaller. A reproducible build plus a checksum file would be needed to keep "I can audit what runs on my machine"; none exists | CONJECTURE | framing item 3 |
| S7 | What it removes that a cheaper change does not | per-start CPU (75 to 11 s) and about 70 s of wall; `lab_status` parse time (830 ms parse of 228 MB: serde at about 1 GB/s would take 0.25 s, ESTIMATE; the cache already gives 261 ms warm). What `mcp_tool` residency removes that a binary does not: the whole 90 ms start of rows 1 and 2, the transcript re-read (state in memory), the byte-loop gate | CONJECTURE (Rust lab_status); MEASURED (2 ms mcp_tool) | rows above |
| S8 | `mcp_tool` limits already in the lab's own probes | `async: true` ignored (the turn waits); SessionStart and SessionEnd fail ("not connected"); a server outage removes a blocking hook (waits up to `MCP_TIMEOUT`, then errors without blocking); a plugin MCP server's tools are named `mcp__plugin_<plugin>_<server>__<tool>`, so they appear in every agent's tool list unless denied (SA15's allowlist note) | CITED | `__reports__/platform_probes/01-findings_v1.md` rows 5, 6, 7, 8, 26 and the hooks docs |

## Worst-fitting case

The story "language is not the lever, residency is" fits worst here: **the platform-visible figures for Rust are not stable against Python's.** In the interleaved run Rust ran 58 (gate), 64 (drain), 70 (noop) ms against `python3 -S -I` at 65: within noise of each other, and in the unpaired first run `rust-noop` came out at 88 ms and `sh :` at 46 ms (`platform_unpaired_table.md`; load 4 to 6, runs minutes apart), where bare it is 51 and 33. So I cannot say from the platform's record that a binary beats lean Python by even the 7 ms the bare run shows; and I cannot rule out that a better-built binary (no `std` runtime init, static `panic=abort`, code-signed once) would start nearer `sh :`. The row that fits the story best: `mcp_tool` at 2 ms (n = 18, max 3), against 38 for the cheapest process start.

Second misfit: the one cell in which a compiled language is the clear winner is the CPU column, 42 to 6 ms per start (75 to 11 s per wave); the wall column that the user's complaint turns on is where it is weakest. A reader who counts CPU (energy, a loaded laptop with 4.6 load average) would put the binary above what the wall figures give it.

Prior work: nothing fetched beyond context7's Claude Code documentation (`/websites/code_claude`, plugin and hooks pages, queried 2026-10-21); the text of those pages as returned by context7 is the only source for S4's CITED claims.

## Not covered

- No Rust port was written; the line count is a rule of thumb. A 100-line port of `handback.handle` would calibrate it, and a replay of the 291 runs would be the equivalence test.
- No `mcp_tool` hook for the real budget logic: the stub does nothing. Untested: that `${transcript_path}`, `${agent_id}`, `${permission_mode}` and `${tool_calls}` reach a server in one call for a worker; that a PostToolUse `mcp_tool` can answer `decision: block`; that the agents' tool lists stay unchanged (a bundled server adds tools); the server's behaviour when two workers hit it at once; UserPromptSubmit as `mcp_tool`.
- Cross-compiling (windows, linux arm64), a code-signing or Gatekeeper effect on a committed binary on macOS, and the Windows behaviour of the present plugin.
- Platform-visible per-start cost of a worker start on a 5 MB transcript (the stub runs outside a lab and exits early; budget.py's 104 ms is its no-op path).
- `user_words.py`'s count per wave: explorer-w05-d's table has 0 for it (its counter does not see prompts); no number for task notifications.
- The interleaved run was cut at 72 of 72 calls by my 280 s timeout after the debug log held most rows (n = 16 to 31 per cell); a longer rerun at lower load would tighten the Rust-versus-Python ordering.

## Steering questions

- [now] Land B1+B2+B3 (about -10% of hook wall, outputs identical by construction, one dispatcher script and two hooks.json edits) as a claim with a replay, or skip it since it leaves 88% of the starts?
- [now] Is the resident `mcp_tool` server worth one claim: a Python stdlib server with the budget check, tested for the ceiling block and the failure mode, 3.6 s against 161 s per wave?
- [later] A 100-line Rust port of `handback.handle` plus the 291-run replay, to put a measured number on S2 before anyone argues for SA1 on language grounds.

## Pointers

All under `__reports__/wave-06/explorer-w06-b/` unless noted; scratch in `/private/tmp/murmuration-w06/explorer-w06-b/` (debug logs there carry account identifiers: not committed).
- `inter_partial_table.md`, `rows4_partial.json`: platform-visible per-event cost, interleaved in one session. Command: `CLAUDE_CODE_SHELL=/bin/bash python3 -I __instrumenta__/hook_platform_floor.py runs4 $S/bin $S/plug --interleaved --reps 3 --calls 8 --variants sh-colon,python3-SI-pass,python3-pass,rust-noop,rust-drain,rust-gate,budget.py,sh-gate-lean,mcp_tool` (timed out in session 0 at 72 calls; the table is a parse of that session's log, rule in the script's attribution by the hook command text). `rows3_try.jsonl` is the 6-per-variant session of the same script.
- `platform_unpaired_table.md`, `rows2.jsonl`: one variant per run, 3 runs of 10 calls, same script without `--interleaved` (noisy, runs minutes apart).
- `bare_n60.jsonl`, `cases_bare.json`: `python3 -I __instrumenta__/cmd_cost_interleaved.py cases_bare.json --n 60 --out bare_n60.jsonl`.
- `option_sums.md`: `python3 -I __instrumenta__/w06b_hook_option_sums.py __reports__/wave-05/explorer-w05-d/starts_wave4_pi_session.json`.
- `noop.rs`, `drain.rs`, `gate.rs` (built with `rustc -O -C strip=symbols`), `noop_mcp.py`, `spike_serde_main.rs`, `spike_Cargo.toml` (`cargo build --release --offline`, 4.7 s, 319 KB).
- Scripts: `__instrumenta__/hook_platform_floor.py`, `__instrumenta__/w06b_hook_option_sums.py` (both `@` the commit of this report); reused `__instrumenta__/cmd_cost_interleaved.py`.
