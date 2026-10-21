#!/bin/sh
# Prints, for the shell the Bash tool gave this command: env var NAMES (no values), PATH entries, which common tools resolve, and alias/function counts.
echo "SHELLNOW=$(ps -o comm= -p $PPID)"
echo "VARS=$(env | cut -d= -f1 | sort | tr '\n' ' ')"
echo "PATH_ENTRIES:"; echo "$PATH" | tr ':' '\n'
for c in node npm npx conda mamba nvm brew cargo rustc go java R julia gh docker; do printf "%s=%s\n" $c "$(command -v $c 2>/dev/null)"; done
