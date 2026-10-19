## S-w01-reproducer-w01-6-1
`prompts.csv` caps `human_text` near 420 characters for 18 or 19 of its 55 research prompts, and nothing in the file says so. Every regex run by author-w01-6 on that column was run on truncated text. How many other explorer-w01-d numbers (the `>` quote counts, the CE classes, the "asks" tables) were derived from the capped column and not from the transcript?
refs: __reports__/reflective_run/w01/explorer-w01-d/prompts.csv (column human_text vs chars), __reports__/reflective_run/w01/reproducer-w01-6/full_text.py, full_text.json

## S-w01-reproducer-w01-6-2
The replay's unit is "a prompt the human sent", and the counterfactual changes the PI message that came before it. But a different earlier message could have changed which prompts the human sends at all, in either direction, including prompts that look like direction or insight (the N bucket). Rating a prompt "N, no wording changes it" assumes that the PI's earlier message is held fixed apart from its wording. Is there any way to test that without a live run?
refs: __reports__/reflective_run/w01/author-w01-6/c6_replay.py (HAND table), __pondus__/w01-c6.md

## S-w01-reproducer-w01-6-3
d10ebf86 shows a human who opened a report file because the chat gave no verdicts, and who then complained about the file. The remedy that worked in that session was a memory rule about report structure (`reports-state-hypotheses-and-verdicts.md`), not about the chat message. Murmuration's claim head already has statement, label and scope. Does the plugin have any rule about the structure of the files a person might open (framing, synthesis, wave note)? w01-c6 regulates only the chat close and a block in the wave note, so the case that started this claim would be untouched.
refs: ~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/memory/reports-state-hypotheses-and-verdicts.md, __reports__/reflective_run/w01/reproducer-w01-6/full.py (idx 1041-1080)

## S-w01-reproducer-w01-6-4
I rated these prompts after reading the author's HAND table, so my agreement figure (12 of 14) is not blind. A blind second rater would need to be given only the transcripts. If one more agent rated all 55 without seeing the table, how often would the Y/P set change? I sampled only 8 of the 49 N prompts; the 95% upper bound for a miss rate is about 31%.
refs: __reports__/reflective_run/w01/reproducer-w01-6/sample.txt, ctx.py

## S-w01-reproducer-w01-6-5
Is the ordering sentence ("question first, then findings, then what needs you") in waves.md step 4 a procedure the PI will follow, or just text in the skill? The only in-session evidence of a rule in context failing (S-w01-explorer-w01-d-1) is also the evidence the author cites against rating 3959fc84 P. If a rule about order can fail like that, what keeps the contract from failing the same way, and what in the lab would show it?
refs: __reports__/reflective_run/w01/author-w01-6/c6-contract.diff, __scrupuli__/wave-01-explorer-w01-d.md
