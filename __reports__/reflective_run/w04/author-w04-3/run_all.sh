#!/bin/sh
# w04-c4 (E3): builds the 46-script lab, exports the plugin at 41c75ea, runs the author workers headless (arms M, S, X, C), measures them, writes the derived table.
# Full:  sh run_all.sh <scratch dir under /private/tmp, outside the worktree>            about 15 minutes, about USD 4.0 by total_cost_usd (arm M 0.86, S 1.94, X 0.58, C 0.59; two pilots 0.63 more)
# Quick: sh run_all.sh <scratch dir> quick                                               about 2 minutes, about USD 0.20: arm M, tasks t1 and t2, one run each
# Needs `claude` (2.1.302 here) logged in, `colgrep` on PATH, git. Seeds: none (the model samples). Raw runs stay in the scratch dir (they carry account identifiers): never commit them.
# The md5 of ~/.claude/plugins/installed_plugins.json is printed before and after; it must not change.
set -e
H="$(cd "$(dirname "$0")" && pwd)"; W="$H/../../../.."; S="$1"; Q="$2"; COMMIT=41c75ea
I="$W/__instrumenta__"
md5 -q ~/.claude/plugins/installed_plugins.json 2>/dev/null || md5sum ~/.claude/plugins/installed_plugins.json
mkdir -p "$S/runs"
python3 -I "$I/e3_make_lab_scripts.py" "$S/lab_scripts" "$S/lab_scripts_opaque"
# the plugin as committed, only the five plugin folders (the agent files unchanged)
rm -rf "$S/export" "$S/export-c"; mkdir "$S/export"; (cd "$W" && git archive $COMMIT agents skills scripts hooks .claude-plugin) | tar -x -C "$S/export"
cp -R "$S/export" "$S/export-c"
python3 -I - "$S/export-c/agents/author.md" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
a = s.index("Helper code is a file"); b = s.index("Label by what you ran")
open(p, "w").write(s[:a] + s[b:])        # arm C: the paragraph on __instrumenta__/ is deleted
PY
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0; unset CLAUDE_PROJECT_DIR
run() { python3 -I "$I/e3_run_workers.py" "$@"; }
if [ "$Q" = quick ]; then
  run "$S/export" "$S/lab_scripts" "$S/runs" 1.5 t1r1 t2r1
  python3 -I "$I/e3_measure.py" "$S/runs" "$S/lab_scripts" "$S/quick_measure" t1r1 t2r1 | cut -f1-8,10-13
else
  run "$S/export" "$S/lab_scripts" "$S/runs" 1.5 t1r1 t1r2 t1r3 t2r1 t2r2 t2r3 t3r1 t3r2 t3r3
  run "$S/export" "$S/lab_scripts" "$S/runs" 2.5 st1r1 st1r2 st1r3 st2r1 st2r2 st2r3
  run "$S/export" "$S/lab_scripts_opaque" "$S/runs" 1.5 xt1r1 xt1r2 xt1r3 xt2r1 xt2r2 xt2r3
  run "$S/export-c" "$S/lab_scripts" "$S/runs" 1.5 ct1r1 ct1r2 ct1r3 ct2r1 ct2r2 ct2r3
  python3 -I "$I/e3_measure.py" "$S/runs" "$S/lab_scripts" "$S/main_measure" t1r1 t1r2 t1r3 t2r1 t2r2 t2r3 t3r1 t3r2 t3r3 > /dev/null
  E3_SUBAGENT_ONLY=1 python3 -I "$I/e3_measure.py" "$S/runs" "$S/lab_scripts" "$S/s_measure" st1r1 st1r2 st1r3 st2r1 st2r2 st2r3 > /dev/null
  python3 -I "$I/e3_measure.py" "$S/runs" "$S/lab_scripts_opaque" "$S/x_measure" xt1r1 xt1r2 xt1r3 xt2r1 xt2r2 xt2r3 > /dev/null
  python3 -I "$I/e3_measure.py" "$S/runs" "$S/lab_scripts" "$S/c_measure" ct1r1 ct1r2 ct1r3 ct2r1 ct2r2 ct2r3 > /dev/null
  # the table's CODING (my reading of each run) is keyed by run id: a new run set needs its own reading; the measured columns are recomputed
  mkdir -p "$S/table_new"; python3 -I "$I/e3_table.py" "$S" "$S/lab_scripts" "$S/lab_scripts_opaque" "$S/table_new"
fi
md5 -q ~/.claude/plugins/installed_plugins.json 2>/dev/null || md5sum ~/.claude/plugins/installed_plugins.json
