#!/bin/sh
# w06-c7 (E3): the full registered run in 5 parallel shards (each in its own arena folder), then the derived tables; input: a commit; output: shard results under /private/tmp/murmuration-w06/author-w06-5/shard*/ and __reports__/wave-06/author-w06-5/e3_results_<sha>_full.md. Usage: sh __instrumenta__/w06c7_e3_full.sh <commit>   (run from the repository root; about 10 min)
set -e
C=${1:?commit}
B=/private/tmp/murmuration-w06/author-w06-5
for i in 0 1 2 3 4; do
  W06C7_S=$B/shard$i SHARD=$i/5 python3 -I __instrumenta__/w06c7_e3_all.py "$C" full > "$B/full_s$i.log" 2>&1 &
  echo $! >> "$B/full.pids"
done
wait
SHA=$(git rev-parse --short "$C")
python3 -I __instrumenta__/w06c7_e3_report.py "$SHA" full > "$B/report.log" 2>&1
echo finished > "$B/full.done"
