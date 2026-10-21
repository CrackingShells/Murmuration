# Wave 6: pre-registered experiments

Written by research-pi on 2026-10-21, after explorers w06-a, w06-b and w06-c returned, before any run
it governs. Committed before those runs. A pilot run (calibration only) is allowed, named `pilot-*`
and excluded from every decision. Any change to a metric or rule after this commit goes into a new
version of this file (`_v1`) with its reason; the decision is then taken under both versions and both
are reported.

## Why this experiment, and not a Rust rewrite

The user (17:06) asked why the lab never considered "completely changing the language of the
scripts in the hooks from python to Rust". The probes give the answer in numbers:

- Language moves little. A Rust no-op hook saves about 30 ms per start against python as the
  platform records it, about 54 s over wave 4's 1788 starts, roughly 1% of the wave (explorer-w06-a).
  Against a lean `python3 -S -I` start the saving is inside the noise (58–70 against 65 ms,
  explorer-w06-b). A Rust port replaces about 1900 code lines with an estimated 3000–4500 lines. It
  needs committed binaries per platform, because a plugin installed from git has no build step, and
  a committed binary cannot be reviewed from a diff (explorer-w06-b).
- What makes a hook cost 300–600 ms is the number of processes started together, about +40 ms per
  sibling, not the language (explorer-w06-a). What makes it cost anything is that it is a process.
- An `mcp_tool` hook calls a server that is already running. It is recorded at 2 ms (n = 18,
  explorer-w06-b) and at 3 ms (n = 148, platform probe rows 5–6), against 104 ms for the shipped
  `budget.py`.

So the larger move worth testing is that **a hook starts no process**. This is the "hook entry point"
half of SA1, served by a resident server, which may stay in Python. It is tested in two stages.
Stage 2 (the full port with replay equivalence) is run only if stage 1 passes.

## E1, stage 1: can a resident server carry Murmuration's hooks at all?

Arms: none. This is a feasibility test with pass/fail metrics, on a throwaway test plugin outside the
repository. Headless `claude -p` runs, haiku parent, one subagent worker per run, under
`/private/tmp/murmuration-w06/<author name>/`, with `CLAUDE_CODE_SHELL=/bin/bash`, no
`--max-budget-usd`, and the test plugin passed with `--plugin-dir`.

The server is a stdio MCP server in Python standard library only, bundled with the test plugin
through its `.mcp.json`. It exposes one tool that records the fields it receives and answers as the
event requires. It is registered as `type: mcp_tool` on each event where Murmuration registers
`budget.py` or `handback.py` today: SubagentStart; PreToolUse with matcher `Agent|Task`; PostToolUse;
PostToolBatch; SubagentStop; PreToolUse and PostToolUse with matcher `SubagentHandback`. The worker
is a plugin agent whose `tools:` allowlist does not name the server. The main thread runs an agent
whose `disallowedTools:` names the server.

| Metric | Pass when |
|:--|:--|
| m1 fields | Every payload field that `scripts/budget.py` and `scripts/handback.py` read at main (the author lists them from the code first and commits the list before any run) reaches the server on every event that needs it, by substitution or by a stated derivation (for example a transcript path from the session id and cwd) |
| m2 firing | The hook fires on every instance of each registered event, in the worker (allowlist without the server) and in the main thread (server denied); counted against the transcript's own record of those events |
| m3 context | The server adds 0 tokens to the worker's request 0 and 0 to the main thread's request 0 when denied, against the same runs without the server (n ≥ 2 pairs) |
| m4 outage | When the server process is stopped by its own pid mid-session, the next hook's failure shows in a record the lab reads (a transcript hook-error record, or text the model sees), and the turn waits no more than 10 s. A silent drop fails |
| m5 latency | The median `durationMs` of the `mcp_tool` hooks is at most 10 ms (n ≥ 20 per event class) |
| m6 effects | Three effects Murmuration relies on work through the server: injected context from SubagentStart reaches the worker; a PreToolUse answer denies an `Agent` call; a PostToolUse `decision: block` reaches the worker (the 150% block) |

**Rule.** Stage 2 runs only if m1, m2, m3, m5 and m6 pass and m4 shows a visible failure within 10 s.
Otherwise the resident server stays out, with the failing metric named as the reason, and the lab
turns to the changes that are identical by construction (explorer-w06-b, section "identical by
construction") as E2, pre-registered in `_v1` before it runs.

Cost cap for stage 1: USD 6 of the author's runs and work. The author may stop early on any failed
metric that the remaining runs cannot rescue, and says so.

## E1, stage 2 (only if stage 1 passes): the port

Written here so it cannot be fitted to stage 1's results. The `budget.py` and `handback.py` logic is
served by the resident server, and the hooks become `mcp_tool` rows. `user_words.py` and
`resume_brief.py` stay `command`, since SessionStart(startup/resume) cannot use `mcp_tool` (probe
row 8).

| Metric | Pass when |
|:--|:--|
| s1 identical outputs | Replaying the recorded payloads of waves 1–5 (the 197 distinct transcripts of w04-c5's and w05-c4's replays, with true parallel batches as in reproducer-w05-4's replay), the text and decision the model would receive equal main's on every transcript |
| s2 platform time | The sum of platform-recorded hook time per worker run, in paired headless runs, is at most 20% of main's (n ≥ 3 pairs) |
| s3 outage | m4 holds for the real build, and the budget's 150% block either still holds during an outage or the outage is announced to the worker and the PI |
| s4 code | Lines of production code no more than main's `budget.py` + `handback.py` + 300 for the server; selftests pass |

**Rule.** Land on main if s1–s4 pass. Otherwise do not land; report which metric failed.
