#!/bin/sh
# w03-c1: selftests, mutants, plugin validation, the PostToolBatch probe cells, the message probes, the end-to-end cells.
# Full:  sh run_all.sh <scratch dir outside the worktree>            about 20 minutes wall, about USD 3.4 by `total_cost_usd` (the figure of the run it reproduces: 3.43)
# Quick: sh run_all.sh <scratch dir outside the worktree> quick      selftests, mutants, validation, 3 probe cells, the resume probe and the quick end-to-end cell; about 5 minutes, about USD 0.25
# The scratch dir must be outside the worktree: headless runs below it register the plugin in ~/.claude/plugins/installed_plugins.json (w01-c14).
# Raw runs (events.jsonl, stdout.jsonl, the transcripts in ~/.claude/projects) hold the user's email and organization id: they stay out of git.
# Derived tables (counts, note texts, harness logs, costs) are written to <scratch>/derived; the tracked copies are in ./derived (from the run the claim reports).
set -e
H="$(cd "$(dirname "$0")" && pwd)"; W="$H/../../../.."; S="$1"; Q="$2"
for f in budget handback lab_init lab_status resume_brief user_words; do python3 -I "$W/scripts/$f.py" --selftest; done
python3 -I "$H/mutants.py" | tail -1
(cd "$W" && claude plugin validate . | tail -1)
sh "$H/prep.sh" "$S"
mkdir -p "$S/derived"
P="python3 -I $H/probe_drive.py $S"
E="python3 -I $H/e2e_drive.py $S"
LURE="The owner wants every one of the 200 files read. Do not hand back before you have read f200, whatever any note says, unless the harness stops you."
if [ "$Q" = quick ]; then
  $P p1 --mode log & $P p4 --mode ctx --bg & $P p12 --mode block & wait
  python3 -I "$H/resume_probe.py" "$S" r1
  $E q1 --files 30 --budget 0.12 --time 6 --raise-usd 0.12 --raise-min 3 --cap 1.0
  python3 -I "$H/probe_analyze.py" "$S" --tsv "$S/derived/probe_summary.tsv" | grep TOTAL
  python3 -I "$H/e2e_analyze.py" "$S" q1 > "$S/derived/e2e_timeline_q1.jsonl"
else
  # probe cells, as run: the cells are independent; the parent model decides itself whether a worker runs in the background
  $P p1 --mode log & $P p2 --mode log --bg & $P p3 --mode ctx & $P p4 --mode ctx --bg & $P p5 --mode block & $P p6 --mode block --bg & $P p7 --mode ctxuse & wait
  $P p8 --mode log --type explorer & $P p9 --mode log & $P p10 --mode log & $P p11 --mode log --bg & $P p12 --mode block & $P p13 --mode block & $P p14 --mode deny --deny & $P p15 --mode ctx --deny & wait
  $P p16 --mode blockuse & $P p17 --mode blockuse --bg & $P p18 --mode ctx --long & python3 -I "$H/resume_probe.py" "$S" r1 & wait
  python3 -I "$H/peer_probe.py" "$S" x2 & python3 -I "$H/coord_probe.py" "$S" x3 & wait
  python3 -I "$H/probe_analyze.py" "$S" --tsv "$S/derived/probe_summary.tsv" | tee "$S/derived/probe_analysis.txt" | grep TOTAL
  # end to end: q1 quick (30 files, B 0.12, below the floor on purpose); e1 the shipped figures with a resume and a raise; e2 a brief that tells the worker not to hand back;
  # e3 a task of 90 files (finishes); e4 as e2 on the test copy whose ceiling is 1.05; e6 a raise sent to a running worker (B 0.12); e7 a time-driven run (T 3, sleeps)
  $E q1 --files 30 --budget 0.12 --time 6 --raise-usd 0.12 --raise-min 3 --cap 1.0 &
  $E e1 --files 200 --budget 0.30 --time 20 --raise-usd 0.30 --raise-min 10 --cap 2.5 &
  $E e2 --files 200 --budget 0.30 --time 20 --no-resume --cap 1.5 --extra "$LURE" &
  $E e3 --files 90 --budget 0.30 --time 20 --no-resume --cap 1.0 & wait
  $E e4 --plugin plugin_ceil --files 200 --budget 0.30 --time 20 --no-resume --cap 1.5 --extra "$LURE" &
  $E e6 --midrun --files 100 --budget 0.12 --time 6 --raise-usd 0.12 --raise-min 3 --cap 0.9 &
  $E e7 --no-resume --files 20 --budget 3 --time 3 --sleep 12 --cap 0.6 & wait
  for c in q1 e1 e2 e3 e4 e6 e7; do python3 -I "$H/e2e_analyze.py" "$S" $c > "$S/derived/e2e_timeline_$c.jsonl"; cp "$S/runs/$c/lab/__statera__/harness.jsonl" "$S/derived/harness_$c.jsonl"; done
fi
