# Wave 6, E2: lean hook starts with nothing else changed (pre-registered)

Written by research-pi on 2026-10-21, after E1 stage 2 (w06-c4) missed its rule and was reverted,
before any E2 run. Committed before those runs.

## Why

E1 v0 names E2 as the fallback: "the changes that are identical by construction". The hook waste is
real: `budget.py` costs 104 ms a start as the platform records it, against 65 ms for a bare
`python3 -S -I` and a floor of 38–60 ms (explorer-w06-b). There are 1788 starts in a wave like
wave 4. The resident server removed the starts but added a failure mode: it can die silently, and
it may stay dead across sessions (S-w06-author-w06-4-1). The safety net for that cost the margin.
E2 keeps every registration, every command and every output. It only makes each start do less
before it can answer. Both earlier lean builds failed on their rules, not on the idea:
- w04-c5: outputs identical 291 of 291, but a 50% wall threshold that the platform floor made
  nearly unreachable;
- w05-c4: it merged starts and so changed behaviour (11 of 197 transcripts).
E2 does neither.

## The build

On main's current `scripts/` (`lab_status.py` as w05-c5 left it):
- `budget.py` and `handback.py` start lean. They decide from the payload alone whether there is
  anything to do (main thread, an event with nothing to note), and only then import the rest.
- The interpreter flags (`-S`, `-I`) are used only if outputs stay identical.
- `hooks/hooks.json` keeps the same events, matchers and number of rows. Only the command string of
  a row may change.
- w04-c5 (4c46fe4^) may be reused. Its `lab_status.py` part is not (superseded by w05-c5).

## Metrics and rule

| Metric | Pass when |
|:--|:--|
| e1 outputs | the replay of the 197 distinct transcripts used by w04-c5, w05-c4 and w06-c4, in sequence and with parallel PostToolUse threads (`__instrumenta__/w06c4_replay.py` or its process-mode equivalent), gives EQUAL text, decision and exit code on 197 of 197, and one deliberate mutant of the build gives at least one DIFF |
| e2 time | in paired headless runs (n ≥ 3 pairs, haiku, 2 workers each), the median platform-recorded `durationMs` of a worker's `budget.py` PostToolUse start is at least 25 ms lower than main's in every pair; main-thread starts and the per-run sums are reported |
| e3 same shape | the same events, matchers and row count in `hooks.json`; no resident process; selftests pass |
| e4 code | production lines (selftests excluded) at most main's + 100; selftest lines reported |

**Rule.** Land on main if e1–e4 all pass. Otherwise do not land; report which metric failed.

Headless runs in default or auto permission mode only, under
`/private/tmp/murmuration-w06/<author name>/`, with `CLAUDE_CODE_SHELL=/bin/bash`, no
`--max-budget-usd`, and an export of the branch commit passed with `--plugin-dir`.
