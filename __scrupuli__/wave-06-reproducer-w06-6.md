## S-w06-reproducer-w06-6-1
The microbench saving is 25 to 27 ms in my alternating `sh -c` loop (main 85, build 58, bare `python3 -S -I` 53.5) but 20 ms in the author's (81.2 against 61.2). The two differ by about 4 ms on each arm, in opposite directions, and I do not know why (pycache state, payload path, lab state). The PI's decision sits on a threshold of 25, so a 5 ms difference between two benches decides which side the saving lies.
refs: /private/tmp/murmuration-w06/reproducer-w06-6/bench_300k.txt, bench_more.txt; __reports__/wave-06/author-w06-6/floor_n40.jsonl, bench_worker_short_n40.jsonl

## S-w06-reproducer-w06-6-2
Platform-recorded pairs scatter by about 20 ms (differences -30 to 42 over 13 quiet pairs, median 23, 6 of 13 at 25 or more), so a rule that needs 25 ms "in every pair" is failed by noise in any set of pairs even when the true saving is 25. The rule could not have passed unless the saving were far above 25; the registered threshold was never testable at n of 3 to 9.
refs: __reports__/wave-06/author-w06-6/e2_all_pairs.txt; /private/tmp/murmuration-w06/reproducer-w06-6/runs/r_5..r_8_{main,new}/dbg.log

## S-w06-reproducer-w06-6-3
`loads` falls back to `json.loads(bytes)`, which accepts a UTF-8 BOM and UTF-16/32; the old arm read text and rejected them. Only the fallback differs (the C-scanner path decodes UTF-8 itself and rejects). Harmless for the platform's payloads, but "fallback gives identical outputs" is exact only for payloads without a BOM. Also, `loads` and `dumps` catch only ImportError: a `make_scanner` that raises any other error would make all 8 hook rows silent no-ops with exit 0 and no log (my mask E).
refs: /private/tmp/murmuration-w06/reproducer-w06-6/tools/w06c9_fuzz_json.py (masks A to D), cmd_maskE.txt

## S-w06-reproducer-w06-6-4
My first 4 headless pairs ran while my own replays loaded the machine (load 10 to 20): platform start medians 200 to 900 ms and differences 208, -118, 108, -150. The author's claim reports load 2 to 15 for its pairs and its early pair at load 15 gave 21 ms; I cannot tell from the debug files how much of the author's 5 loaded pairs (load 7 to 11) is noise rather than saving.
refs: /private/tmp/murmuration-w06/reproducer-w06-6/runs/r_1..r_4_*/dbg.log
