#!/bin/sh
# explorer-w01-b: regenerate every table in this folder. Read-only on transcripts. Run from this folder.
# Cost: under one minute, no model calls.
set -e
P="$HOME/.claude/projects"
G="$P/-Users-hacker-Documents-explore-combinatorics-on-binary"
PR="$P/-Users-hacker-Documents-src-CrackingShells-Murmuration-probes-out-work"
python3 -I extract_comm.py .      # dispatches.csv returns.csv reactions.csv startctx.csv
python3 -I analyze.py .           # brief_anatomy.csv handbacks.csv summary.txt
python3 -I coded_tables.py        # handbacks_coded.csv followups.csv (hand-coded columns, see script header)
python3 -I numcheck.py .          # numcheck.csv (candidates only)
python3 -I brief_dup.py > brief_dup.csv
python3 -I pair_thread.py \
  "$PR/ec70ebcf-315a-4615-b1eb-65d276b117da.jsonl" "$PR/ec70ebcf-315a-4615-b1eb-65d276b117da/subagents" \
  "$G/82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl" "$G/82e8a947-1a0c-441c-bc39-df8e2e5fa743/subagents" \
  > pair_threads.csv 2> pair_orphans.txt
