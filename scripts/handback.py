#!/usr/bin/env python3
"""Keep every subagent's hand-back, verbatim, in a lab project; make an explorer leave its report file.

Runs as a SubagentStop hook, as a PostToolUse hook on the `SubagentHandback` tool, and as a
PreToolUse hook on the same tool. It reads the hook JSON from stdin and does nothing outside an
initialized lab (a folder with `__statera__/`).

Saving (SubagentStop, PostToolUse): appends the agent's final message to
`__statera__/handbacks/wave-NN-<agent name>.md` (or `<agent name>.md` when the name carries no
wave). A resumed agent appends a second section. The file is a recovery aid for the PI and humans:
no hook, brief or skill may feed it to agents: in auto mode the harness may withhold or flag a hand-back and the hook
cannot tell, so the file can hold text the PI never received.

Where the message sits depends on the permission mode:
  default, bypassPermissions  SubagentStop.last_assistant_message
  auto                        PostToolUse(SubagentHandback).tool_input.message; SubagentStop has no text

Each section starts with a header line carrying `bytes=N`, so a reader can slice the text exactly
even when it contains lines that look like headers. If a SubagentStop arrives without text and no
delivered section of that agent was written in the last 30 s, a `status=missing` section records the gap. In auto mode a
SubagentStop that does carry text is a turn the agent ended without calling SubagentHandback (the harness answers that
the report was not delivered): it is stored as `status=draft`, and the later SubagentHandback is a separate section.

Report check (PreToolUse on `SubagentHandback`, explorers only, `murmuration:explorer`): if no file
under `__reports__/` has the agent's name in its path, the first hand-back is denied with a reason
that names `__reports__/wave-NN/<name>/00-findings_v0.md`. At most one deny per agent (a marker file
`__statera__/.harness/<agent_id>.denied`, created atomically); the second attempt goes through, so a
report is never lost to a loop (a deny on every attempt can end the run with no hand-back delivered). The deny
is logged as one JSON line in `__statera__/harness.jsonl`.

Saving never blocks an agent and prints nothing. Anything unexpected is dropped, and the hook exits 0.

Usage:
    handback.py              read a hook event from stdin
    handback.py --selftest   check the script on a temporary project (the checks are in handback_selftest.py)

Lean (w04-c5, w05-c4): the code is in `handback_core.py` (Python caches its bytecode where it may); `re`, `hashlib` and `datetime` are imported by the paths that need them. The report check looks
first for the deny marker (a second hand-back is never searched for), then in the convention's own folder (`__reports__/wave-NN/<name>/`), and walks all of
`__reports__/` only when both fail.
"""
import sys

import handback_core

if __name__ == "__main__":
    sys.exit(handback_core.run(sys.argv[1:]))
