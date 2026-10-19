## S-w01-reproducer-w01-11-1
A claim of "no reason to bring back" is a statement of absence, and the claim file gives no check that would find a reason: for SA1, SA7 and SA11 the facts concern other elements (hand-back hook cost, one author's own-head edit, async Stop). A stay-out verdict needs the row to say which failure that element addresses and where it was looked for. The claim's own closing section asks for this and the rows mostly do not give it.
refs: __pondus__/w01-c11.md rows SA1, SA7, SA11 and the section "What would differ if the claim were false"

## S-w01-reproducer-w01-11-2
`lab_status.py` prints c8 as "escalated: PI decides" while the PI's wave note says "used at MEASURED with that statement". A PI decision on an ESCALATE has no state in lab_status, so every downstream note must either say "escalated" or invent a label ("MEASURED by PI decision"). Should the loop have a recorded state for a decided escalation, written by the PI in the claim file (not the verifier's section)?
refs: python3 scripts/lab_status.py (w01-c8 line); __statera__/wave-01.md lines 82-87; __pondus__/w01-c11.md SA2, SA9

## S-w01-reproducer-w01-11-3
Explorer-w01-b §5 says lab-status parsed explorer-w01-e's puzzle file ("7 puzzles plus ## symbols") into 14 listed puzzles with no warning; the file lists 7 today and `## symbols` is not listed. Either the file changed, the parser changed, or the sentence is a typo. I could not tell which, and it is the only direct measurement of a parse in the explorer reports.
refs: __reports__/reflective_run/w01/explorer-w01-b/report.md line 153; __scrupuli__/wave-01-explorer-w01-e.md; python3 scripts/lab_status.py

## S-w01-reproducer-w01-11-4
The open-puzzle count differs between sources I read: 136 (c11 rows SA2, SA16), 142 open (lab_status now), 147 `## S-w01` headings across `__scrupuli__/`. The 5 difference may be puzzles lab_status skips (files without `S-` ids, or the `## symbols` header), or agents' files written since. Which count does the wave note take at close?
refs: python3 scripts/lab_status.py ("Open puzzles (142)"); grep -c "^## S-w01" __scrupuli__/wave-0*.md (sum 147)

## S-w01-reproducer-w01-11-5
A SendMessage to "main" from a verifier returns "queued for the main conversation's next turn", but nothing in my run shows whether a PI turn will happen before the verifier must close. For a CONJECTURE claim whose author is the PI, the exchange step may simply never complete. Is "no answer" the expected outcome whenever the PI is not between turns?
refs: __pondus__/w01-c11.md ### exchange

## S-w01-reproducer-w01-11-6
Update to -5: the PI's answers did arrive, but after I had appended my verdict, so the first exchange log said "no answer" and a second block had to be appended. A verifier that closes before the PI's next turn writes a false "no answer" into an append-only file. Should the loop say to wait for the PI's reply (or poll once) before the verdict line is written, or allow a "late answers" subsection?
refs: __pondus__/w01-c11.md (### exchange and ### exchange, late answers)

## S-w01-reproducer-w01-11-7
Each restatement round of the same CONJECTURE (c11, c12, c13) fixed what the verifier named and left one stale sentence elsewhere (c13's `scope:` still says "seven" for nine not-examined elements). Rewriting a whole table by hand under supersedes lets old wording drift in, and a verifier scoped to "the changes" does not read every line. Should a superseding claim list which sentences changed (a diff block), so the verifier can check changes against that list and not against the whole text?
refs: __pondus__/w01-c13.md (`scope:`, SA3 row); __pondus__/w01-c12.md

## S-w01-reproducer-w01-11-8
"Examined" was defined only after the first verdict: c11 and c12 counted an element as examined if any wave-1 fact was named in its row, which let SA1 and SA2 pass with "no fact bears on" in the same row. A count in a title is only as good as the criterion for the counted class. Should a claim that counts a class state the membership rule in `scope:` in its first filing?
refs: __pondus__/w01-c11.md (independent result, item 11); __pondus__/w01-c13.md (`scope:`)
