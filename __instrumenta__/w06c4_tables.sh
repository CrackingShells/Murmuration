#!/bin/sh
# w06-c4: writes the derived tables of the claim (s2, s3, m3 from the final-commit runs g_*, and the s1 replay summaries) to stdout; inputs: /private/tmp/murmuration-w06/author-w06-4/{runs,s1_*.txt}; no raw run output is copied, only counts and milliseconds
S=/private/tmp/murmuration-w06/author-w06-4; H=$(dirname "$0")
echo "## s2: platform-recorded hook time per run (2 workers per run), main 134e3ac against build a5e708b"
python3 $H/w06c4_measure.py s2 g_s2_main_0 g_s2_new_0 g_s2_main_1 g_s2_new_1 g_s2_main_2 g_s2_new_2
echo; echo "## m3-style context: request 0 input tokens (main thread; each worker)"
python3 $H/w06c4_measure.py m3 g_s2_main_0 g_s2_new_0 g_s2_main_1 g_s2_new_1 g_s2_main_2 g_s2_new_2
echo; echo "## s3: outage runs on a5e708b (a: kill by pid, restart works; b: restart exits; c: restart hangs; mid: the worker kills the server and the restart exits)"
python3 $H/w06c4_measure.py s3 g_b0 g_b1 g_mid0 g_mid1 g_c0
echo; echo "## s1: replay of 197 transcripts (final build; sequential and parallel result records), EQUAL / DIFF counts"
for f in final_seq final_par; do echo "$f: $(grep -c EQUAL $S/s1_$f.txt) EQUAL, $(grep -c ' DIFF' $S/s1_$f.txt) DIFF"; done
echo "mutants on the first 60 transcripts: mut1 (dispatch row without tool_input) $(grep -c ' DIFF' $S/s1_mut1.txt) DIFF; mut2 (PostToolBatch row without tool_calls) $(grep -c ' DIFF' $S/s1_mut2.txt) DIFF"
