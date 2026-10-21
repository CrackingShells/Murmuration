# Claude Code hook design: where a hook's time goes, and how to build one — Knowledge Transfer (v0)

Date: 2026-10-22
Source cycle: wave 7 of the Murmuration reflective run (`__statera__/wave-07.md`), on Claude Code
2.1.304, macOS 26.6 on an Apple M3 Pro with an endpoint-security extension installed. Every number
carries its label and its source; machine-specific numbers are marked as such. Meant to be copied
into other repositories as a best practice.

## Executive Summary

- **What changed:** the Murmuration plugin's 42 hook handlers now start in exec form (no shell),
  the per-call permission guard is a native binary with a fallback to its Python source, and one
  hook that only records runs `async`.
- **Primary outcome:** most of a hook's start time was never the script. It was the shell the
  platform puts in front of it. Removing the shell took the guard from 123 to 42 ms and the budget
  hook from 104.5 to 41 ms a start (pooled medians, 10 of 10 pairs; MEASURED, `__pondus__/w07-c3.md`).
- **The rule that follows:** decide, for each hook, whether the agent loop must wait for it, and
  start it with one exec and nothing else.

### Where the time of one hook start goes

```mermaid
flowchart LR
    CC[Claude Code] -->|string form: /bin/sh -c| SH[/bin/sh<br/>exec 1]
    SH -->|trampoline| BA[bash<br/>exec 2]
    BA --> PY[python3 / node / uv<br/>exec 3 + interpreter start]
    PY --> W[the hook's own work]
    CC -.->|exec form: command + args| PY2[python3 or a binary<br/>one exec]
    PY2 --> W2[the hook's own work]
```

| Part, this machine | Cost | Label | Source |
|:--|:--|:--|:--|
| One exec, spawn to the child's first instruction, any language | 14–16 ms | MEASURED (machine-specific) | `__reports__/wave-07/explorer-w07-a/00-findings_v0.md` |
| `/bin/sh` on macOS | two execs (a trampoline into bash) | MEASURED | same |
| String-form hook | always `/bin/sh -c`, whatever `CLAUDE_CODE_SHELL` or `"shell"` says | MEASURED | same, and `__pondus__/w07-c3.md` |
| `python3 -S -I` start over a native no-op | +7.8 ms; plain `python3` about +19 ms | MEASURED | explorer-w07-a |
| `uv run python …` as a hook (colgrep-mcp's policy hook) | median 194 ms per Bash call (p90 554) | MEASURED | `__reports__/wave-07/explorer-w07-g/00-findings_v0.md` |
| A native binary in exec form | 16.5 ms start to exit, CPU 1.6 ms | MEASURED | `__pondus__/w07-c6.md` |
| A new binary's first exec on a machine | 150–480 ms, once | MEASURED | explorer-w07-a, w07-c6 |
| The platform's recorded `durationMs` | ends 0–1 ms after the hook's `main()` starts: it is all spawn path | MEASURED | explorer-w07-a |

## Wins

- **Exec form** (`"command": "python3", "args": ["-S", "-I", "${CLAUDE_PLUGIN_ROOT}/scripts/x.py"]`)
  is a one-line change per row that keeps outputs identical (215 of 215 scripted starts) and still
  fails closed. Placeholders are substituted inside `args`; no quoting is needed (CITED, the hooks
  docs; `__reports__/wave-07/explorer-w07-c/docs_hooks_2026-10-22.md`).
- **`async: true` for a hook that only records.** `user_words.py` waits up to 3 s for a transcript
  record without holding the prompt; the platform runs it in the background (1–4 ms to start).
- **A native binary with a fallback.** The guard binary is installed per session only when its
  hash, its sources' hashes and a 12-payload self-test agree; otherwise the Python source decides
  and the session is told why. Doubt resolves to the reviewable reference, visibly.
- **Paired designs and sign tests.** Every timing rule that held this wave compared arms in
  interleaved pairs and gated on the sign, not on a size near the ceiling.

## Pain Points

- Six waves measured hooks in milliseconds without measuring the loop around them. Hooks are
  0.13–0.5% of a worker's wall time; the model is about 31%, tools about 46%, waits about 22%
  (`__reports__/wave-07/explorer-w07-b/00-findings_v0.md`).
- `sh :` was taken for "an empty hook" (33 ms), so the shell's cost looked like a platform floor.
- Behaviour the docs do not state had to be found by testing (table below).
- One merge broke a selftest that matched a hook's command string; each branch had been tested
  alone.

## Root Causes

- **Exec counts, not languages.** A string-form hook is three execs; every exec costs about 15 ms
  here. Comparing Rust with Python inside that chain measured the chain.
- **Not asking whether the loop must wait.** Every hook was synchronous by default, including ones
  whose output nobody waits for.
- **Untested platform behaviour.** The facts below are what the platform did, not what was written.

| Platform behaviour (2.1.304) | Consequence for a hook author | Label | Source |
|:--|:--|:--|:--|
| Hooks of one event start one after another, 40 ms apart in string form, 14 ms in exec form, then run concurrently | each added sibling delays the last one's start | MEASURED | explorer-w07-c |
| Two rows with the same command string run once | do not rely on two identical rows doing two things | MEASURED | author-w07-2 |
| In auto mode a PreToolUse hook runs beside the permission classifier (628 ms median on Bash) | its time is mostly hidden; PostToolUse's is not | CHECKED | explorer-w07-g |
| A prompt's transcript record is written after the UserPromptSubmit hooks exit | a synchronous UserPromptSubmit hook cannot read its own prompt's record | MEASURED | `__pondus__/w07-c2.md` |
| `async` hook: deny and `decision: block` have no effect; `additionalContext` reaches the model at the next tool boundary after it exits; a failure leaves only a debug-log line; one still running when `-p` ends is cancelled | async is for effects nobody must wait for | MEASURED | explorer-w07-c, `__pondus__/w07-c5.md` |
| `http` hook: 2 ms; with `onFailure: "block"` it fails loudly on PreToolUse and PostToolUse, ends the session on PostToolBatch, is silent on SubagentStop; default timeout 600 s | needs a server, a port, a token, and a timeout set | MEASURED, CITED | explorer-w07-c |
| `onFailure: "block"` needs 2.1.295; exec form needs 2.1.139 | state the minimum version; below it a guard may fail open | CITED | `~/.claude/cache/changelog.md` lines 620, 5678 |
| An agent file truncated to empty is dispatched as a generic agent, silently | check a generated agent file is not empty | MEASURED | reproducer-w07-6 |

## Next-cycle Changes: the practice

**1. Decide whether the loop must wait.**

| What the hook does | Run it | Why |
|:--|:--|:--|
| Denies or allows a tool call (PreToolUse), blocks a stop, injects context the very next step needs | synchronous, exec form, `onFailure: "block"` if it is a guard | the decision must exist before the loop moves |
| Injects context that may arrive one tool call later (a budget note, a reminder) | `async: true` is possible | it arrives at the next tool boundary; a failure is silent, so do not use it for a safety net |
| Records, logs, counts, mirrors, notifies, saves a copy | `async: true` | nothing waits on it; accept that a failure is silent and a `-p` teardown may cancel it |
| Must survive being killed and must not be silent when it fails | synchronous | async failures leave no transcript record |

**2. Start it with one exec.** Use exec form (`command` plus `args`) on every row. Prefer a direct
interpreter call with lean flags (`python3 -S -I`, lazy imports) or a native binary. Avoid
launchers that add their own process and resolution step on every call (`uv run`, `npx`, a shell
wrapper); resolve once, at install or session start.

**3. Count the calls, then optimise the hot rows.** A PreToolUse or PostToolUse row without a
narrow `matcher` or `if` runs on every tool call; a SessionStart row runs once. Spend effort on the
rows that run on every call, and on PostToolUse first in auto mode, since PreToolUse hides behind
the classifier.

**4. Compile only with a fallback.** A native hook binary saves the interpreter (here about 16 ms
CPU a start) but is not reviewable from a diff and is per platform. Install it from a manifest of
hashes, self-test it at install, and fall back to the source implementation, visibly, on any doubt.
Run an equality replay of the two implementations before every commit that touches either.

**5. Measure as the platform records it, in pairs.** Read `durationMs` from the debug log or the
transcript, alternate arms, and gate on the sign over many pairs. Measure a ceiling paired before
registering a size threshold.

- Instruction changes: put the table in point 1 and the exec-form rule in any plugin's hook
  checklist.
- Workflow changes: run every script's selftest on the merged tree, not only on each branch.
- Review process changes: a hook row change is reviewed against its failure mode (blocked, silent
  or loud), not only its output.

## Artifacts to Preserve

- Exec counts and spawn floor: `__reports__/wave-07/explorer-w07-a/00-findings_v0.md`.
- Hook kinds under failure (`async`, `http`, exec form, siblings):
  `__reports__/wave-07/explorer-w07-c/00-findings_v0.md`.
- The agent loop's time budget: `__reports__/wave-07/explorer-w07-b/00-findings_v0.md`,
  `__reports__/wave-07/explorer-w07-g/00-findings_v0.md`.
- Exec form, verified: `__pondus__/w07-c3.md`; async with an origin rule: `__pondus__/w07-c5.md`;
  the native guard and its installer: `__pondus__/w07-c6.md`, `__pondus__/w07-c8.md`.
- The plugin's `hooks/hooks.json`, `scripts/install_binary.py`, `scripts/check_guard_equal.py`,
  `scripts/git-hooks/pre-commit` at local main ea6015f or later.
- The figure: `__reports__/wave-07/research-pi/lab_cost_map.html`.

## Open Questions

- Whether the 14–16 ms per exec is this machine's endpoint-security extension or macOS in general
  (needs a machine without it).
- How `async` and exec form behave in the Desktop app and in interactive mode (all runs here were
  headless `-p`).
- Exec form on Windows: the docs require a real executable, so `python3` may need to be
  `python.exe` or `py`; untested.
- What a human sees of a hook's stderr when it exits 0.
