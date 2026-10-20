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

## Addendum, 10:10 (before any run it governs)

**PI decision on E3's reading of "extended"** (asked by author-w04-3 before the verifier, puzzle 8 of
its file). The protocol did not define it. A copy of an existing script adapted into a new file is
reported as its own category ("adapted by copy"), not counted as extension: where the strict and the
loose reading give different verdicts, the synthesis states the strict one. This is decided before
the verifier reads the claim, and is the more conservative reading.

## E3b (open item 11, claim w04-c7): a folder where `ls` is not the cheaper search

E3 ran at 46 scripts, where `ls` (about 1,240 characters) is cheaper than one colgrep search
(about 3,670). The user asked for "enough scripts that `ls` is not the cheaper search".

Setup: as E3, with at least 300 scripts with descriptive names (so that `ls -1 __instrumenta__`
is at least 3 times one colgrep `search` result of `limit: 5`), the index built as `/lab` builds it.
Arm M only (author as the main agent, as E3's cheap arm), two tasks (one fit, one near fit).
- **P**: the agent files of 41c75ea unchanged. n = 6 (3 per task).
- **Q**: the search paragraph of `agents/author.md` reworded by author-w04-3 to describe the
  search as list-then-read (`ls`, first lines of the close ones, a new name not in the listing),
  with colgrep `search` for a folder too long to list. n = 6 (3 per task).

Metrics: E3's s1–s4, plus (s5) the search method (colgrep, `ls`, `head` over all files, other) and
(s6) an existing file overwritten or a new name that collides with one.

Decision rule:
- **Q is proposed** (a change to `agents/*.md`, claim w04-c7) if Q's reuse (run as is or edited in
  place, strict reading) is at least P's, Q has 0 overwrites, and Q's median search output
  characters (s3) is at most P's.
- Otherwise the paragraph stays as it is, and the table is reported.
- Either way, if P shows colgrep `search` in at most 1 of 6 runs at 300 scripts, the sentence
  "search that folder once with colgrep `search`" is reported as not followed at that size.

## Addendum, after w04-c2 and w04-c3 were filed (before any run it governs)

Reason: E1 did not reproduce with a brief that names the report (0 of 6 denies, capped and
uncapped); the exploratory wave-3-shaped brief did (capped XA 3 of 3). `--max-budget-usd` makes the
platform show the worker a session spend figure at every request (author-w04-2, 88 of 88
requests), so no run below passes it. E2's task (about 1.1 B, 100% accuracy everywhere) could not
separate the readings.

### E1b (claim w04-c8)
Brief in the wave-3 shape (the list in the hand-back; the report only from the explorer file),
150 files, `Budget: USD 0.30`, no `--max-budget-usd`. Arms, n = 3 each, exports of 41c75ea:
**A** unchanged; **B'** one line in `agents/explorer.md`: write the findings report, from the
template, before handing back, also when a budget note says to hand back.
Metrics m1–m5 of E1, plus the template's shape (its headings present).
Rule: **B' is proposed** if A has denies in at least 2 of 3, B' in at most 1 of 3, B''s report is
present in 3 of 3 and in the template's shape in at least 2 of 3, and B''s median final fraction is
not above A's. Otherwise not proposed; table reported.

### E2b (claim w04-c9)
A task whose full deliverable costs about 1.5 B, that does not reach `maxTurns` before 2 B (fewer,
larger items per call), and whose items can be wrong (each item needs a small derived value, checked
against ground truth). No `--max-budget-usd`. Arms, n = 3 each: **N** notes on (A); **C** every
output of budget.py off, `frac` logged. Metrics n1–n5 of E2, plus (n6) deliverable lost (no
hand-back, or no list).
Rule: E2's rule, plus: **"the notes are what stops the worker"** if C runs past 1.3 B in at least
2 of 3 runs while N hands back between 0.9 and 1.2 B in at least 2 of 3. Anxiety still needs N
below 0.9 with items per USD or accuracy more than 15% below C's, or a budget reason with at least
10% left in 2 of 3.

## Addendum, after the exchange on w04-c7 (before any run it governs)

### E3c (claim w04-c10): the target past the listing's cut
In E3b both targets sorted 3rd and 9th of 429, so every first `ls | head -N` showed them and finding
was not tested (author-w04-3's answer to reproducer-w04-7, Q1). Setup: the 429-script lab of E3b,
with the fit and near-fit scripts renamed (descriptive names, same first lines) so that both sort
after position 200 of `ls -1`. Arm P only (agent files of 41c75ea unchanged), n = 6 (3 per task),
claude version recorded.
Metrics: s1–s6 of E3b, plus (s7) the target found: the run opens, runs or copies the target script.
Rule (a reading, not a plugin change):
- **Finding works** if s7 holds in at least 4 of 6.
- **Finding fails at this size** if s7 holds in at most 2 of 6; a change to the search paragraph is
  then a separate claim with its own test.
- Otherwise inconclusive. colgrep `search` use is reported in either case.
