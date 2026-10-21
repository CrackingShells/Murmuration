#!/usr/bin/env python3
"""Give each Murmuration worker a budget in USD and in minutes and send it plain notes that get denser towards the limit and go on past it.

Runs as a hook on SubagentStart, PreToolUse(Agent), PostToolUse and SubagentStop. It reads the hook JSON from
stdin. It does nothing outside an initialized lab (a folder with `__statera__/`), for the main thread (except the dispatch
record below), and for any agent whose type is not `murmuration:<role>`.

  SubagentStart  `additionalContext`: the two budgets (USD B, minutes T) and the contract, in the same plain tone as the notes: a note
                 arrives at 50, 75, 87.5 and 93.75 percent of the larger of the two fractions and at every check from 100 percent;
                 from 100 percent the worker finishes if one or two more steps do it, else hands back with its case, and the PI,
                 who holds the money, decides whether to resume it with more. A resumed worker's run clock restarts (the idle gap
                 does not count); the platform does not deliver a SubagentStart `additionalContext` to a resumed worker (1 of 1 resumes), so none is sent.
  PreToolUse     On the `Agent` tool (the PI dispatching a worker): the brief's `Budget:` and `Time:` lines are put in a short-lived
  (Agent)        file, because the transcript of a new worker does not exist yet at SubagentStart; the start note reads the file. A
                 figure below the floor (USD 0.30, 3 minutes) is logged as a `warn` line and left as it is.
  PostToolUse    The check, once per request however many tool calls the request made (a counter in the state: parallel calls run
                 parallel hook processes). It sends one message: below 1.5 of the larger fraction, an `additionalContext` note with the
                 current figures when the fraction has passed the next of 0.5, 0.75, 0.875, 0.9375 (one note however many thresholds were
                 skipped) and at every check from 1.0: below 1.0 the line `Spent X of USD Y (Z%); t of T min (W%)` and nothing else, from
                 1.0 the line followed by one sentence (finish, or hand back and ask). From 1.5: `decision: block` with the line and "hand
                 back now" (the agent can still call the hand-back tool, which is never blocked). The hand-back call itself gets nothing.
                 After HALT_AFTER earlier blocks, `continue: false`: the backstop; measured earlier (w02-c3) to lose the hand-back, so a
                 backstop and not the stop. There is no PostToolBatch registration (w05-c4): `decision: block` on PostToolBatch ends the worker like
                 `continue: false` (measured: the run stops, no hand-back, no SubagentStop), so the ceiling cannot sit there, and one start per
                 tool call instead of two is the saving. PostToolUse does not fire for a failed or a denied call (measured, w03-c1: 13 of 172
                 calls), so a request whose calls all failed is checked at the next call that succeeds.
  SubagentStop   one `end` line in the log, and the run's active time is closed.

The fractions. USD / B and active minutes / T. Active minutes are the minutes between SubagentStart and SubagentStop of each run, summed:
the idle gap between a hand-back and the resume does not count. B is in USD. Default by role: explorer 3.0, author 3.0, reproducer 2.0,
proof-adversary 2.0 (any other murmuration role 2.0). T is in minutes: explorer 20, author 20, reproducer 15, proof-adversary 15 (other
roles 15). A line of exactly the form `Budget: USD <number>`, and one of the form `Time: min <number>`, in the agent's first user message
(its brief) replace the defaults. The floor is no budget under USD 0.30 and no time under 3 minutes: with about USD 0.03 to 0.04 for the first
request of a worker, a smaller budget is used up before any note can come (w02-c8). A figure below it is logged, not changed.

The raise. A later message from the coordinator (the PI) with a line `Budget: USD x` or `Time: min t` grants that much more from that moment.
In the worker's transcript (measured, w03-c1) a message that resumes a stopped worker is a user record with `origin.kind == "coordinator"`, and a
message to a worker that is still running is an `attachment` of type `queued_command` with the same origin; a peer's message has `origin.kind == "peer"`.
The limit becomes the limit becomes
max(limit, spend at the message) + x and likewise for the minutes, so the worker is never over budget straight after a raise. The
figures are cumulative; the schedule restarts above the new fraction. A message from anyone else, a tool result, and the brief are not raises. A
resume without such a line changes nothing: the worker keeps its spend and its limits.

Spend is the list price of the tokens in the subagent's transcript: input, cache read, cache write for 5 minutes and for 1 hour, which are
exact, and output. In `auto` permission mode the transcript holds only 6 to 15 percent of the output as a count, so the recorded output is a
lower bound there (the log's `used_recorded`). The thresholds use the larger of the recorded count and an estimate from the message content
(`CHARS_PER_TOKEN`); the log's `used` is that figure and `basis` says so. The price table is the one `lab_status.py` uses
(https://platform.claude.com/docs/en/about-claude/pricing, fetched 2026-10-19); the selftest checks that the two agree.

State per agent: `__statera__/.harness/<agent_id>.json` (git-ignored by a `.gitignore` inside the folder), updated under a file lock and
replaced atomically. Log, one JSON line per `start`, `warn`, `raise`, `note`, `stop`, `halt`, `end` and `deny` (the deny is written by
`handback.py`): `__statera__/harness.jsonl`. `frac` is USD / B, `t_frac` is minutes / T, `which` names the budget that decided.

Lean (w04-c5, w05-c4). A hook process is started on every tool call of every agent, so its cost is paid thousands of times: (1) `hooks/hooks.json` starts it for
PostToolUse through a POSIX sh test that runs Python only when the payload has an `"agent_id"` key (the main thread has none and the script acts for no one there);
the gate reads its input in one block (`$(</dev/stdin)`, where the shell has it, else byte by byte); Python starts as `python3 -S` (no `site`; the environment is
respected, so PYTHONDONTWRITEBYTECODE stops bytecode being written into the plugin folder, and the code is then compiled at each call); (2) the imports are `json`,
`os`, `sys`, `time`, `zlib`, `fcntl` and the sibling `handback_core`; `re`, `datetime`, `hashlib` load when a path needs them; (3) the transcript is read from the byte offset where the last
check stopped (`sc` in the state file: the offset, the last bytes before it as a guard, the cost of every finished request, and the last CARRY_OPEN requests in full);
the result equals a read from the start (selftest 2b) and a read from the start is made whenever the guard fails, the file shrank, or a record names a finished
request; (4) the selftest is in `budget_selftest.py`, which is not imported at a call. The file's last line, if it is not yet ended by a newline, waits for the
next check (an unfinished line cannot be parsed anyway).

A hook runs only between tool calls: one tool call that runs for 10 minutes cannot be interrupted, and the time is checked when it returns.
The script never fails an agent: anything unexpected is dropped and it exits 0 with no output.

Usage:
    budget.py              read a hook event from stdin
    budget.py --selftest   check the script on a temporary project (the checks are in budget_selftest.py)
"""
import sys

import budget_core

if __name__ == "__main__":
    sys.exit(budget_core.run(sys.argv[1:]))
