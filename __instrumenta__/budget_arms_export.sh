#!/bin/sh
# Builds the three plugin exports of wave-4 experiments E1/E2 (A unchanged, B with one explorer line, C with every budget.py output off) from a named commit by `git archive`, into <scratch>/plugin_A, plugin_B, plugin_C.
# usage: budget_arms_export.sh <scratch dir outside the repo> <commit> [B-extra-line-file]   Output: the three folders and <scratch>/export_commit.txt. Stdlib python3 + git only.
set -e
S="$1"; C="$2"
rm -rf "$S/plugin_A" "$S/plugin_B" "$S/plugin_C"; mkdir -p "$S/plugin_A"
git archive "$C" agents skills scripts hooks .claude-plugin | tar -x -C "$S/plugin_A"
cp -R "$S/plugin_A" "$S/plugin_B"; cp -R "$S/plugin_A" "$S/plugin_C"
python3 - "$S" <<'PY'
import sys, os
S = sys.argv[1]
# B: one line in agents/explorer.md, after the paragraph that names the deliverable
p = os.path.join(S, "plugin_B", "agents", "explorer.md"); s = open(p).read()
anchor = "Your deliverable is one findings report, `__reports__/wave-NN/<your name>/00-findings_v0.md`, from the\nreport template of the research-loop skill, and a short hand-back message that points to it.\n"
assert anchor in s
line = "Write the findings report before you hand back, also when a budget note tells you to hand back; the hand-back message then points to it.\n"
open(p, "w").write(s.replace(anchor, anchor + line))
# C: budget.py keeps its state and log (frac, t_frac, note/stop lines) but answers nothing: no start note, no graded note, no ceiling block
p = os.path.join(S, "plugin_C", "scripts", "budget.py"); s = open(p).read()
old = "def handle(event, now=None):\n"
assert s.count(old) == 1
new = "def handle(event, now=None):\n    \"\"\"ARM C PATCH: the real handler runs (state and log lines as before), its answer is dropped.\"\"\"\n    _handle(event, now)\n    return None\n\n\ndef _handle(event, now=None):\n"
open(p, "w").write(s.replace(old, new))
PY
find "$S" -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
echo "$C" > "$S/export_commit.txt"
(cd "$S" && diff -r plugin_A plugin_B; diff -r plugin_A plugin_C) || true
