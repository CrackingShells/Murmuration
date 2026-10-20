## S-w04-reproducer-w04-6-1
Real colgrep 1.6.2 on an empty folder exits 0 and says `Index is up to date for <folder> (0 files)`, so nothing was built and no index exists, yet `describe_index` words it "was already there and up to date". Does colgrep keep an (empty) index record for such a folder? I did not check the store. The real `/lab` never meets it (it writes files first), so is the wording worth a fix or only a selftest line?
refs: /private/tmp/murmuration-w04/reproducer-w04-6/e1.err; scripts/lab_init.py lines 185-206

## S-w04-reproducer-w04-6-2
`build_index` is documented as never raising, but `text=True` plus non-UTF-8 colgrep output raises UnicodeDecodeError, a ValueError, and `main` then reports "settings.local.json is not a JSON object" with exit 3 after the lab folders were written. The wrong message hides the true cause. The same catch-all `except ValueError` in `main` would mislabel any ValueError from `run`. Is that clause too broad?
refs: /private/tmp/murmuration-w04/reproducer-w04-6/fake/colgrep; scripts/lab_init.py lines 209-222 and 592-602

## S-w04-reproducer-w04-6-3
The sentence added to briefs.md gives "one run in seven" for runs told "no claim file is needed". The source puzzle S-w03-author-w03-2-4 has 1 run told (skipped the file) and 6 not told (kept a file). The shipped text reads as a 1-in-7 rate among told runs; the data say 1 of 1 told versus 0 of 6 untold, a single run in the main thread, with the cause a conjecture. How did the denominator become seven in the claim head too?
refs: __scrupuli__/wave-03-author-w03-2.md lines 17-19; skills/research-loop/references/briefs.md lines 16-17

## S-w04-reproducer-w04-6-4
Parsing colgrep's stderr relies on exact English lines of colgrep 1.6.2; a lab-in-parent case is detected only by comparing the named folder to the lab. A colgrep update that changes the wording degrades to the fallback (colgrep's own words), which is safe, but nothing flags that the selftest's real-colgrep part would then fail only on the "built" assertions. Is the selftest failing on a colgrep upgrade the intended alarm, or a nuisance for `/lab` users who run `--selftest`?
refs: scripts/lab_init.py lines 392-407
