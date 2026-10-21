## S-w05-reproducer-w05-4-1
The replay set called "291" is 197 distinct transcripts: 94 file names occur more than once, and the md5 of the 291 files gives 197 distinct. The dump folder of hook_replay_equiv.py is keyed by file name, so duplicates overwrite each other there.
refs: /private/tmp/murmuration-w05/reproducer-w05-4/list291.txt; __reports__/reflective_run/w04/author-w04-4/derived/replay_transcripts_291.txt

## S-w05-reproducer-w05-4-2
The replay builds one PostToolBatch per tool-result record, so the old and the new build check after every result and can differ only by repeats; "285 of 291" is nearly true by construction. With one batch per assistant request, 21 of 197 transcripts differ, 11 with an extra message from the new build in the final batch that holds the hand-back. Why does the extra note matter or not on the real platform (does PostToolUse of Bash fire before the hand-back's PostToolUse)? Not measured.
refs: __instrumenta__/w05c4_replay_batched.py; /private/tmp/murmuration-w05/reproducer-w05-4/m1_batched.txt; /private/tmp/murmuration-w05/reproducer-w05-4/dump_batched/agent-afb6ca38ecdd110e9.jsonl.old.json and .new.json

## S-w05-reproducer-w05-4-3
m3 at 500 KB, short worker: my n = 30 run gave wall 0.95 (0.89 to 1.02), my n = 150 run 1.053 (1.048 to 1.059), the author's 1.06. In-run intervals under 10 points wide, between-run movement of 10 points: the bootstrap interval of a median of one run understates run-to-run (load) variation. CPU ratio 1.42 is stable in all runs. A rule keyed on wall at a payload the platform was not seen to send (max 87 KB in 2441 results) decides the claim.
refs: /private/tmp/murmuration-w05/reproducer-w05-4/timing_m3_500k.jsonl, timing_m3_500k_short_n150.jsonl

## S-w05-reproducer-w05-4-4
m2 is 52.5% (44 to 59) for the author and 56.1% (42 to 58 as 1 - 0.491..0.418) for me, on a machine where old worker PostToolUse took 82 ms against the author's 130. The 50% line is crossed by the saving only through the 803 gone PostToolBatch starts; the 50% threshold is inside the author's interval, so "met" rests on the point estimate.
refs: /private/tmp/murmuration-w05/reproducer-w05-4/m2_sum.txt; __reports__/wave-05/author-w05-3/m2_sum.md

## S-w05-reproducer-w05-4-5
m4 in E7 says 150%; the run tested 164% (a single run, the note schedule 51 to 108% before). Not re-run by me. The new build's check exists only on PostToolUse, which does not fire for failed or denied calls (13 of 172 in w03-c1), so a batch made only of failures would have no check; untested.
refs: __pondus__/w05-c4.md (m4, scope)

## S-w05-reproducer-w05-4-6
My independent result text names "agent-a7779c3c1800fb1b5... records 34-37 of the second list entry"; the second list entry is agent-a41c53b7f77ba2588 (records 34-37 show A, A, U, U with one message id). Appended text is not rewritten; this is the correction.
refs: /private/tmp/murmuration-w05/reproducer-w05-4/list291.txt line 2

## S-w05-reproducer-w05-4-7
Correction to puzzle 4: the saving's interval on my run is 50.9 to 58.2% (new/old 0.418 to 0.491), not "42 to 58". My verdict section in `__pondus__/w05-c4.md` is appended but not committed, because the file also holds the author's uncommitted amendments and I commit only my own paths.
refs: /private/tmp/murmuration-w05/reproducer-w05-4/m2_sum.txt
