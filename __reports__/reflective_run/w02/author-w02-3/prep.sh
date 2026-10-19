#!/bin/sh
# Build the three plugin copies used by drive.py, outside the worktree.
# usage: prep.sh <scratch dir>     (run from anywhere; reads the worktree this file sits in)
set -e
W="$(cd "$(dirname "$0")/../../../.." && pwd)"
S="$1"; mkdir -p "$S"
rm -rf "$S"/plugin_*
# head: agents and skills as committed (the explorer's file does not ask for a report file), scripts and hooks as in the working tree
mkdir -p "$S/plugin_head"
git -C "$W" archive HEAD agents skills .claude-plugin | tar -x -C "$S/plugin_head"
cp -R "$W/scripts" "$S/plugin_head/scripts"; cp -R "$W/hooks" "$S/plugin_head/hooks"
# wt: the whole working tree's plugin parts (agents and skills as author-w02-4 has them now)
mkdir -p "$S/plugin_wt"
for d in agents skills scripts hooks .claude-plugin; do cp -R "$W/$d" "$S/plugin_wt/$d"; done
# nohooks: head with an empty hooks file (the control)
cp -R "$S/plugin_head" "$S/plugin_nohooks"; echo '{"hooks":{}}' > "$S/plugin_nohooks/hooks/hooks.json"
# test-only copies: the default budgets scaled to USD 0.06 so a short task crosses them (no brief line needed), and one without the 80 percent note
for v in small smallhead large; do
  src=wt; [ $v = smallhead ] && src=head
  B=0.06; [ $v = large ] && B=0.30
  cp -R "$S/plugin_$src" "$S/plugin_$v"
  python3 - "$S/plugin_$v/scripts/budget.py" $B <<'PY'
import sys
p, b = sys.argv[1], sys.argv[2]; s = open(p).read()
old = 'DEFAULT = {"explorer": 3.0, "author": 3.0, "reproducer": 2.0, "proof-adversary": 2.0}'
assert old in s
open(p, "w").write(s.replace(old, 'DEFAULT = {"explorer": %s, "author": %s, "reproducer": %s, "proof-adversary": %s}' % ((b,) * 4)))
PY
done
cp -R "$S/plugin_small" "$S/plugin_smallstop"
python3 - "$S/plugin_smallstop/scripts/budget.py" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = "NOTE_AT, STOP_AT, HARD_AT = 0.8, 1.0, 1.5"
assert old in s
open(p, "w").write(s.replace(old, "NOTE_AT, STOP_AT, HARD_AT = 9.0, 1.0, 1.5"))
PY
# control with the working-tree agents and no hooks
cp -R "$S/plugin_wt" "$S/plugin_nohooks_wt"; echo '{"hooks":{}}' > "$S/plugin_nohooks_wt/hooks/hooks.json"
find "$S" -name __pycache__ -prune -exec rm -rf {} +
echo "plugins in $S:" $(ls "$S" | grep plugin_)
