## S-w04-reproducer-w04-2-1
The protocol sizes the E1 task so that the work does not fit the budget. The E1 cells finish the whole 90-file table at 0.92 to 1.14 B in 9 of 12 runs (3 stopped short at 68 or 71 files). At that size the notes-on explorer has no reason to hand back without the report, so "0 of 6 denies" may follow from the size more than from the brief. The head's scope names "the pre-registered E1 task" but not that its size departs from the protocol text.
refs: __reports__/reflective_run/w04/00-experiment_protocol_v0.md (E1, Task); /private/tmp/murmuration-w04/author-w04-2/runs/{e1-a*,u-a*}/meta.json; derived/results_all_runs.tsv column frac_final, items_done

## S-w04-reproducer-w04-2-2
X differs from E1 in the brief (list in the hand-back vs report path), in size (150 vs 90 files) and in seeds. No cell varies one of these alone, so "the deny comes from the brief shape" and "the deny comes from work above the budget" cannot be told apart. The addendum v0 itself says "from briefs that said write the list ... and from tasks of 90 to 200 files".
refs: __instrumenta__/headless_explorer_cell.py lines 28-36 (brief report | list); derived/results_all_runs.tsv rows x-a*, u-a*

## S-w04-reproducer-w04-2-3
My log-based first hand-back fraction for the deny runs (last harness record before the deny: x-a1 0.756, x-a2 0.942, x-a3 0.887) differs from the author's transcript-based one (0.993, 1.067, 0.984; median 0.99). Final fractions agree. The two readings of "first hand-back" are not the same quantity; the claim's 0.99 holds only with the transcript pricing (the request that holds the call).
refs: /private/tmp/murmuration-w04/author-w04-2/runs/x-a1/lab/__statera__/harness.jsonl; derived/results_all_runs.tsv x-a1 frac_first

## S-w04-reproducer-w04-2-4
The capped XB cells ("0 of 3 with the line") have no uncapped repeat (budget ran out), and the full command does not run them. The decisive-looking contrast (3 of 3 vs 0 of 3) rests on cells with the platform's budget channel open (platform_budget_attachments 83 to 96 per run), the channel the author found to confound arm C. Uncapped XA still denied (2 of 2), so the deny does not depend on the channel, but the effect of the line is only seen with it.
refs: derived/results_all_runs.tsv rows x-b*, ux-a*; 01-addendum_v1.md

## S-w04-reproducer-w04-2-5
The uncapped XC cells (ux-c1, ux-c2) never handed back: 40 and 39 notes lines, 150 requests, 1.45 and 1.83 B, no report, no list. This is an exploratory side-result of w04-c3, but it also shows that the explorer file's report requirement does not hold when the notes are off and the brief names no report; the head of w04-c2 does not mention it.
refs: /private/tmp/murmuration-w04/author-w04-2/runs/ux-c1, ux-c2; derived/results_all_runs.tsv rows ux-c1, ux-c2
