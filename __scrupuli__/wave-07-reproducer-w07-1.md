## S-w07-reproducer-w07-1-1
The claim's statement line gives 10.6k-11.9k for request 0 "where the deferred tool names matched", but 11,828 (V1_1) and 11,378 (V1_3) come from pairs where B had fewer deferred names than A (194 and 203 against 229). The matched pairs give 10,620-10,952. The author agreed in the exchange but did not edit the statement line.
refs: /private/tmp/murmuration-w07/author-w07-1/wt/__reports__/wave-07/author-w07-1/cells_table.md (rows A4, V1_1, V1_3), __instrumenta__/w07c1_recheck.py

## S-w07-reproducer-w07-1-2
The claim body counts "13 B cells" without the Skill listing, but there are 14 (7 v0, 7 v1) in the runs folder, and 19 sessions in all. Tables and summaries list 14 B cells. This is a miscount only.
refs: /private/tmp/murmuration-w07/author-w07-1/runs/*/summary.json

## S-w07-reproducer-w07-1-3
Request 0 is not the session cost. B reads SKILL.md later, so whole-session input tokens in the 3-request p2 cells are A 109.5k-117.3k and B 73.6k-85.1k, a saving of about 25-35k, not 3 times 10.6k. Nothing in the claim says the saving per session is the request-0 drop times requests, but a synthesis quoting "10.6k lower" could be read that way. The cost over long sessions is outside the claim's scope.
refs: __instrumenta__/w07c1_recheck_totals.py (run on the runs folder)

## S-w07-reproducer-w07-1-4
The deferred name count is only valid when cut at the first assistant record. Counting the whole transcript gives 233-344 names, because MCP servers (arangodb, octopus-dev) connect after request 0. The cutoff is not stated in the claim head. A noise model for the registered p1 rule would need to include which MCP servers are up at launch, and the 9,000 margin did not.
refs: /private/tmp/murmuration-w07/author-w07-1/runs/A1 transcript, attachments at lines 9, 40, 53 (the first assistant record is at line 31)

## S-w07-reproducer-w07-1-5
`dataviz` is not on disk as SKILL.md, yet its references/ (7 .md files) and scripts/ are, in a hash folder under /private/tmp/claude-501/bundled-skills/2.1.304/. A new hash folder appears per session that calls the Skill tool (af37... on Oct 21, da70... during A_p5d). So whether a B PI could use the references without SKILL.md was not tested. The folder name changes per session, so the path is not stable.
refs: /private/tmp/claude-501/bundled-skills/2.1.304/*/dataviz/references/
