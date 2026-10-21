## S-w04-reproducer-w04-4-1
Five near-fit runs are coded `extension_by_copy` (t2r3, st2r2, st2r3, and in arm X xt2r1, xt2r3) although the worker read only the first lines (`head -5`, `head -2`, `head -n1`) and wrote a plain loop that shares nothing with the existing script but the header comment and the `LIMIT` line. The table's "similarity 0.4 to 0.5" is mostly that shared header. The category "adapted by copy" cannot tell a copied body from a copied style. Is there a body-level test (shared lines beyond the first, or the `cache` loop) that would settle this before a decision is read from it? Only t2r1 and t2r2 reuse the cache loop.
refs: /private/tmp/murmuration-w04/author-w04-3/runs/t2r3/run.jsonl (calls 2 and 4), runs/st2r3 (call 4: header says "Plain loop, no cache, so it is independent of the memoised scripts"), runs/st2r2, `CODING` in __instrumenta__/e3_table.py; my reading in __pondus__/w04-c4.md

## S-w04-reproducer-w04-4-2
The task design is weaker than "near fit": the existing `collatz_longest_stopping_time.py` computes a different function (longest stopping time) from the task (highest peak). A worker that reads it properly may rightly decide that nothing fits and write new code. A "near fit" in the protocol's words is "with a small change". Only t3 (alphabet constant) is a small change, and there 3 of 3 adapted. So the t2 runs measure "did the worker look", not "did it extend". Should E3b use tasks where a one-line change turns an existing script into the answer?
refs: /private/tmp/murmuration-w04/author-w04-3/lab_scripts/collatz_longest_stopping_time.py, runs/t2r1/lab/__instrumenta__/collatz_highest_peak.py

## S-w04-reproducer-w04-4-3
The rule's thresholds (3 of 4) were written for n = 4 and applied to n = 15 by proportion; 11/15 (my loose reading) is 0.73 and 12/15 would be 0.80. The claim's verdict flips on one run. No decision should rest on this proportion at this n; the strict reading (7 of 15) is far from the line, which is the reason to state it first.
refs: __reports__/reflective_run/w04/00-experiment_protocol_v0.md (E3 rule, 10:10 addendum)

## S-w04-reproducer-w04-4-4
Every run's first Bash call lists `__instrumenta__` in the same call as `__design__`, `__pondus__`, `__scrupuli__` (20 of 21 in arms M, S, X) and the brief names none of them. The s1 metric credits the paragraph for the listing, and arm C (2 of 6) supports that, but a listing of every lab folder at start could also come from `framing.md` or the agent file's other lines naming those folders. Arm C removes only the paragraph; whether the lines naming `__pondus__` and `__scrupuli__` elsewhere in `agents/author.md` would still prompt the same first call was not tested. n = 6 per arm.
refs: runs/t1r1/run.jsonl call 1; runs/ct2r2/run.jsonl call 1; /private/tmp/murmuration-w04/author-w04-3/export-c/agents/author.md

## S-w04-reproducer-w04-4-5
The evidence is pinned at e1ed4fd but `__instrumenta__/e3_measure.py` is modified in the working tree (an additive s5/s6 block for E3b, per `git diff`), so a rerun of the claim's evidence at HEAD is not the pinned code. Harmless here (the quick run reproduced the numbers), but the claim's `evidence:` line no longer names the file that runs.
refs: git diff -- __instrumenta__/e3_measure.py
