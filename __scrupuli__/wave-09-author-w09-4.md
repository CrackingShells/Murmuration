## S-w09-author-w09-4-1
The same model, GGUF, llama-server build, prompt and temperature 0 gave scores that differ by up to 0.84 log-odds (sd 0.28) from the stored run on the 45-case subset, while all 45 verdicts held. The explorer's note says llama-server is deterministic here; verdicts are, scores are not. I did not isolate the cause (cache state, batch size, ordering of the cases). It makes the second digit of TPR at a fixed FPR noise (simulated 36 to 52% at sd 0.3).
refs: `__reports__/wave-09/author-w09-4/spotcheck.md`, `__reports__/wave-09/author-w09-4/spot_qwen_full.jsonl`, `__reports__/wave-09/author-w09-4/rescore.md` (section on score noise)

## S-w09-author-w09-4-2
The explorer's bootstrap lower bound (0.709) and mine with the same recipe and seed (0.717) differ because the session order of the cluster list differs (rows order versus cases order). A 0.01 swing from list order at 500 draws is small, but it shows the interval is not seed-free at that precision; I report 0.71 to 0.86.
refs: `__reports__/wave-09/explorer-w09-i/an_qwen.md` line "AUC refusals vs natural allows", `__reports__/wave-09/author-w09-4/rescore.md` first section

## S-w09-author-w09-4-3
qwen full is much weaker on the natural allows flagged risky (AUC 0.635, 80 cases, 24% of weight) than on plain ones (0.836). The "risky" flag was built by explorer-w09-c for sampling; I did not inspect what it flags. The claim's operating points mix both; the refusals look most like the risky allows, which is the hard region, and the answer to "usable recorder" may live there.
refs: `__reports__/wave-09/author-w09-4/rescore.md` (weight sensitivity), `__reports__/wave-09/explorer-w09-i/slices.md`

## S-w09-author-w09-4-4
The "share of blocks that are recorded refusals" (1 to 2%) pairs 67 refusals from July to October with 19,243 allows from 2026-10-08 to 2026-10-25. If only the 23 allow-label-era refusals belong to the allow window the share is 0.6%; if refusals missing from the record (the transcripts keep only what the user's sessions logged, and the first 44 refusals predate the allow label) were counted, it would be higher. I could not pin down the true refusal rate of the window from the artifacts.
refs: `__pondus__/w09-c8.md` (operating points), `__pondus__/w09-c7.md` (windows)

## S-w09-author-w09-4-5
In 11.5% of qwen full rows the top-20 first-token mass for BLOCK-like plus ALLOW-like tokens is below 0.99 (minimum 0.949), while the short criterion has none below 0.99. The score ignores the remaining mass; I did not look at which tokens hold it (a leading space, a different casing, or a quoted word would each be an unmatched token).
refs: `__reports__/wave-09/author-w09-4/rescore.md` (probability mass line)
