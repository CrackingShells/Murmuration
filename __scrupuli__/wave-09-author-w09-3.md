## S-w09-author-w09-3-1
The explorer's headline allow-side figure for Granite (48.6% of allows refused) pools two different populations: the user's own sessions (natural, 19,243 allows) and the lab's own templated probe runs (arena, 11,420 allows, none of the 67 refusals come from them). On natural strata alone it is 59.8%; on arena 29.8%. The question was about the user's own sessions, so the pooled figure understates the disagreement there.
refs: __reports__/wave-09/author-w09-3/rescore.md (allow-side table); __reports__/wave-08/explorer-w09-a/00-findings_v0.md line 19, 60

## S-w09-author-w09-3-2
The refusal set and the allow set are from different eras: 44 of the 67 refusals precede the date when allow decisions were recorded (2026-10-08), so the allows are all recorded-era classifier-allows while two thirds of the refusals are not. On the 23 recorded-era refusals Granite misses 4 (17%) against 17 of 67 (25%) overall; safeguard misses 20 of 23 (87%) against 59 of 67 (88%). I did not find why the before-era refusals are easier for Granite (31 of 44 blocked, 70%, against 19 of 23, 83%, so in fact harder; the miss rate is higher before the era).
refs: __reports__/wave-09/author-w09-3/rescore.md (refusal-side table, columns "recorded era", "before era")

## S-w09-author-w09-3-3
gpt-oss-safeguard-20b at temperature 0 flipped one refusal from block to allow between the explorer's run and mine (11 of 12 repeated). The batched or reasoning path of LM Studio is not deterministic; the explorer ran one pass, so the 59-of-67 miss count carries a run-to-run noise it did not measure. Granite repeated 24 of 24.
refs: __reports__/wave-09/author-w09-3/spotcheck.md; private subset and outputs under /private/tmp/murmuration-w09/author-w09-3/

## S-w09-author-w09-3-4
The safeguard allow side has 45 cases in 28 of 53 strata, about 1 per stratum, so its stratum-weighted bootstrap interval (0.0 to 3.3%) is narrower than a raw Clopper-Pearson interval on 3 of 45 (1.4 to 18.3%). The weighted point (2.5%) lies below the raw rate (6.7%) because the blocked allows sit in low-weight strata. The bootstrap interval should not be read as 95% coverage here. The explorer's own report already says n is too small but still prints the 0.0 to 3.4% interval in the main table.
refs: __reports__/wave-09/explorer-w09-c/tables_all.md row 3; __reports__/wave-09/author-w09-3/rescore.md

## S-w09-author-w09-3-5
The report says "19 of 20 allow-labelled real calls of a 24-call probe blocked" under Granite's full rules. The smoke rows hold 19 real allow-labelled calls (7 under criterion A, 12 under criterion B) of which 18 are blocked, plus one synthetic allow-labelled call, blocked: 19 of 20 only if the synthetic one is counted. The word "real" is off by one; the substance (Granite under the full rules blocks nearly all allows) is unchanged. The two smoke files also use two different criterion wordings.
refs: __reports__/wave-09/explorer-w09-c/results/smoke_granite_full.jsonl, smoke_granite_full_b.jsonl; 00-findings_v0.md Result bullet 2

## S-w09-author-w09-3-6
First-call latency of safeguard was 3.7 s in the committed run but 28 s in my spot check (also a 20 s outlier among the 23 following calls), with machine load average 4 to 6 in both windows from another job. The steady p50 repeated (4.25 s against 4.57 s), but the tail depends on what else runs on this machine; the committed p90 of 8.2 s is not a bound.
refs: __reports__/wave-09/author-w09-3/spotcheck.md; /private/tmp/murmuration-w09/author-w09-3/spot_safeguard.res.jsonl

## S-w09-author-w09-3-7
"Allow" here means "classifier allow" only: calls auto mode allowed by mode accept (4,835), rule accept (2,722) or a hook never reached the classifier and are not in the 30,663. A local judge that blocks more of the classifier-allowed calls is compared on a population that already excludes the calls a rule waved through, so the allow-side disagreement is conditional on reaching the classifier.
refs: __reports__/wave-09/explorer-w09-c/tables_counts.md (decider totals)
