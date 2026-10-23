## S-w08-reproducer-w08-9-1
The proposed `restated at MEASURED` for w02-c7 and w02-c8 had no source line; the PI's own notes (wave-02.md:94-95, :230, synthesis.md:49,51) say "below MEASURED: restate; restated by PI decision". The table column "wave-note line" cited :230, which does not state a label. Who checks that a cited line says what the proposed state says, rather than that it names the claim? The tool only checks that the line names the claim id.
refs: __statera__/wave-02.md:94-95, __statera__/wave-02.md:230, __statera__/synthesis.md:49, __reports__/wave-08/author-w08-9/decisions_table.md (af1b33e)

## S-w08-reproducer-w08-9-2
For 7 of the 9 remaining escalations no wave-note line contains the label MEASURED; "restated in place" is read as "at the head label". w07-c7's head title still carries the wording its decision withdraws ("nets only slightly positive") and its label is compound (`MEASURED (c1-c3 ...); c4 is an ESTIMATE inside it`), shown flat as MEASURED. Is the head label the PI's decided label, or an inference by the author?
refs: __statera__/wave-07.md:363, __pondus__/w07-c7.md lines 1-4, __instrumenta__/w08_v9_apply_check.py output

## S-w08-reproducer-w08-9-3
Adding a stop at `## decision:` to the verdict-section parser changes how old files read: a line-start `## decision: research-pi` inside a code fence in a verdict section cuts the section, the `verdict:` line after it is lost, and the state becomes `unverified`. No real file triggers it (77 files identical), but a verifier quoting the rule in its exchange would. Also `superseded by <nonexistent id>` is applied. Neither is in the selftest or the mutations.
refs: __instrumenta__/w08_v9_cap_attacks.py cases "4d" and "7"

## S-w08-reproducer-w08-9-4
The permission guard (G2) blocked my first script because its text contained the name of a config-directory environment variable, though I only wanted to keep the status tool from scanning transcripts. I dropped it (claims do not depend on it) and was not hindered, but a helper that must isolate the user's transcripts from lab_status has no sanctioned way to do so.
refs: first attempt of __instrumenta__/w08_v9_apply_check.py (hook error text, G2)
