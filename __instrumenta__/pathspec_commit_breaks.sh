#!/bin/sh
# Probes git commit -m M -- <paths> against edge cases (staged deletion, staged rename, same file staged by other then modified by me, commit -a, new untracked file by other agent, path with nothing changed); input: scratch dir $1; output: one result line per case.
set -u
base=${1:?scratch dir}; rm -rf "$base/w"; mkdir -p "$base/w"; cd "$base/w"
init(){ rm -rf .git *; git init -q .; git config user.email t@t; git config user.name t
 echo a>mine.txt; echo b>theirs.txt; echo c>gone.txt; echo d>old.txt; git add .; git commit -qm init; }
show(){ echo "  committed: $(git show --name-status --format= HEAD | tr '\t\n' ': ' )"; echo "  still staged: $(git diff --cached --name-status | tr '\t\n' ': ')"; }
echo "case1 staged deletion by other"; init; echo a2>mine.txt; git rm -q gone.txt; git commit -qm m -- mine.txt; show
echo "case2 staged rename by other"; init; echo a2>mine.txt; git mv old.txt new.txt; git commit -qm m -- mine.txt; show
echo "case3 other staged theirs.txt, I then also modified theirs.txt and name it"; init; echo b2>theirs.txt; git add theirs.txt; echo b3>theirs.txt; echo a2>mine.txt; git commit -qm m -- mine.txt theirs.txt; show; echo "  theirs.txt in HEAD: $(git show HEAD:theirs.txt)"
echo "case3b same, I name only mine.txt"; init; echo b2>theirs.txt; git add theirs.txt; echo b3>theirs.txt; echo a2>mine.txt; git commit -qm m -- mine.txt; show
echo "case3c I modify mine.txt that other staged earlier, then commit -- mine.txt"; init; echo a2>mine.txt; git add mine.txt; echo a3>mine.txt; echo b2>theirs.txt; git add theirs.txt; git commit -qm m -- mine.txt; show; echo "  mine.txt in HEAD: $(git show HEAD:mine.txt)"
echo "case4 commit -a contrast"; init; echo a2>mine.txt; echo b2>theirs.txt; git add theirs.txt; echo c2>gone.txt; git commit -aqm m; show
echo "case5 new file added by other, pathspec commit of mine"; init; echo n>newf.txt; git add newf.txt; echo a2>mine.txt; git commit -qm m -- mine.txt; show
echo "case6 pathspec of my NEW untracked file (no git add)"; init; echo n>mynew.txt; git commit -qm m -- mynew.txt 2>&1 | head -2; show
echo "case7 pathspec of my new file after git add, other staged too"; init; echo n>mynew.txt; git add mynew.txt; echo b2>theirs.txt; git add theirs.txt; git commit -qm m -- mynew.txt; show
echo "case8 my staged deletion named"; init; git rm -q gone.txt; echo b2>theirs.txt; git add theirs.txt; git commit -qm m -- gone.txt; show
