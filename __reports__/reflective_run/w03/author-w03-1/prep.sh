#!/bin/sh
# Build the plugin copies the runs use, outside the worktree: plugin_e2e is the working tree's plugin parts (agents, skills, scripts,
# hooks, manifest); plugin_probe is the logging-only plugin of the PostToolBatch probe (the same agents and skills, a hooks file that only logs).
# usage: prep.sh <scratch dir>     (the scratch dir must be outside the worktree)
set -e
W="$(cd "$(dirname "$0")/../../../.." && pwd)"
H="$(cd "$(dirname "$0")" && pwd)"
S="$1"; mkdir -p "$S"
rm -rf "$S/plugin_e2e" "$S/plugin_probe" "$S/plugin_ceil"
mkdir -p "$S/plugin_e2e"
for d in agents skills scripts hooks .claude-plugin; do cp -R "$W/$d" "$S/plugin_e2e/$d"; done
# plugin_ceil: the same, with the hard ceiling at 1.05 instead of 1.5 (a test-only copy, so that a short run reaches the ceiling)
rm -rf "$S/plugin_ceil"; cp -R "$S/plugin_e2e" "$S/plugin_ceil"
python3 - "$S/plugin_ceil/scripts/budget.py" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read(); old = "OVER_AT, HARD_AT = 1.0, 1.5"
assert old in s
open(p, "w").write(s.replace(old, "OVER_AT, HARD_AT = 1.0, 1.05"))
PY
mkdir -p "$S/plugin_probe"
for d in agents skills .claude-plugin; do cp -R "$W/$d" "$S/plugin_probe/$d"; done
mkdir -p "$S/plugin_probe/hooks" "$S/plugin_probe/scripts"
cp "$H/plog.py" "$S/plugin_probe/scripts/plog.py"
python3 - "$S/plugin_probe/hooks/hooks.json" <<'PY'
import json, sys
h = {e: [{"hooks": [{"type": "command", "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plog.py"', "timeout": 10}]}]
     for e in ["PreToolUse", "PostToolUse", "PostToolBatch", "SubagentStart", "SubagentStop", "Stop"]}
json.dump({"hooks": h}, open(sys.argv[1], "w"), indent=1)
PY
find "$S" -name __pycache__ -prune -exec rm -rf {} +
echo "plugins in $S:" $(ls "$S" | grep plugin_)
