---
type: findings
wave: wave-07
author: research-pi
date: 2026-10-22
version: v0
decision-required: confirm
---

# Wave 7: what the machine and the agent loop allow, and what was worth saving (v0)

Every number carries its claim's current label (`scripts/lab_status.py`) or the probe report it
comes from. Claims: `__pondus__/w07-c1.md` to `w07-c8.md`. Probe reports:
`__reports__/wave-07/explorer-w07-a/` to `-g/`. Decisions and their order:
`__statera__/wave-07.md`. Figure: `lab_cost_map.html` beside this file.

## Result

Five changes landed on the local `main` (3b0448b, not pushed): every hook row in exec form, the
permission guard as a Rust binary with a fallback to its Python source, your words recorded only
when a person typed them, the spend report pricing fast mode and web searches, and authors keeping
a 1-hour prompt cache. Two did not: the PI without the skills listing, and `lab_status.py` without
its `git` child. The wave cost at least USD 38.28 of the at least 47 left (35.80 this checkout at
list price, session open; 2.48 headless, exact).

The larger finding is where the time goes. On this machine a process costs about 15 ms whatever
the language, and the shell had tripled it for every hook. In the agent loop the plugin's hooks
are well under 1% of a worker's time; the model, the tools a worker runs, its waits, and auto
mode's classifier are the rest.

## What the wave taught about the hardware

| Fact (this M3 Pro, macOS 26.6, Falcon endpoint extension installed) | Value | Label | Source |
|:--|:--|:--|:--|
| One exec, spawn to the child's first instruction | 14–16 ms, any language | MEASURED | explorer-w07-a |
| `fork` without exec; dyld + libSystem | 0.48 ms; ≤ about 2 ms | MEASURED | explorer-w07-a |
| A binary the kernel kills before user code | still 13.6 ms | MEASURED | explorer-w07-a |
| Why an exec costs 14 ms | the kernel's exec security path; `opendirectoryd` burns about 11 ms of CPU per exec, none per fork | CONJECTURE | explorer-w07-a |
| C, assembly, every Rust build, against each other | within 1.2 ms | MEASURED | explorer-w07-a |
| `python3 -S -I -c pass` over a native no-op | +7.8 ms | MEASURED | explorer-w07-a |
| `/bin/sh` | a trampoline into bash: two execs | MEASURED | explorer-w07-a |
| A new binary's first exec | 150–480 ms, once | MEASURED | explorer-w07-a, w07-c6 |
| Parallel parse scaling, Python pool | 1.9, 2.8, 3.6, 4.8, 5.5, 6.0× at 2, 3, 4, 6, 8, 12 workers | MEASURED | explorer-w07-d |
| Rust parse of 274 MB | 87 ms on 1 thread, 16–17 ms on 10–12 (efficiency 0.42–0.53) | MEASURED | explorer-w07-d |
| An efficiency core | about 0.3–0.5 of a performance core | MEASURED | explorer-w07-d |
| Python pool start on macOS | `spawn` 63–172 ms, `fork` 2–10 ms | MEASURED | explorer-w07-d |

So "know your algorithms" came before "parallel-first" here. `lab_status.py`'s incremental cache
(0.39 s warm) beats a 12-way parallel re-parse or Rust (0.33 s cold, rare), and parallelism past the
six performance cores buys little. The serial loops that dominate the lab's wall time are its
headless `claude` cells, which are bound by the API, not the CPU.

## What the wave taught about Claude Code's agent loop

| Fact | Value | Label | Source |
|:--|:--|:--|:--|
| A worker's wall, waves 5–6 | model 30.8% (thinking 41% of it), tool phases 45.6%, idle waits 22.3%, client gaps 1.3% | MEASURED | explorer-w07-b |
| The plugin's hooks; the classifier | 0.13–0.5%; about 1.9% of worker wall | ESTIMATE | explorer-w07-b, -g |
| Auto mode's classifier on a trivial Bash call | 628 ms median wait; the call 55 ms in default mode, 709 ms in auto | MEASURED | explorer-w07-g |
| A PreToolUse hook beside the classifier | mostly hidden; PostToolUse is not | CHECKED | explorer-w07-g |
| A Read | never reaches the classifier | MEASURED | explorer-w07-g |
| Requests that batching independent calls could save | 0.8–1.6% | ESTIMATE | explorer-w07-b |
| Bash calls that already chain three or more statements | 75% | MEASURED | explorer-w07-b |
| Prompt-cache re-writes after gaps over 5 minutes | 15.8% of worker spend | ESTIMATE | explorer-w07-b |
| How every string-form hook starts | `/bin/sh -c`, whatever `CLAUDE_CODE_SHELL` says; the recorded duration ends 0–1 ms after the hook's `main()` | MEASURED | explorer-w07-a |
| A prompt's transcript record | written after the UserPromptSubmit hooks exit | MEASURED | w07-c2 |
| Two hook rows with one command string | run once | MEASURED | author-w07-2 |
| An `async` hook | does not block; its failure is silent; cancelled at the end of `-p` | MEASURED | explorer-w07-c, w07-c5 |
| An `http` hook with `onFailure: "block"` | 2 ms; loud on PreToolUse and PostToolUse; ends the session on PostToolBatch; silent on SubagentStop | MEASURED | explorer-w07-c |
| A subagent's cache lifetime | 5 minutes; `experimental: {cacheTtl: "1h"}` in an agent file is honoured | MEASURED | w07-c7 |
| The PI's request 0 | moves by about 2.4k tokens with which MCP servers connected at launch | MEASURED | w07-c1 |

The limit of optimising the loop from a plugin: the plugin can make its own hooks nearly free and
choose which tools its workers reach for, but the two largest per-call costs, the model's turn and
the classifier, are the platform's, and the classifier is part of your permission layer. Parallel
tool calls are already used where they can be: the model chains work inside one Bash call.

## What was decided, and why

| Change | Claim · label | Decision | Why |
|:--|:--|:--|:--|
| Hooks in exec form | w07-c3 · MEASURED | landed | Same 42 handlers and outputs, fails closed; guard 123 → 42 ms, budget 104.5 → 41 ms, 10 of 10 pairs. Session wall not shown shorter |
| The guard as a Rust binary, installed with fallback | w07-c6 · MEASURED; w07-c8 · below MEASURED: restate | landed by PI decision on the verifier's wording | 0 differences over 20,847 events; CPU 17.6 → 1.6 ms a start. Any doubt the manifest or the 12-payload self-test sees falls back to the Python guard, visibly. Residual gap named (Still open 32) |
| Your words by origin, async | w07-c5 · MEASURED (v0 w07-c2 failed live) | landed | 0 errors over 3,027 prompts; 10 of 10 live; drops exactly the three known wrong entries. Costs: a silent crash, a 0.4 s quit window |
| Fast mode and web searches priced | w07-c4 · MEASURED | landed (c473203) | A silent under-count; the cache file now carries its version |
| Authors keep a 1-hour cache | w07-c7 · escalated; PI decides | landed by its rule | Honoured, survives a gap and a resume; money undetermined (P(net ≤ 0) = 0.34, ESTIMATE) |
| The PI without the skills listing | w07-c1 · below MEASURED: restate | not landed | −10.6–11.0k tokens of request 0, but the listing goes only whole and built-in skills such as `dataviz` are lost |
| `lab_status.py` without `git` | w07-c4 · MEASURED | not landed, by PI decision | 0.04–0.05 s a call for a re-implementation of git that was silently wrong in its first version |

Three rules of mine needed correction during the wave: P1's noise did not include the MCP servers'
connection timing; P4's ceiling came from two unpaired medians and was three times too high; P5
v0's landing would have tied the guard to a file outside the repository with nothing tying that
file to its source. A verifier or the author caught each.

## Worst-fitting case

The Rust guard. It is the change the user asked for most directly, and it passed every registered
metric, yet its verifier showed that a binary can be right on every test the installer runs and
wrong elsewhere. A compiled guard is reviewable only through its build, and this machine cannot
make the build byte-reproducible (the LC_UUID follows the build path). The pre-commit file closes
the gap for commits made here, once installed; CI would close it for everyone.

## For you (guardrails and things only you can do)

- **The managed setting** is probably not the active tier: `~/.claude/remote-settings.json` wins
  first (CHECKED by reading the binary). `/status` in an interactive session says which source is
  active; test 2 in `__reports__/wave-07/explorer-w07-f/00-findings_v0.md` says whether bypass is
  refused. The guard stays until then.
- **The pre-commit hook** for the Rust guard: `ln -s ../../scripts/git-hooks/pre-commit .git/hooks/pre-commit`.
  The CI file `.github/workflows/guard-binaries.yml` is ready and not pushed.
- **Your own hooks** cost more per call than the lab's: colgrep-mcp's `colgrep_policy` (`uv run`,
  median 194 ms per Bash call) and `inject_plan_directive.py` (177–206 ms per prompt).
- **The first Desktop session on main** is the check of what no headless run covers (Still open 37).

## Not covered

The Desktop app, interactive mode, Linux, Windows, a real Intel Mac, `budget` and `handback` in
Rust, and any effect of the changes on a real wave's wall time.

## Steering questions

- [now] Run `/status` and test 2 for the managed setting?
- [now] Install the pre-commit hook, and push the CI file when you choose?
- [later] Next wave: `budget` and `handback` into the binary (Still open 36), or the cache and long
  outputs (38)?

## Pointers

Claims `__pondus__/w07-c1.md`–`w07-c8.md`; protocols `__reports__/wave-07/0*-protocol_*.md`; probe
reports `__reports__/wave-07/explorer-w07-*/00-findings_v0.md`; the smoke run
`__reports__/wave-07/reproducer-w07-7/00-smoke_v0.md`; spend `python3 scripts/lab_status.py --spend`
and `--project /private/tmp/murmuration-w07 --spend` at 02:41 JST.
