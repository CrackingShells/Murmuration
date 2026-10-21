#!/usr/bin/env python3
# SessionStart hook: reads the event on stdin, compares CLAUDE_PLUGIN_ROOT with the git toplevel of the event's cwd (found by walking up to a `.git`, no git call); prints a warning as additionalContext when they differ, nothing otherwise.
# Uses the event's cwd, not CLAUDE_PROJECT_DIR: in a Desktop worktree session CLAUDE_PROJECT_DIR is the main checkout (w05 explorer-w05-e, run H1).
import json, os, sys

def toplevel(p):
    p = os.path.realpath(p)
    while True:
        if os.path.exists(os.path.join(p, ".git")):
            return p
        q = os.path.dirname(p)
        if q == p:
            return None
        p = q

try:
    ev = json.load(sys.stdin)
except Exception:
    ev = {}
root = os.path.realpath(os.environ.get("CLAUDE_PLUGIN_ROOT", ""))
top = toplevel(ev.get("cwd") or os.getcwd())
if top and root != top and os.path.exists(os.path.join(top, ".claude-plugin", "plugin.json")):
    msg = f"WARNING: this session runs the plugin read from {root}, but its own folder {top} holds a plugin too. Edits there are not what runs."
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}}))
