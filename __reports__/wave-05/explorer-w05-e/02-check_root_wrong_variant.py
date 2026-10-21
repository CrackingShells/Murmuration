#!/usr/bin/env python3
# SessionStart check: compares CLAUDE_PLUGIN_ROOT with the session's own folder (CLAUDE_PROJECT_DIR), no git call; prints a warning as additionalContext when they differ.
import os, json
r = os.path.realpath(os.environ.get("CLAUDE_PLUGIN_ROOT", "")); p = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR", ""))
if r != p:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": f"WARNING: plugin read from {r}, session folder is {p}"}}))
