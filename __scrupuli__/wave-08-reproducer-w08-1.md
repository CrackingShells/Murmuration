## S-w08-reproducer-w08-1-1
My paired saving for budget (12.1 to 12.9 ms wall, 9.6 ms no-lab; Python start 27 to 31 ms) is 2 to 5 ms above the author's table (7.4 to 12.0; no-lab 7.7) on a machine at lower load (2.4 vs 2.8 to 3.3). The author could not say why. Different timer (posix_spawn from Python vs the C bench), same `python3`? Not resolved.
refs: /private/tmp/murmuration-w08/reproducer-w08-1/pair1.jsonl, pair2.jsonl; __reports__/wave-08/author-w08-1/e3_budget_table.md

## S-w08-reproducer-w08-1-2
The live harness log of this wave shows `"mode": null` and `"source": "unknown"` on every real start record (5 and now 11), so the platform's SubagentStart seems to carry no permission_mode; the claim's replay builds events with a mode in most scenarios (None only in dispatch ones). My set used none/auto/default and found no difference, but no recorded platform payload was replayed by anyone.
refs: __statera__/harness.jsonl; __instrumenta__/w08_v1_wave8_replay.py

## S-w08-reproducer-w08-1-3
Real worker spend in this wave's transcripts stays under the first 50 percent threshold, so my real-event replay exercised almost no `note` lines; only seeded-state scenarios of the author reach them. Equality at thresholds on real platform-written records rests on synthesized spend.
refs: /private/tmp/murmuration-w08/reproducer-w08-1/S2/run/*/lab/__statera__/harness.jsonl

## S-w08-reproducer-w08-1-4
The shipped binary is not bit-identical to a rebuild of the same sources on this machine (a9604f7f... vs 74fbbe31...), and the replay runs a different build (testclock). The link between replayed code and shipped bytes rests on the installer's self-test and the author's real-clock pass, not on identity.
refs: /private/tmp/murmuration-w08/reproducer-w08-1/Tship, bin/manifest.json
