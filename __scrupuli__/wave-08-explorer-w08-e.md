## S-w08-explorer-w08-e-1
Idle compaction is documented as on by default (about 54 minutes after the last request, context over 200k, 1-hour cache), yet none of the six PI transcripts has a `Compacted while idle` line, and s3 (427k) and s5 (569k) each paid a USD 3.4-3.8 re-write after an over-one-hour pause. The sessions all carry entrypoint `claude-desktop`, which the docs exclude ("interactive terminal sessions"). I do not know whether that is the whole reason, or whether the feature flags it needs are off; and whether a Desktop-launched PI session honours `autoCompactWindow` / the environment variable at all is untested.
refs: `__reports__/wave-08/explorer-w08-e/tables.md` section 1 (last row); `__reports__/wave-08/explorer-w08-d/tables.md` section 4 (misses); transcripts `ab96c5ed`, `6b0e1f2a`, `f023f552`, `ad75be4f` entrypoint counts (script in the report's Pointers is not committed; the count is `entrypoint` of the first 400 rows).

## S-w08-explorer-w08-e-2
After a compaction the platform re-sends the whole preamble (skill listing 34.7k characters, deferred tools 28.6k, MCP instructions 8.9k, agents 8.2k): about 30k of the 40k tokens written. explorer-w08-d found the skill listing 22 times in s1 though s1 holds one compaction, so most of those 22 re-injections have another cause; nor do I know whether the preamble could be left out of the post-compaction write. The post-compaction context floor (91.5k for the PI) is mostly this preamble, and the break-even of every threshold depends on that floor.
refs: `__reports__/wave-08/explorer-w08-e/tables.md` section 3; `__instrumenta__/w08e_postcompact_items.py`; `__reports__/wave-08/explorer-w08-d/00-findings_v0.md` row "Skill listing" and "Steering questions" third bullet.

## S-w08-explorer-w08-e-3
The only evidence on what the PI loses is one event (s1 request 276) in which the next 12 requests grew by just 3.3k tokens above normal, so recovery reading looks near zero; yet my synthetic probe shows prose detail is lost (0 of 10 after compaction against 10 of 10 without) while codes and user facts survive (28 of 28). Both are true at once only if the PI needed nothing verbatim after request 276, or if it recovered later (request 289 jumps 11k after the pause). The net table is flat to R = 10k and halves by R = 45k, so this is where the estimate is weakest and I could not close it without an Opus-priced run of a PI-like task through a compaction.
refs: `__reports__/wave-08/explorer-w08-e/recovery_growth.txt`; `__reports__/wave-08/explorer-w08-e/net_estimate.md`; `__reports__/wave-08/explorer-w08-e/runs_analysis.md` (d1_plain, e1_control_nocompact); `/private/tmp/murmuration-w08/explorer-w08-e/runs/d1_plain/stream_detail.jsonl`.

## S-w08-explorer-w08-e-4
Three haiku sessions ended with "ok" right after a compaction (c1, c4, d2_precompact) and two never-compacted controls (e3, e3b) ended with "ok" after the first file, so I attribute it to the prompt, not the compaction. But the same prompt completed in five other compacted runs, so a rate of 3 of 8 against 2 of 2 cannot separate "compaction makes a model more likely to take the last instruction as finished" from chance. I did not repeat the controls enough to say.
refs: `/private/tmp/murmuration-w08/explorer-w08-e/runs/{c1_window100k,c4_codes_w200k,d2_precompact,e3_settings_key,e3b_settings_key}/stream.jsonl` (`jq` on `.result` of the `result` line).

## symbols
none new
