## S-w08-reproducer-w08-10-1
The registered list e3v2 denies 3 of 6 cases in my run of the author's registered_diff script (before = after), but registered_diff.txt and the claim say 2 of 6. I did not find why (arena or scratch path differences are my guess; not tested).
refs: /private/tmp/murmuration-w08/reproducer-w08-10/rd_scratch, __reports__/wave-08/author-w08-10/registered_diff.txt

## S-w08-reproducer-w08-10-2
`env -Sclaude -p hi <bypass flag>` is allowed while `env -Sclaude -p hi --bare` is denied on the branch. G1 should be text based; why does G1 pass the joined form? Only the claude word boundary is my guess.
refs: /private/tmp/murmuration-w08/reproducer-w08-10/ex.py, holes1.json (shape env_S_adj)

## S-w08-reproducer-w08-10-3
Baseline Python takes 17 s for `python3 -c write` + 30,000 characters (quadratic findall in g3_bash), over the 20 s hook timeout at ~35 KB, while Rust takes 0.04 s. The Python script is the fall-back whenever the binary is in doubt; nobody has registered this input class. Also `python3 -c x` + n chars: 16,000 chars -> 2.5 s.
refs: /private/tmp/murmuration-w08/reproducer-w08-10/lw.py, lw2.py, lw3.py, time1.log

## S-w08-reproducer-w08-10-4
The live guard (G4) refused my Write of a script containing a bypass flag string even though the brief told me to put such strings in files; JSON data files pass. Worth stating in the brief: flags go in .json, not scripts.
refs: __instrumenta__/w08_v10_flags.json

## S-w08-reproducer-w08-10-5
`bash -lc 'claude -p hi --bare'` is allowed on the baseline (plain form): the combined `-lc` is not read as `-c`. Not this claim's, not listed anywhere I saw.
refs: /private/tmp/murmuration-w08/reproducer-w08-10/ex.py output, holes1.json shape bash_lc

## S-w08-reproducer-w08-10-6
w08-c13 states the work cap bites at nesting depth about 3,200; I measure G? at 2.4 s already for `$(echo ` x 1700 (13.6 KB) and not at 1400, so the boundary depends on characters per level (about 10M scanned chars), not on a depth. Harmless but the sentence in the claim is loose.
refs: /private/tmp/murmuration-w08/reproducer-w08-10/sweep_13.py, c13/time.log

## S-w08-reproducer-w08-10-7
Branch commit b452702 (before 68ac4c1) carried the OLD binary: Python denied, Rust allowed 1,907 of my cases; the claim head named 6041223, then the branch was rebased twice. A reader who takes the "branch tip" at the wrong moment sees Python and Rust disagree. Landing needs the manifest check the installer already does.
refs: /private/tmp/murmuration-w08/reproducer-w08-10/c13/holes.log (first run overwritten), git log of w08-c10-guardholes
