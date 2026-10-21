# Hand judgment of the batching heuristic (explorer-w07-b)

Question per pair: could the second turn's calls have gone out in the same message as the first turn's, i.e. did their inputs not depend on the first turn's result? Y = yes, N = no, M = unclear (a line range or file that may have come from the earlier result). I read both turns' commands in `merge_audit_sample.txt` and `merge_audit_strict_sample.txt` (commands scrubbed of long identifiers).

## Sample 1: 30 pairs from the loose list, seed 7, drawn before the two structural rules were added (deferred-tool loading, near-copy refinement)

merge_audit_sample.txt order. Y 16, M 3, N 11.
- Y: author-w04-2 t5, author-w04-2 t58, author-w04-3 t30, author-w04-4 t3 (two Reads), reproducer-w04-7 t8, reproducer-w05-1 t7 (ToolSearch for a known name), reproducer-w05-3 t14, reproducer-w05-3 t25, reproducer-w06-2 t10, reproducer-w06-4 t26, reproducer-w06-7 t3, author-w06-3 t5 (two ToolSearch), reproducer-w06-6 t6, reproducer-w06-6 t8, author-w06-4 t5, author-w06-5 t14 (two Writes, distinct files).
- M: reproducer-w04-4 t3, reproducer-w05-6 t2, author-w06-3 t27.
- N: reproducer-w04-2 t4 (ls, then cat of a file the listing showed), reproducer-w04-4 t2 (grep -n, then sed with its line numbers), author-w04-3 t59 (same), reproducer-w04-7 t9 (ls, then a loop over names it showed), explorer-w05-b t24 and reproducer-w05-1 t8 and explorer-w05-c t48 (call to a deferred tool before its ToolSearch loaded it: structural, now excluded by rule), reproducer-w05-3 t24 (a corrected re-run of the previous command), reproducer-w05-6 t14 (loop over names ls | grep printed), reproducer-w06-4 t12, reproducer-w06-7 t8 (refinement of the previous command).
- Precision of that list: 16/30 = 53% (Y only), 19/30 = 63% (M counted as Y). Three of the 11 N are removed by the deferred-tool rule, two more by the near-copy rule probably.

## Sample 2: 32 pairs from the strict list (after the rules), seed 11

merge_audit_strict_sample.txt order. Y 20, M 5, N 7.
- N: author-w04-3 t31 (PIDs taken from the previous ps output), author-w04-3 t59 (sed line range from the previous grep -n), author-w05-3 t16 (sed 60,248 where 248 came from a wc -l of the batch), reproducer-w05-3 t24 (corrected re-run), reproducer-w05-4 t4 (sed range from a grep '^## ' of the previous turn), reproducer-w06-7 t8 (refinement), author-w06-6 t170 (grep of a file that a grep -l just named).
- M: author-w04-2 t58, reproducer-w05-1 t2, explorer-w05-f t6, author-w06-6 t62, author-w06-3 t27 (sed line ranges that may come from an earlier grep).
- Precision of the strict list: 20/32 = 62.5% (Y only), 25/32 = 78% (M counted as Y).

## What stays unseen
A judgment from the commands alone cannot see whether the model needed to read the first result before deciding to issue the second call at all (a decision dependency); the heuristic cannot either. Both samples are one reader's judgment, n = 30 and 32; no second reader.
