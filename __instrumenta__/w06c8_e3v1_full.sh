#!/bin/sh
# w06-c8 (E3 v1): the full registered v1 run in 5 parallel shards (each in its own arena folder); input: a commit, optionally shard numbers 0-4; output: shard results under /private/tmp/murmuration-w06/author-w06-5/shard*/ (derived json) and, when the shards finish, the tables from w06c8_e3v1_report.py. Usage: sh __instrumenta__/w06c8_e3v1_full.sh <commit> [shards]   (from the repository root; about 12 min)
C=${1:?commit}
shift
SHARDS=${*:-0 1 2 3 4}
B=/private/tmp/murmuration-w06/author-w06-5
rm -f "$B/v1.pids" "$B/v1.done"
for i in $SHARDS; do
  rm -rf "$B/v1shard$i"
  W06C7_S=$B/v1shard$i SHARD=$i/5 python3 -I __instrumenta__/w06c8_e3v1_all.py "$C" full > "$B/v1_s$i.log" 2>&1 &
  echo $! >> "$B/v1.pids"
done
wait
echo finished > "$B/v1.done"
