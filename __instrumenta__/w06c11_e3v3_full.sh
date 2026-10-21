#!/bin/sh
# w06-c11 (E3 v3): the full registered v1 run in 5 parallel shards (each in its own arena folder); input: a commit, optionally shard numbers 0-4; output: shard results under /private/tmp/murmuration-w06/author-w06-5/shard*/ (derived json) and, when the shards finish, the tables from w06c11_e3v3_report.py. Usage: sh __instrumenta__/w06c11_e3v3_full.sh <commit> [shards]   (from the repository root; about 12 min)
C=${1:?commit}
shift
SHARDS=${*:-0 1 2 3 4}
B=/private/tmp/murmuration-w06/author-w06-5
rm -f "$B/v3.pids" "$B/v3.done"
for i in $SHARDS; do
  rm -rf "$B/v3shard$i"
  W06_ARM=C W06C7_S=$B/v3shard$i SHARD=$i/5 python3 -I __instrumenta__/w06c10_e3v2_all.py "$C" full > "$B/v3_s$i.log" 2>&1 &
  echo $! >> "$B/v3.pids"
done
wait
echo finished > "$B/v3.done"
