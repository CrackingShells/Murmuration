## S-w08-author-w08-2-1
The gross saving of explorer-w08-d (USD 6.0-10.3 at caps of 1,000-3,000 characters) and my net (USD 0.9-2.8 at N = 5,000) differ by the worker's side: one extra request of a Sonnet worker costs USD 0.01-0.04 and its second message about a third of the PI's per-character price, and nothing in the lab priced it before. Why did the earlier lever never include the cost of making the worker shorten?
refs: __reports__/wave-08/author-w08-2/counterfactual_S1200.md (rows N = 3000-5000), __reports__/wave-08/explorer-w08-d/tables.md section 5(c)

## S-w08-author-w08-2-2
The sign of the whole lever depends on one number nobody can measure on the worker side: how often the PI opens a worker's file once the hand-back is short. In the past it opened 19 of 26 explorers' files (73%), 17 of 90 authors' (19%), 20 of 61 reproducers' (33%), median 2,439 characters read, yet a claim head is 9,594 characters and a verdict section 6,640 (medians): when the PI does open them, it reads a small part (grep, sed). Is the PI's reading of a claim file by section a habit the gate would break (it opens the head once the message gets short) or one it keeps?
refs: __reports__/wave-08/author-w08-2/pi_side.tsv (columns pi_read, pi_read_chars), sections.tsv

## S-w08-author-w08-2-3
In the explorer live cells the worker had written all 42 ground-truth items into its report before its first hand-back, so the long message was a duplicate and the deny moved nothing; in the author cells I cannot say from the tool inputs whether the detail reached the file before or after the deny, because the worker built the files with scripts. Past explorer hand-backs (median 4,480 characters) may be the same duplicates. Do real hand-backs repeat what the report holds? A diff of 20 past hand-backs against their reports (Result section) would say, and would price the loss of "what the PI needs" directly.
refs: __reports__/wave-08/author-w08-2/live_cells.tsv (first_items_written_before_first_call), live_within.tsv

## S-w08-author-w08-2-4
Default permission mode: the worker has no `SubagentHandback` tool call, so `PreToolUse` never sees its hand-back (cell e_on_default: 5,200 bytes delivered through `SubagentStop`, no deny). In the lab's own waves every worker called the tool (216 of 217 hand-backs are tool inputs, one is a final text), but the lab's headless cells in default mode are not covered by any hand-back check, the report check included. Is that known and intended?
refs: __reports__/wave-08/author-w08-2/live_cells.tsv (row e_on_default), live_calls.tsv

## S-w08-author-w08-2-5
Haiku complied with the deny in 5 of 5 cells where it had a file and nothing said otherwise, and ignored it in the two where the brief said otherwise (told to resend unchanged; "no file, answer in your hand-back"). The second case is a real brief shape (wave 3's "the list goes into the hand-back"). A worker whose brief makes the message the deliverable pays a request for nothing, and the deny text, which says "put the detail in your file", contradicts its brief. Should the deny text defer to the brief, or should the briefs of the PI say when the message is the deliverable?
refs: __reports__/wave-08/author-w08-2/live_calls.tsv (a_nopath_auto, e_repeat_auto), live_deny_texts.txt

## S-w08-author-w08-2-6
Gate-on and gate-off cells of one pair (same files, same brief) differ by a factor of 1.7 in worker requests (10 against 6 for the explorers, 17 against 9 for the authors) before the first hand-back call, so the paired whole-cell difference (reading B of h6) is dominated by run-to-run variation of haiku, not the gate; the explorer pair's sign on that reading is negative (USD -0.035). I registered h6 without choosing between the two readings. A paired design that fixes the first message (replay it from the same worker state) would settle it; I did not build one.
refs: __reports__/wave-08/author-w08-2/live_pairs.tsv, live_within.tsv, __reports__/wave-08/01-protocol_p2_shorthandback_v0.md (h6)

## S-w08-author-w08-2-7
The PI sees the hand-back wrapped by the harness in about 1,276 characters (frame plus a closing policy paragraph, median of 183), which is as long as the short message the gate asks for. Cutting a 5,000-character hand-back to 1,500 therefore cuts the PI's carried text to about half, not to a third, and nothing the lab controls shortens the frame.
refs: __reports__/wave-08/author-w08-2/pi_side.tsv (pi_chars minus hb_chars)

## S-w08-author-w08-2-8
Two things I could not keep clean. The first `e_on_auto` run gave a 3,380-character message (under N) and was overwritten by the rerun with a longer brief (14 files, 700 characters a paragraph); only the rerun is in the tables, so the tables hold no cell whose brief I changed after seeing the result besides that one. And a headless run with `--plugin-dir` of a plugin named `murmuration` shares its data folder name with the installed plugin (`~/.claude/plugins/data/`, which I did not touch); I did not check whether the cells wrote to it.
refs: __instrumenta__/w08_c2_live.py (PARA, the 14-file spec), __reports__/wave-08/author-w08-2/live_cells.tsv
