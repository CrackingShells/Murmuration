#!/usr/bin/env python3
"""Prototype hook (claim w01-c3): append one line per SessionStart / SubagentStart / SubagentStop to the lab's run index.

    index_hook.py [--lab DIR]       reads the hook input on stdin; DIR overrides the lab found from the input's `cwd`

Line: {"ts", "event", "session_id", "agent_id", "agent_type", "transcript_path", "cwd"}  in <lab>/__expensa__/runs.jsonl.
The lab is the nearest folder above the input's `cwd` that holds `__statera__/` (not CLAUDE_PROJECT_DIR, which in a
worktree session names the main checkout, S-w01-research-pi-5). No lab found: write nothing. Never fails the session.
Input fields used are those of the probe report (CITED, __reports__/platform_probes/01-findings_v1.md rows 3-4,
Claude Code 2.1.296): session_id, transcript_path, cwd, agent_id, agent_type, hook_event_name.
"""
import json, os, sys, time

def lab_above(cwd):
    d = os.path.abspath(cwd or os.getcwd())
    while True:
        if os.path.isdir(os.path.join(d, "__statera__")):
            return d
        if os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)

def main(argv):
    try:
        ev = json.load(sys.stdin)
        lab = argv[argv.index("--lab") + 1] if "--lab" in argv else lab_above(ev.get("cwd"))
        if lab:
            os.makedirs(os.path.join(lab, "__expensa__"), exist_ok=True)
            line = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "event": ev.get("hook_event_name"), "session_id": ev.get("session_id"),
                    "agent_id": ev.get("agent_id"), "agent_type": ev.get("agent_type"),
                    "transcript_path": ev.get("agent_transcript_path") or ev.get("transcript_path"), "cwd": ev.get("cwd")}
            with open(os.path.join(lab, "__expensa__", "runs.jsonl"), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(line) + "\n")  # one write: appends of one short line do not interleave
    except Exception:
        pass
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
