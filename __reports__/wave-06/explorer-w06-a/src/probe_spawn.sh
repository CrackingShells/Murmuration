#!/bin/sh
# diagnostic: who spawned this hook, with what shell and env
{
echo "--- $(date +%s)"
echo "self: $0 $$ ppid=$PPID"
ps -o pid=,ppid=,command= -p $PPID
gp=$(ps -o ppid= -p $PPID | tr -d ' ')
ps -o pid=,ppid=,command= -p "$gp"
echo "SHELL=$SHELL CLAUDE_CODE_SHELL=$CLAUDE_CODE_SHELL BASH_ENV=$BASH_ENV ENV=$ENV"
echo "interactive flags: $-"
} >> "${W06_PROBE_LOG:-/dev/null}" 2>&1
echo "probe-sh"
