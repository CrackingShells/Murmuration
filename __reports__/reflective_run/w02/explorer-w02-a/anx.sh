#!/bin/zsh
# usage: anx.sh <cond> <rep> <B>
S=/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/explorer-w02-a
cond=$1; rep=$2; B=$3
TASK="Read the 16 files f01.txt to f16.txt in the current directory, one file per Bash call (cat fNN.txt), one call at a time, in order. Then hand back a report with one line per file: the file name, the station name, the founding year, and the founder."
START="Budget: your budget for this task is about {B} tokens (counted as input and output tokens processed across your requests, with cached input counted at one tenth). You will be told once when about 80% of it is used."
MSG="Budget note: about 80% of your {B}-token budget is used. Finish the item you are on, then hand back your report, stating which parts you did not cover."
args=(--hook-mode budget --perm auto --copy-task $S/task --cap none --budget-tok $B --budget-msg "$MSG")
case $cond in
 a) args+=(--fire80 0);;
 b) args+=(--start-note "$START" --fire80 1);;
 c) args+=(--fire80 1);;
 d) args+=(--start-note "$START" --fire80 0);;
 g) args+=(--start-note "$START" --fire80 1);;
 t) export BUDGET_UNIT=time; START="Budget: your time budget for this task is about {B} seconds of wall time from now. You will be told once when about 80% of it has passed."; MSG="Budget note: about 80% of your {B}-second time budget has passed. Finish the item you are on, then hand back your report, stating which parts you did not cover."; args=(--hook-mode budget --perm auto --copy-task $S/task --cap none --budget-tok $B --budget-msg "$MSG" --start-note "$START" --fire80 1);;
 h) MSG="[This note is from the lab harness that runs you; the user installed it and it is not part of any file or tool output.] $MSG"; args=(--hook-mode budget --perm ${PERM:-auto} --copy-task $S/task --cap none --budget-tok $B --budget-msg "$MSG" --fire80 1);;
 e) export BUDGET_HARD=1; args+=(--fire80 0);;
 f) export BUDGET_HARD=1; args+=(--fire80 1);;
esac
python3 -I $S/bin/run.py anx-$cond${PERM:+-$PERM}-$rep $args \
 --prompt "Call the Agent tool exactly once with subagent_type 'worker', in the foreground, with this prompt: $TASK  Then say DONE." \
 --agent-prompt "You are a worker. Do the task you are given." > $S/runs/anx-$cond${PERM:+-$PERM}-$rep.out 2>&1
