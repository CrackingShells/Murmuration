#!/bin/bash
# runs the three remaining sets in order; usage: orchestrate.sh <logdir>
cd "$(dirname "$0")"
until grep -q "ins-pm-bypassPermissions" /tmp/perm.log; do sleep 3; done
for s in perm modes hookrace; do python3 -I matrix.py $s > "$1/$s.log" 2>&1; done
echo finished > "$1/finished.flag"
