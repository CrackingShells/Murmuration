#!/bin/zsh
# Runs one headless `claude -p` (not logged in, so no model call) in a scratch CLAUDE_CONFIG_DIR and prints the dummy plugin SessionStart log line (root, marker, cwd); inputs: label, cwd, extra claude flags; output: hook.log, dbg_<label>.log beside it in the scratch folder.
B=/private/tmp/murmuration-w05/explorer-w05-e
export CLAUDE_CONFIG_DIR=${CFG:-$B/cfg}
label=$1; cwd=$2; shift 2
rm -f $B/hook.log $B/dbg_$1.log
( cd $cwd && timeout 90 claude -p ok --model haiku --debug-file $B/dbg_$label.log "$@" </dev/null >$B/out_$label.txt 2>&1 )
echo "== $label cfg=$CLAUDE_CONFIG_DIR cwd=$cwd out: $(head -c 60 $B/out_$label.txt | tr '\n' ' ')"
[ -f $B/hook.log ] && python3 -c "
import json
for l in map(json.loads,open('$B/hook.log')):
    print('  root=',l['root'],'marker=',l['marker'],'cwd=',l['cwd'],'root_is_toplevel=',l['root_is_toplevel'])" || echo "  (no SessionStart hook line)"
