# Wave 5: pre-registered experiments

Written by research-pi on 2026-10-21 after the five probes returned and before any wave-5 run.
Committed before the runs it governs. A pilot run (task calibration only) is allowed in each
experiment. It is named `pilot-*` and is excluded from every decision. Any change to a metric or
rule after this commit becomes a new version of this file (`_v1`) with its reason, and the decision
then reports both.

## Why these four

The probes measured where wave 4's time and money went [sources: `__reports__/wave-05/explorer-w05-{a,b,c,d}/00-findings_v0.md`]:
- The wall clock went into experiment cells and into workers waiting on them. The PI was idle 75%
  of the time, and 80% of worker Bash time was 48 calls of 60 s or more (a, d).
- A wait longer than 5 minutes inside one tool call loses the prompt cache: all 7 mid-run cache
  lapses, about 17% of worker list price (c, ESTIMATE). A message sent to a worker inside such a
  wait sits unread for 1.5 to 2.5 minutes (a). The harness tells workers to use Monitor, which no
  worker has (c).
- The PI's cost is structural. About 85% of its 75k-token starting context is tool schemas, and
  `research-pi` is the only agent file without `tools:` (b, CONJECTURE that this is the lever).
- The plugin's own machine cost is 1788 hook starts per wave, about 156 s serial, plus
  `lab_status.py` at about 0.8 s per call (d).

Each experiment is ranked by what it is expected to save per wave, and none asks the user for
more process.

## Common to all runs

- Headless `claude -p`, outside the repository, in `/private/tmp/murmuration-w05/<agent name>/`.
  `--plugin-dir` points to an export of this branch at a named commit, never the installed plugin.
  `COLGREP_DATA_DIR` sits inside the run folder, and `CLAUDE_PROJECT_DIR` is unset.
- **No `--max-budget-usd`**: it shows the worker the session's spend and confounded wave 4's first
  20 cells (w04-c11).
- Launch cells **side by side**, with a pause of at least 2 s between launches ("Not logged in"
  hit 5 of 33 parallel launches in wave 4). Run **one pilot cell first** and read its raw
  transcript before the batch. Wave 4 lost 15 minutes on its critical path to a confound found
  after 20 cells (explorer-w05-a).
- The md5 of `~/.claude/plugins/installed_plugins.json` is checked before and after.
- Spend per run is the run's `total_cost_usd`. Raw run folders stay out of git (they carry account
  identifiers). Derived tables and timing records (start, end, per-request usage, no identifiers)
  are committed.
- Kill only process ids you started; never by name pattern.

## E5 (claim w05-c1): how a worker waits

Arms, same task, n = 3 each:
- **A**: the branch at its export commit.
- **B**: A plus one short paragraph in the four worker agent files, on how to wait. A single tool
  call never waits more than 4 minutes: poll in chunks, or use Monitor if the pilot shows a
  subagent can have it through `tools:`. Background jobs the worker started are stopped (by their
  pid) before it hands back. If Monitor works, it is added to `tools:`.

Task: an author-type worker whose context at the wait is **at least 100k tokens** (the brief has it
read a large reference first, as real authors carry 200–300k). It launches a provided job that runs
about 9 minutes and writes one number, then files that number with one small derived figure.

Metrics, per run:
- m1: cold mid-run requests, meaning requests with cache read below 50% of the context that follow
  a tool call or gap longer than 300 s;
- m2: longest single tool call, in seconds;
- m3: `total_cost_usd`;
- m4: wall time;
- m5: correct number filed;
- m6: processes started by the run still alive 30 s after it ends;
- m7: count of blocked or failed wait calls (`sleep` blocks, "No such tool").

Decision rule:
- **B is proposed** if all of these hold:
  - A shows the problem: m2 > 300 s in at least 2 of 3 runs;
  - B has m2 ≤ 300 s in 3 of 3, m1 = 0 in at least 2 of 3, and m5 correct in 3 of 3;
  - B has m6 = 0 in 3 of 3;
  - B's median m3 is not above A's median by more than 5%.
- If A does not show the problem, B is **not proposed**, reported as untested at this task.
- Any other outcome: not proposed; the table is reported.
- Reported, not decided: the cost formula extrapolated to wave-4 context sizes (ESTIMATE). Message
  latency during a wait is not tested headless; its mechanism (messages are read between tool
  rounds) is cited from wave 4's transcripts.

## E6 (claim w05-c3): a `tools:` list for the PI

Arms, paired, n = 3 each:
- **A**: `agents/research-pi.md` as it stands.
- **B**: A plus a `tools:` line. It covers every tool a PI needs on any project, including Agent,
  SendMessage, Skill, ToolSearch, AskUserQuestion, the web tools, the file and shell tools,
  TaskStop, Monitor and the MCP wildcards the worker files already name. App-provided tools are
  also covered where a wildcard can name them. The author states what is left out and why.

Run: headless with the plugin's PI as the main agent, on a smoke task that dispatches one tiny
explorer, loads the research-loop skill, reads, writes and edits a file, runs Bash, and finds a
deferred tool with ToolSearch.

Metrics: m1 the context size at request 0 (input + cache write + cache read); m2 the smoke task
completed with each step's tool call present; m3 any "No such tool" or refused call; m4
`total_cost_usd`.

Decision rule: **B is proposed** if B's m1 is at least 15,000 tokens below A's in 3 of 3 pairs,
and B passes m2 in 3 of 3 with no m3. Otherwise not proposed; the table is reported. What the
Desktop app injects regardless of `tools:` cannot be tested headless. It is reported as CONJECTURE,
with what a one-minute Desktop check would need.

## E7 (claim w05-c4): lean hooks, second build

The build starts from the set-aside lean hooks (revert of 4c46fe4) and adds the next steps open
item 9 names:
- the gate reads its input in blocks;
- the hand-written JSON goes;
- `PYTHONDONTWRITEBYTECODE` is respected;
- fewer process starts per tool call.

**The hard block at the ceiling must stay where the worker can still hand back.** A block sent
from PostToolBatch stops the worker dead (4 of 4 runs in wave 3), so it stays on PostToolUse or an
equivalent path.

Metrics:
- m1: hook outputs on the 291-transcript replay set of w04-c5, and the selftests;
- m2: **serial hook seconds per wave**, defined as wave 4's start counts per event and thread type
  (explorer-w05-d, `hook_starts_per_wave.py`) times the paired, interleaved per-start medians
  (at least 100 pairs per event), lean against main at 4c675ec;
- m3: per-start wall at payloads of 2 KB, 200 KB and 500 KB;
- m4: a worker at 150% still hands back (one headless run);
- m5: lines of code, reported only.

Decision rule: **proposed** if m1 is identical on 291 of 291 with all selftests passing, m2 is down
by at least 50%, m3 is not slower than main at any payload size, and m4 holds.

Why the metric differs from E4's: E4 asked for 50% on main-thread wall and 50% on long-worker wall
separately. The first build missed the second by 1.6 points, and a measured saving stayed off the
branch. What costs the lab is the sum over a wave, and m2 is that sum. The change is stated here,
before the build runs.

## E8 (claim w05-c5): `lab_status.py` time

Change: one `git worktree list` call instead of three. A per-file parse cache keyed on size and
mtime is allowed only if its writes are atomic and it has a selftest.

Metrics: m1 output byte-identical to main's on a frozen copy of the transcript tree; m2 wall
(interleaved, n ≥ 20); m3 the selftest; m4 lines added.

Decision rule: **proposed** if m1 is identical, m2 is down by at least 40%, and m3 passes. If only
the single git call is kept (no cache), it is proposed when m1 is identical and m2 is down at all.

## v1 addendum (2026-10-21, after w05-c3 was filed): E6b, a denylist for the PI

Reason: E6's arm B passed its rule. But an allowlist drops every MCP server the plugin cannot name,
such as user connectors and project servers (author-w05-2, mechanics probes). That breaks E6's own
aim of keeping every tool the PI needs on any project, and E6 had no metric for it. author-w05-2's
exploratory arm D (a `disallowedTools:` line) cut the base about as much. It was not pre-registered,
so it decides nothing. E6 and its decision stand as written; E6b is added.

Arms, paired, n = 3 each, same smoke task, same harness as E6, with the dummy MCP server attached
in both arms:
- **A**: `agents/research-pi.md` without `tools:` or `disallowedTools:`.
- **D**: A plus a `disallowedTools:` line naming only heavy app tools that no research PI needs.
  The author lists each one and why.

Metrics: m1 to m4 as in E6, plus m5, the dummy MCP tool present in D's tool list in 3 of 3 runs.

Decision rule: **D is proposed** if D's m1 is at least 15,000 tokens below A's in 3 of 3 pairs,
D passes m2 in 3 of 3 with no m3, and m5 holds. If both B (E6) and D are proposed, D supersedes B
on the branch tip, because it keeps tools that B silently drops. The user decides which lands.
