## S-w06-reproducer-w06-3-1
The lead's request 0 differs by up to 2520 tokens between two runs of the same plugin and arm (ON 47685 vs OFF 45165 in my pair 1; the author saw clusters 46.4k and 46.85k). The same lead agent, cwd and prompt; the user's own MCP servers or deferred tool listing are my guess, not isolated. This makes the lead half of m3 ("0 tokens") unresolvable at token level in this environment, and the control (+22 tokens, same shape hash) cannot show an addition on the lead.
refs: /private/tmp/murmuration-w06/reproducer-w06-3/runs_extra/m3_on_1, /private/tmp/murmuration-w06/reproducer-w06-3/runs_extra/m3_off1; `python3 -I __instrumenta__/w06c3_verify_m3_request0.py -private-tmp-murmuration-w06-reproducer-w06-3-work <run dirs>`

## S-w06-reproducer-w06-3-2
Worker request 0 differs by up to 7 tokens between runs in the author's pairs (5938 to 5945) but was exactly equal in both of my pairs (5947/5947, 5949/5949) and equal inside every run. My cwd path is 4 characters longer (about +6 tokens), which fits a path-dependent component, but the author's within-arm spread has no such cause; I did not isolate it.
refs: /private/tmp/murmuration-w06/author-w06-3/runs/m3_on_1, m3_off0; /private/tmp/murmuration-w06/reproducer-w06-3/runs_quick/m3_on_0

## S-w06-reproducer-w06-3-3
m4 (a), the registered scenario, has no failure to show: the platform restarts a killed server and the next hook succeeds (m4a0 was even blocked by the restarted server). The rule asks for "a visible failure within 10 s", so for (a) it is satisfied vacuously and the real test of visibility is the added variant (b), whose only record is a transcript attachment that no script of the lab reads.
refs: /private/tmp/murmuration-w06/author-w06-3/runs/m4a0, m4b0 (session transcripts under ~/.claude/projects/-private-tmp-murmuration-w06-author-w06-3-work/)

## S-w06-reproducer-w06-3-4
After a hung restart a boundary waits 10.0 s (PostToolUse), 10.0 s (PostToolBatch), and the next ones 7.4 to 7.9 s; the 30 s connection timeout the author names does not explain 7.5. Not investigated.
refs: /private/tmp/murmuration-w06/reproducer-w06-3/runs_extra/m4c1, quick m4c0
