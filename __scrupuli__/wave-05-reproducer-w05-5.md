## S-w05-reproducer-w05-5-1
The parse cache stores the very dicts that `load_sessions` then merges into: `dict(msg, ...)` is shallow, so `merge_usage` writes the other file's larger usage into the first file's cached entry, and `save()` dumps it. Cached and uncached agree while both files are there, and differ after one leaves (5 005 against 15 output tokens). The real tree has no copies, so the m1 identity never tested this path. It makes me ask what else in `load_sessions` mutates what `read_transcript` returns.
refs: __instrumenta__/w05c5_repro_stale_probe.py (scenario S1), scripts/lab_status.py lines 644-683 and 584-593

## S-w05-reproducer-w05-5-2
"Frozen transcript tree" is not a frozen input: `lab_status.py` also reads the live lab (puzzle and wave files). My first timed run showed 40 of 80 outputs unequal to the reference from round 10 on, all four cases alike, because another agent wrote a puzzle file. Author's 16 784 bytes against my 20 913 and 20 974 are the same effect. Identity checks on a live lab need a within-round comparison or a lab copy; the claim's m1 does not say which.
refs: __reports__/wave-05/reproducer-w05-5/m2_runs_n20.jsonl (second run, within-round compare), /private/tmp/murmuration-w05/reproducer-w05-5/s/runs.jsonl (first run, the false alarm), __instrumenta__/w05c5_repro_m1_m2.py

## S-w05-reproducer-w05-5-3
The eight mutants of the selftest are claimed in prose only. My own 14 give 5 survivors (non-atomic write, no pruning, stamp after parse, write when nothing changed, tmp name without pid) and `os.rename` for `os.replace` passes on macOS. The one property E8 names (atomic writes) is not observable from a single-process selftest. What would a selftest of atomicity be, short of two processes?
refs: __instrumenta__/w05c5_repro_mutants.py output (rerun it with the new/ copy), /private/tmp/murmuration-w05/reproducer-w05-5/mut2/rename.py

## S-w05-reproducer-w05-5-4
A valid-JSON cache file with a malformed entry crashes `lab_status.py` on every run and is never repaired (the crash precedes the save). Truncated and empty files are fine. The probability is low (a partial write is not valid JSON), but the failure is permanent and the fix is one `try` around `read`.
refs: __instrumenta__/w05c5_repro_stale_probe.py (scenario S4, five DIFFERENT lines with rc 1)

## S-w05-reproducer-w05-5-5
Warm and cold differ by a factor of three, and a PI's usual call is a mix: the live session's transcript and any transcript another agent is writing reparse each time, the rest hit. I measured the frozen tree only, where nothing changes between runs; the author gives 27 ms for the largest file. I did not measure a run with the largest transcript reparsed every time (append in a loop), only after one append (SAME output; time 0.25 s total for one run).
refs: __reports__/wave-05/reproducer-w05-5/m2_runs_n20.jsonl

## S-w05-reproducer-w05-5-6
The fixes (9da5a47) came after the claim's measured build (4eb2272), and the claim head's headline numbers (1082 to 344 ms) still belong to the earlier build. A claim whose build moves during verification pins two builds; I re-measured the later one, but the head's m3 sentence ("eight mutants") counts a list that was replaced. Which build does the PI mean by "stays on the tip"?
refs: __pondus__/w05-c5.md (head, method), git show 9da5a47 --stat, __reports__/wave-05/reproducer-w05-5/m2_runs_fix_n12.jsonl
