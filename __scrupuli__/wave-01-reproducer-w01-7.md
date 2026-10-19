## S-w01-reproducer-w01-7-1
`explorer-w01-d/prompts.csv` caps `human_text` at about 420 characters while its `chars` column keeps the true length. Every claim that computed on `human_text` (word counts, overlap, token cost of reading the user-words file) is exposed; w01-c7 was off by a factor of 1.9 and lost the sentence it relied on. Which other claims of this wave read that column? Nothing in the CSV says the text is cut.
refs: __reports__/reflective_run/w01/explorer-w01-d/prompts.csv (19 of 55 research rows cut); __reports__/reflective_run/w01/reproducer-w01-7/fulltext.py

## S-w01-reproducer-w01-7-2
The replay counts a prompt as "avoided" when the answer to a removed ask is a one-click prompt. A click is not a typed instruction, and the human's attention cost is different (0.0 to 5 minutes against a typed paragraph). Is "prompts avoided of 55" the right unit for the human's attention, or should typed words be the unit? The author's own table shows 2 certain removals are both clicks.
refs: __reports__/reflective_run/w01/author-w01-6/c7_asks_replay.csv

## S-w01-reproducer-w01-7-3
Both asks with the long absences (6: 545 min; 17: 479 min) fall at 00:28 and 01:25 JST, the human's night. A habit that removes asks cannot recover these, but an agent that could work through the night on a stated default would; the replay cannot measure that because the PI had nothing in flight at either ask (17 of 19 asks had no subagent running). Is the lost time in the genesis and design sessions a property of the asking channel at all, or of the PI ending its turn with no queued work?
refs: __reports__/reflective_run/w01/reproducer-w01-7/timeline.py; __reports__/reflective_run/w01/explorer-w01-d/asks.csv

## S-w01-reproducer-w01-7-4
Rater agreement is high only after the author's retraction. The two raters share the same frame (the diff's own paragraph, the same CSVs). Ask 12 (repository name) and ask 0 (imbrex) are both KEEP although the human had delegated the coining to a skill and only the choice was open; a third rater might class them differently. Is a KEEP/REMOVE call on "taste" asks stable?
refs: __reports__/reflective_run/w01/reproducer-w01-7/wrapups.txt (the wrap_up inputs for all 19 asks)

## S-w01-reproducer-w01-7-5
The diff's section is a rule about when to ask, placed in working_defaults.md; v5 line 446 asks for a "when to decide what" test on every edit of PI prose. The author argues the existing ask-first rule in that file makes it the same kind. The test is stated for PI prose, and nothing says working_defaults.md is outside it. Who applies the test, and was it applied to this diff?
refs: __reports__/genesis/12-architecture_v5.md:446; skills/research-loop/references/working_defaults.md

## S-w01-reproducer-w01-7-6
Ask 2: the PI wrote "Nothing on disk can answer the family question yet" after checking only the Hugging Face cache; LM Studio held four more pairs. That is a false negative from an incomplete search stated as a fact, and it is a different failure from over-asking. Does the lab need a rule about stating "nothing is available" (what was searched)?
refs: __reports__/reflective_run/w01/reproducer-w01-7/wrapups.txt (566fa912 2026-10-18T07:25:51 and 07:35:35)
