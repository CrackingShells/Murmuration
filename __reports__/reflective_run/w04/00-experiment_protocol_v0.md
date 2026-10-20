# Wave 4: pre-registered experiments

Written by research-pi on 2026-10-20 before any wave-4 run. Committed before the runs it governs.
A pilot run (calibration of task size only) is allowed in each experiment, is named `pilot-*`,
and is excluded from every decision below. Any change to a metric or rule after this commit is
written as a new version of this file (`_v1`) with its reason, and the decision then reports both.

Common to all runs:
- Headless `claude -p` outside the repository, in `/private/tmp/murmuration-w04/<agent name>/`,
  with `--plugin-dir` pointing to an export of this branch at a named commit (not the installed
  plugin), `COLGREP_DATA_DIR` inside the run folder, `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`,
  `CLAUDE_PROJECT_DIR` unset. The md5 of `~/.claude/plugins/installed_plugins.json` is checked
  before and after (value at the PI's start: `8d71e8c0f33b7e927133e7e44194de37`).
- Spend per run is the run's `total_cost_usd` (Claude Code's own figure). Worker fractions are
  `budget.py`'s `frac`/`t_frac` in the run's `__statera__/harness.jsonl` (an ESTIMATE of USD by
  its own docstring; stated as such).
- Raw run folders stay out of git (they carry account identifiers). Derived tables are committed.

## E1 (open item 8, claim w04-c2): write the report before handing back

Arms, same task, same budget, n = 3 each:
- **A** the branch as it stands (`agents/explorer.md` unchanged).
- **B** A plus one line in `agents/explorer.md` telling the explorer to write the findings report
  before it hands back, also when a budget note says to hand back.

Task: an explorer brief whose deliverable is the findings report at the convention path, sized so
that the work does not fit the budget (the wave-3 shape that produced the denies: e2, e3, e5, e6,
q1). Budget at or above the floor.

Metrics, per run: (m1) report-check denies (`deny` lines in `harness.jsonl`); (m2) the fraction
at the first hand-back attempt and at the final hand-back; (m3) the report file present at the
convention path and in the template's shape; (m4) the overshoot after the first hand-back attempt
(final fraction minus first-attempt fraction); (m5) the run's `total_cost_usd`.

Decision rule:
- **B is proposed** if B has denies in at most 1 of 3 runs, A has denies in at least 2 of 3, B's
  report is present in 3 of 3, and B's median final fraction is not above A's.
- If A has denies in at most 1 of 3 runs, the problem did not reproduce: B is **not proposed**,
  reported as untested at this task.
- Any other outcome: B is not proposed; the table is reported.

## E2 (open item 10, claim w04-c3): compliance or anxiety at the notes

Arms, same task, same budget, n = 3 each:
- **N** notes on: arm B of E1 if E1 proposes B, else arm A (the same runs are reused; no new runs).
- **C** the same plugin with every output of `budget.py` switched off (no start note, no graded
  notes, no ceiling block); the brief still carries the `Budget:` and `Time:` lines. Logging of
  `frac` stays on, so the fraction is still measured.

Task: as E1, but sized so that the full deliverable costs about 1.0 to 1.3 times the budget
(calibrated by one pilot). If E1's task is that size, E1's task is used for both.

Metrics, per run: (n1) fraction at the first hand-back; (n2) items completed of the task's items,
and items correct (checked against the generated ground truth); (n3) items per USD of
`total_cost_usd`; (n4) whether the hand-back text gives the budget as the reason to stop;
(n5) unused budget at the hand-back, max(0, 1 − n1).

Decision rule (the reading is stated, not a plugin change):
- **Compliance** if N's median n1 is at least 0.9, or N's early hand-backs follow a note and N's
  items per USD and accuracy are within 15% of C's.
- **Anxiety** if N's median n1 is below 0.9 and N's items per USD or accuracy is more than 15%
  below C's, or if N's hand-back gives the budget as the reason while at least 10% remains in at
  least 2 of 3 runs.
- Otherwise **inconclusive at n = 3**, reported with the table.
A plugin change follows only from "anxiety", and is then a separate claim.

## E3 (open item 11, claim w04-c4): search and reuse of `__instrumenta__/`

Setup: a lab whose `__instrumenta__/` already holds at least 40 scripts, each with the required
first line, on several topics, with a colgrep index built as `/lab` builds it. Among them, for
each task, one script that does the task exactly ("fit") or with a small change ("near fit").
Workers (explorer or author, the agent files of this branch unchanged) get briefs that do not
mention the folder; n = at least 4 worker runs over at least 2 tasks (one fit, one near fit).

Metrics, per run: (s1) a search of `__instrumenta__/` before the first script is written or run
(colgrep `search`, Glob or `ls`, and which); (s2) reuse: an existing script run or extended
(fit and near fit), against a new script that duplicates one; (s3) characters of tool output the
search cost, against the output of `ls -1 __instrumenta__` plus the first lines of all scripts;
(s4) `total_cost_usd`.

Decision rule:
- **The practice works** if s1 holds in at least 3 of 4 runs and s2 shows reuse or extension in at
  least 3 of 4.
- **It fails** if s2 shows a duplicate in at least 2 of 4 runs. A change to the agent files then
  becomes a separate claim with its own test.
- Otherwise inconclusive, reported with the table.

## E4 (open item 9, claim w04-c5): the hooks' own cost

Measure first: for every hook registration in `hooks/hooks.json`, the wall time per invocation
(median and p90 over at least 30 invocations on recorded payloads) for (a) a main-thread event,
(b) a worker event on a short transcript, (c) a worker event on a long transcript (at least 5 MB);
the number of invocations per tool call; and the invocations in a real session (counted from the
transcripts of wave 3).

Then make it lean. A lean version is proposed if all hold:
- the selftests of every changed script pass, and the notes, logs and hand-back copies are
  identical to the old version on replayed recorded payloads (same `additionalContext`, same
  `harness.jsonl` records apart from timestamps);
- main-thread invocations: median wall time down by at least 50%;
- worker invocations on the long transcript: median wall time down by at least 50%;
- no new dependency outside the Python standard library and POSIX sh.
Otherwise the measurements are reported and nothing is proposed.

## E0 (open item 1, claim w04-c1): the prompt hook's lab root

No experiment run here beyond what the PI measured in this Desktop session (wave-04 note). The
change is proposed if its selftest covers: Desktop worktree session (session cwd = worktree,
CLAUDE_PROJECT_DIR = main checkout, both with a lab) → the worktree; the Bash tool `cd`'d into
another checkout at prompt time → still the session's lab; headless start in a lab → that lab;
no lab anywhere → nothing written.
