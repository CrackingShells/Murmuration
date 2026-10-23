# P1 v0: `budget` and `handback` as subcommands of the Rust binary, falling back to the Python scripts on any doubt (registered before the build)

registered: 2026-10-24, by author-w08-1, before any Rust for `budget` or `handback` was written.
Claim: w08-c1 (builds on w07-c6 and w07-c8, the guard and its installer).
Branch: `w08-c1-rustbudget`, from 59e8873.

## The change

`murmuration budget` and `murmuration handback` read the hook JSON on stdin and do what `scripts/budget.py` and
`scripts/handback.py` do (same stdout, same exit code 0, same lines in `__statera__/harness.jsonl`, same state files, same
hand-back files). The 14 budget/handback rows of `hooks/hooks.json` start `${CLAUDE_PLUGIN_DATA}/bin/murmuration` with args
`["budget"]` or `["handback"]` instead of `python3 -S -I run_hook.py <name>`. The installer installs the binary only when
the manifest hashes agree (the manifest now also covers `scripts/budget.py`, `scripts/handback.py`, `scripts/run_hook.py`) and
the self-test (now also budget and handback payloads) agrees with the Python scripts; on any doubt it installs the launcher, which
now dispatches on its first argument (`guard` to `permission_guard.py`, `budget` and `handback` to `run_hook.py`). Inside the
binary, an event whose shape the port does not model (a field of another type than the platform sends, a transcript number that
is not an integer, a timestamp of an unusual form) is handed to `python3 -S -I $CLAUDE_PLUGIN_ROOT/scripts/run_hook.py <name>` with
the same stdin, before any file is written: doubt resolves to the reference there too.

## Ceiling, measured paired before any threshold (open item 27)

Paired, interleaved, order flipped each round (`__instrumenta__/w07c6_pair_bench.c`, 100 pairs per payload, 5 warm-up rounds), the
Python exec-form start (`python3 -S -I scripts/run_hook.py budget`, bytecode cached, a real 640 KB worker transcript, state
present) against a Rust no-op start (`murmuration --version`, the committed binary), on this machine at load 8.1
[source: `__reports__/wave-08/author-w08-1/ceiling_table.md`, `ceiling.jsonl`]:

| payload | Python minus Rust no-op, wall ms, median [p10, p90] | pairs with Python slower | CPU ms median |
|:--|:--|--:|--:|
| PostToolBatch (scan the transcript) | 15.3 [10.7, 32.0] | 100 of 100 | 14.5 |
| PostToolUse | 16.3 [10.5, 33.7] | 98 of 100 | 15.5 |
| no lab (returns at once) | 13.3 [8.0, 25.0] | 99 of 100 | 12.2 |

So the most one start can save is about 13 to 16 ms wall and 12 to 15 ms CPU (about a third of the 48 ms Python start at this load),
and a Rust start that does the work cannot reach the no-op. A size threshold is not registered: a saving is judged by sign over
pairs, and its size is reported next to this ceiling. The 41 ms of w07-c3 was measured unloaded; the Rust no-op's own floor is the machine's
one-exec cost (16 ms unloaded, 30 ms at this load).

## Metrics and rule

All of e1 to e3 are exact outcomes (equal or not), counted as differences; e4 is a sign over pairs.

- **e1 (the same decisions and records, by replay).** A corpus of hook events, each run through both implementations in its own copy of one lab
  folder, in sequences that exercise the state (a start, then checks, then a stop). Sources: (a) records of `__statera__/harness.jsonl`
  (agent ids, names, types, modes) used as the identities of events; (b) real subagent transcripts of this machine's own sessions (at least 150
  of them, all projects, sized from 2 KB to the largest) as the transcript each event points to; (c) synthetic events that cover every note
  threshold (0.5, 0.75, 0.875, 0.9375, 1.0), the 150 percent block and the backstop `continue: false`, the hand-back batch with no note, resume
  and raises (user records, queued commands, peers, tool results), time-dominated checks, floor warnings, dispatch records (equal, ambiguous,
  expired), the explorer report gate, hand-back saving in default and auto mode, draft and missing sections, a lone surrogate, the dedup;
  (d) malformed input (empty, not JSON, not an object, a BOM, invalid UTF-8) and a fuzz of typed fields. Each event records stdout, exit code,
  the lines appended to `harness.jsonl`, and the folder's files afterwards (names and contents).
  Time: both implementations get the same clock, a feature-gated test build of the binary reads `MURMURATION_NOW` and a wrapper that sets
  `time.time` and `datetime.datetime.now` to the same value drives the Python script; then NO normalization is applied. A second pass uses the
  shipped binary (no feature) and the real clock; there the only normalization is the `t` field of log lines and the time in the header
  of a hand-back section, and the fields computed from the elapsed time are compared with 0.15 s tolerance (`active_s`, `minutes_at`, `t_frac`).
  Rule: 0 differences in each of stdout, exit code, appended log lines and files, over the modeled events; events handed to Python by the binary
  count as equal only through that hand-off and are counted and reported apart (the fraction of the corpus).
- **e2 (fallbacks and races).** (i) binary missing from the data folder; (ii) the manifest does not match: `budget.py` edited after the build, `handback.py` edited after
  the build, `run_hook.py` edited, a Rust source edited, a flipped byte in the binary, a manifest missing: in each the launcher is installed, the notice names the cause, and a
  budget and a handback event are then decided as the Python scripts decide (compared as in e1); (iii) a binary that answers wrongly on a self-test payload of budget
  or handback (a stub): launcher installed; (iv) the fallback inside the binary: an event of an unmodeled shape reaches Python and is answered as Python answers;
  `CLAUDE_PLUGIN_ROOT` unset: exit 0, no output, nothing written; (v) concurrent writers: 8 parallel processes of each implementation on the same lab, 40 PostToolUse and
  PostToolBatch events each, with one agent and with four agents: `harness.jsonl` holds every line whole (each parses), the counts of lines equal those of a serial run,
  one block per batch at the ceiling, no state file torn. Rule: all pass.
- **e3 (the cost, paired).** Outside the platform: 300 interleaved pairs per payload (PostToolBatch with a 640 KB transcript, PostToolBatch with the largest transcript of the corpus,
  PostToolUse, a SubagentStop, no lab), wall and child CPU, Python `python3 -S -I run_hook.py` against the shipped binary, load recorded. Rule on signs: the binary is lower in at least 95 percent of
  pairs, wall and CPU, for each payload. Sizes are reported against the ceiling above and not gated.
- **e4 (in the platform).** Alternating pairs of headless haiku sessions, default permission mode, one `murmuration:author` worker per session doing 6 Bash calls, the platform's recorded
  duration of the budget hooks (PostToolUse, PostToolBatch), median per session, Python rows against Rust rows, at least 12 pairs. Rule on sign: the Rust rows are lower in at least 10 of 12 pairs
  (the same fraction for more). In the same sessions: the worker's `harness.jsonl` has the same sequence of event kinds in both arms, and the worker quotes the start note in both.

**Landing.** e1 to e4 pass and reproducer-w08-1 supports them. Then the merge to main is followed by a headless smoke run from main's own tree (open gap 3 of w07-c8). A failing e4 with e1 to e3
passing is reported as a CPU saving only.

## What would be different if the claim were false

A message that the Python script would send and the binary does not (or the reverse), a log line with another key or another float spelling, a state file one byte apart (`base` written `0` where
Python writes `0.0`), a worker that is not blocked at 150 percent, a torn log under concurrency, a pair in which the Rust start is slower, or a stale script that the binary no longer follows. e1 to e4 are built to show each.

## Amendments, written after the runs (the text above is as registered; these say where the runs differ from it)

1. The hooks file has 8 rows for the two subcommands, not 14 (budget: SubagentStart, PreToolUse Agent|Task, PostToolUse, SubagentStop, PostToolBatch; hand-back: PreToolUse, PostToolUse, SubagentStop).
2. e1, real-clock pass: both implementations run each step back to back in two folders, and the fields that follow the clock are compared with 1.0 s (seconds fields), 0.05 min (`minutes_at`) and 1 s over T (`t_frac`), not 0.15 s: two processes cannot run at one instant. The exact pass has no tolerance. The "corpus from `harness.jsonl` records" was 5 start records; the events are built from the fields the scripts read, with the identities of those records not used beyond the shape.
3. e2 (v): under concurrent writers the number of log lines depends on the order in which parallel hooks run (a `note` before or after a `block`), in either implementation; the registered "counts equal a serial run" is replaced by: every line whole, one block per agent, no torn state, no stray temporary file.
4. e4: the live pairs time the main thread's budget rows (the worker path needs a plugin named `murmuration`, whose data folder is the running session's); 12 valid pairs of 13 run (one session failed at start, API error, excluded with its partner).
5. The rule of e3 was applied per payload and per run as registered; it is reported as it came out, and the replicate run is reported beside the first, not instead of it.
