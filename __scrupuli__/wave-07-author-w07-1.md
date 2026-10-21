## S-w07-author-w07-1-1
Request 0 of identical-agent cells moved by up to 2,400 tokens (B2 20,355 against B3 22,739) and A4 against A1–A3 by 2,400, because the deferred tool list had 110, 129, 194, 203, 210 or 229 names from run to run (extra `mcp__arangodb__*` or `mcp__arxiv__*`). The registered noise (329 tokens over three identical baselines, explorer-w07-e) was measured on three cells that happened to have the same names. Which servers connect at launch is a machine state that the rule did not hold fixed; my pair 3 failed the 9,000 rule on it. Why do arangodb/arxiv connect in some headless sessions and not in others, and does the Desktop session have the same variation?
refs: __reports__/wave-07/author-w07-1/cells_table.md (deferred names column), cells/B2/summary.json, cells/B3/summary.json

## S-w07-author-w07-1-2
`dataviz` has no `SKILL.md` on disk: the Skill tool delivers it from the binary and extracts only `references/` and `scripts/` to `/private/tmp/claude-501/bundled-skills/2.1.304/<hash>/dataviz/`. A second `<hash>` folder (da704b91...) appeared during A_p5d beside the earlier one (af37090a...). What fixes the hash, and are other built-in skills (not seen in the 86-skill listing by name here) in the same state? Whether denying `Skill` loses only `dataviz` or more built-ins was not counted.
refs: cells/A_p5d/summary.json, cells/B_p5d/summary.json, cells/V1_p5d/summary.json; `ls -la /private/tmp/claude-501/bundled-skills/2.1.304/*/dataviz`

## S-w07-author-w07-1-3
In V1_p5d the PI said "a built-in skill with no SKILL.md on disk" after one `find` that returned nothing, and did not Read `research-loop` first; in v0, B_p5d read `research-loop` and ran three finds before giving up. The v1 sentence hands the PI a conclusion it did not check; for an installed skill with a typo or an unlisted path the same sentence could make it give up early. I did not test that case.
refs: cells/V1_p5d/summary.json (calls), cells/B_p5d/summary.json (calls)

## S-w07-author-w07-1-4
The first launch of B3 (8 sessions running concurrently) died with "Not logged in" (rc 1, no model request), the only such failure in 20 sessions. I reran it alone; the failure's summary was overwritten by the rerun (the cell folder is replaced), so only this note records it. Whether concurrency of 8 breaks the login check or it was a token refresh at that moment is not known.
refs: /private/tmp/murmuration-w07/author-w07-1/B3.out was overwritten; `__pondus__/w07-c1.md` method line

## S-w07-author-w07-1-5
B reads the 9,974-character `research-loop/SKILL.md` as a tool result in a session start, instead of the system-prompt/listing route. That moves about 2.5k tokens from request 0 to request 1 and onward (every later request re-reads the cache). The registered p3 counted model requests (3 and 3), not cached tokens in later requests, so the net saving over a session is smaller than request 0's 10.6k–11.9k and was not measured here.
refs: cells/B1/summary.json (reads), `wc -c skills/research-loop/SKILL.md`
