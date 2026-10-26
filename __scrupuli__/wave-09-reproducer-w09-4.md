## S-w09-reproducer-w09-4-1
In the author's 45-case re-run the 15 refusals reproduce at exactly 0.0 score difference while 29 of 30 allows differ (max 0.84). The stored run cached 18,283 tokens for allows against 18,274 in the fresh run, but the very first refusal (stored 251 new tokens, fresh 18,525, cold) also differs by exactly 0.0, so cached length alone does not explain it. Why the allow side only?
refs: __reports__/wave-09/author-w09-4/spot_qwen_full.jsonl, __reports__/wave-09/explorer-w09-i/results/qwen36_full.jsonl, __instrumenta__/w09c8v_spot.py

## S-w09-reproducer-w09-4-2
Share of blocks that are refusals ranges 1 in 60 (10% point), 1 in 113 (own verdict), 1 in 160 (23 allow-era refusals). The 67 refusals span 4 months and the 19,243 allows 17 days, so no ratio is well defined; the arena allows (11,420 more) and subagent share (77% of weight) are also outside it.
refs: __instrumenta__/w09c8v_auc.py output; __pondus__/w09-c7.md

## S-w09-reproducer-w09-4-3
Gemma has 6 and 9 infinite scores, yet its weighted AUC is computed with inf ordering; the comparison qwen minus gemma short (-0.038 to +0.091) leans on that ordering.
refs: __instrumenta__/w09c8v_spot.py output
