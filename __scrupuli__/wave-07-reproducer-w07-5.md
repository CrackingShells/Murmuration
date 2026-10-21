## S-w07-reproducer-w07-5-1
The committed binaries are not what a third party rebuilds: 47 bytes (aarch64) and 16 bytes (x86_64) differ, only LC_UUID and one code-signature page hash, and the LC_UUID changes with the output directory (the same source built into two target dirs differs too). So "bin/ equals rust/" cannot be checked by hash; it can only be checked by replaying decisions. Nothing on main does that (the pre-commit hook is not installed, the CI file is not pushed).
refs: /private/tmp/murmuration-w07/reproducer-w07-5/tgt, tgt2, tgt3 (three builds), /private/tmp/murmuration-w07/reproducer-w07-5/src/bin

## S-w07-reproducer-w07-5-2
The 121 registered cases did not catch a mutant that adds `echo` to the inert list (the guard then lets an echo of the bypass flags through); only the fuzz set did (10 of 1,500 events). A different mutant (`rm` removed from the writer list) was caught by one registered case. The registered set is thinner as a gate than "121 cases" suggests.
refs: /private/tmp/murmuration-w07/reproducer-w07-5/g1_mut1.log, g1_mut3.log

## S-w07-reproducer-w07-5-3
A single flipped byte inside the arm64 binary (offset 100,000) still ran and exited 0, whereas a truncated or appended copy is killed by the kernel (rc 137 / -9). So on macOS a corrupted guard is fail-closed only when the damage changes the size or a page that gets loaded; a flipped byte in used code could change decisions silently. The installer's sha256 compare repairs it at the next SessionStart only.
refs: /private/tmp/murmuration-w07/reproducer-w07-5/S/exp_C, S/runs_C.json, cc

## S-w07-reproducer-w07-5-4
The live lab guard blocked my own tool calls three times while I wrote tests that name the bypass words (a heredoc, a Write of a .py holding the flag as one literal, and later this very file). It works as a guardrail on me; it is also friction for any test author, who has to build the words from pieces. Side note: a heredoc whose body contained a line starting a second heredoc truncated my first helper file silently.
refs: __instrumenta__/w07c6_rv_crash_inputs.py

## S-w07-reproducer-w07-5-5
g4 on my machine gives a 15.8 ms median saving (6 pairs, load 3.0) against the claim's 23.5 ms (19 pairs, load 2.7); the first B call in pair 0 took 170 ms (first exec of a freshly copied binary). Same sign everywhere; the size depends on load.
refs: /private/tmp/murmuration-w07/reproducer-w07-5/S/runs/g4_rows.jsonl
