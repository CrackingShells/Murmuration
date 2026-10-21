#!/bin/sh
# Checks that `git commit -m M -- <path>` commits only <path> while another path is staged (the w05 sweep case); input: none (scratch repo in $1 or a temp dir); output: PASS/FAIL lines.
set -eu
d=${1:-$(mktemp -d)}; mkdir -p "$d"; cd "$d"; git init -q .; git config user.email t@t; git config user.name t
echo a > mine.txt; echo b > theirs.txt; git add . ; git commit -qm init
echo a2 > mine.txt; echo b2 > theirs.txt
git add theirs.txt                      # another agent stages its file
git add mine.txt; git commit -qm plain  # plain commit: sweeps both
[ "$(git show --name-only --format= HEAD | sort | tr '\n' ' ')" = "mine.txt theirs.txt " ] && echo "PASS plain commit swept the other agent's staged file" || echo "FAIL plain"
echo a3 > mine.txt; echo b3 > theirs.txt; git add theirs.txt
git commit -qm pathspec -- mine.txt     # pathspec commit: only mine
[ "$(git show --name-only --format= HEAD)" = "mine.txt" ] && echo "PASS pathspec commit took only mine.txt" || echo "FAIL pathspec"
[ "$(git diff --cached --name-only)" = "theirs.txt" ] && echo "PASS theirs.txt still staged for its owner" || echo "FAIL staged"
