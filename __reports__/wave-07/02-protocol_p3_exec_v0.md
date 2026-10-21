# P3 v0: every hook row in exec form (registered before any run)

registered: 2026-10-22, by research-pi, before author-w07-3 starts. Claim: w07-c3.

## The change (B against A)

- A = `hooks/hooks.json` at the commit this protocol is committed in.
- B = the same rows, events, matchers, `if` rules, timeouts and `onFailure` values, with each
  `command` string such as `python3 -S -I "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py" budget`
  rewritten in exec form: `"command": "python3", "args": ["-S", "-I",
  "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py", "budget"]` (documented in
  https://code.claude.com/docs/en/hooks, CITED from `__reports__/wave-07/explorer-w07-c/docs_hooks_2026-10-22.md`).
  No script changes.

## Measured ceiling and noise, before the rule (open item 27)

- explorer-w07-c, one session per arm at load average about 9: the platform recorded 116 ms (shell
  form) against 36 ms (exec form) for one PostToolUse hook; a whole tool call with a Pre and a Post
  hook 314 ms against 174 ms; sibling launch interval 40 ms against 14 ms. Outside Claude Code,
  `sh -c` 152 ms, direct exec 54 ms. [source: `__reports__/wave-07/explorer-w07-c/shell_vs_exec.md`,
  `siblings_table.md`]
- So the ceiling is the shell's share of a start: 40–80 ms on a loaded machine, less on a quiet one
  (wave 6 recorded `sh :` at 33 ms all in). Per-pair noise of platform-recorded hook times was about
  20 ms (w06-c9).
- Three earlier rules failed by putting a millisecond threshold at or above the ceiling. This one
  does not gate on a size. It gates on the sign, which a true saving well above the noise passes
  and a zero saving fails with probability about 5% (8 of 10 or better under a fair coin). The size
  is reported, not gated.

## Metrics and rule

Headless haiku sessions, Claude Code 2.1.304, `CLAUDE_CODE_SHELL=/bin/bash`, exports of A and B
(agent files set to haiku, nothing else changed), auto or default permission mode, the attack tests
with a stub `claude` first on PATH, A and B alternated in pairs.

- **x1 (form only):** a script shows that A and B differ only in `command` turning into `command`
  plus `args`, with every argument equal after the shell's own word splitting of A's string, for
  every row (42 handlers at the time of writing).
- **x2 (same behaviour, live):** a PI session that dispatches one explorer produces the same hook
  effects in A and B: the worker's budget start note, a budget note at a set threshold, the
  hand-back capture file, the guard's deny of a Bash call that names `claude` with a bypass flag,
  the guard's deny of a Write to a settings path, the `user_words.md` entry. All equal, by record.
- **x3 (failure):** with the guard script made to crash, and with `python3` unresolvable for the
  hook, B blocks the Bash call exactly as A does (fail closed), and the budget rows fail as visibly
  as in A (the same record, the same message, or the same silence, stated).
- **x4 (time):** per pair, the median platform-recorded duration of the guard's PreToolUse hook
  and of the budget PostToolUse hook is lower in B than in A in at least 8 of 10 pairs, for each of
  the two hooks. Report the median per-pair saving, its spread and the load average.
- **x5 (who can run it):** the version that introduced `args` (CITED from the docs or changelog),
  and what a Claude Code without it would do with B's rows (CITED or CONJECTURE, stated). If an
  older version would run `python3` with the payload on stdin as a script, the claim says so.

**Landing:** x1–x4 pass and reproducer-w07-3 supports them; x5 is reported and, if it names a
minimum version, that version goes into the plugin's README in the same change.

**Not covered, said now:** the Desktop app (the first Desktop session after the merge is the
check), other machines, Windows.
