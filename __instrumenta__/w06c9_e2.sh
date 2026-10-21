# w06-c9: runs metric e2: PAIRS pairs of headless runs (main's export against the build's export, both arms of a pair at the same time), then prints the tables of w06c9_measure.py; inputs: env MAIN_COMMIT, NEW_COMMIT, PAIRS (default 5), TAG (run name prefix), REPO (repository to `git archive` from); output: runs under /private/tmp/murmuration-w06/author-w06-6/runs/<TAG>_<i>_{main,new}, tables on stdout
# full: PAIRS=5 (about 2 minutes per pair, about USD 0.04 per run); quick: PAIRS=1
for i in $(seq 1 ${PAIRS:-5}); do
  python3 -I __instrumenta__/w06c9_run.py ${TAG}_${i}_main $MAIN_COMMIT &
  python3 -I __instrumenta__/w06c9_run.py ${TAG}_${i}_new $NEW_COMMIT &
  wait
done
PAIRLIST=""
for i in $(seq 1 ${PAIRS:-5}); do PAIRLIST="$PAIRLIST ${TAG}_${i}_main:${TAG}_${i}_new"; done
python3 -I __instrumenta__/w06c9_measure.py $PAIRLIST
