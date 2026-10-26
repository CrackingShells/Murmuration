## S-w09-reproducer-w09-1-1
SubagentStart budget-hook duration depends on how many starts fall within 5 s (exec alone 142 ms n 13, with 3 or more 293.5 n 8; binary alone 106 n 3, with 3 or more 335 n 4). The explorer's "binary 282 vs exec 166" mixes batch sizes; nobody has a paired or stratified run of binary against exec at equal concurrency. Does the port help or not at SubagentStart? n = 3 alone says faster.
refs: __reports__/wave-09/reproducer-w09-1/startconc.txt, __instrumenta__/w09c1v_startconc.py, __reports__/wave-09/explorer-w09-f/hook_dur.md

## S-w09-reproducer-w09-1-2
M1's drop of 26,409 tokens is 1.7 times the 15,690 of w05-c7's headless experiment. The live PI tool list lost 29 tools (83,536 bytes), all matched by the denylist, none added: the mechanism is in the records, but the 10,700 tokens beyond the headless figure come from Desktop servers attached live that the smoke runs lacked (my reading, not tested). The author thinks M1's sessions 6b0e1f2a and 74fa512e are also w06-c1's pair; I did not open w06-c1.
refs: __reports__/wave-09/reproducer-w09-1/tooldiff.txt, __instrumenta__/w09c1v_tooldiff.py, __pondus__/w05-c7.md

## S-w09-reproducer-w09-1-3
"Ceiling" in USD: tokens x requests x cache-read price is neither a ceiling nor a floor (attribution biases it up, omitted writes and cold re-writes down). The 0.20/M and 0.10/M rates and the per-session list-price USD (23.08, 27.14, 26.02) I did not re-derive; whether Opus 5.5 reads at 0.20/M is taken from the explorer.
refs: __reports__/wave-09/explorer-w09-f/before_after.md, __instrumenta__/w09f_before_after.py

## S-w09-reproducer-w09-1-4
M5: "0 of 91 ended over budget" uses the hook's own spend estimate (output = max(recorded, chars/1.3)), not the platform's list price, and the budget in force after raises; 28 of 91 workers were raised, 1 of 28 over their original budget. Every dispatch has an end record, so the file shows no survivorship hole, but a worker killed before its Stop would leave a start and no end, and none exists here: 91 starts, 91 ends, exactly.
refs: __reports__/wave-09/reproducer-w09-1/harness.txt, __instrumenta__/w09c1v_harness.py

## S-w09-reproducer-w09-1-5
The head's title counts "four of explorer-w09-f's figures change when a resumed session, a resumed worker or a record is counted once". M2 (97 to 93) changes because four live explorers are excluded, not because of a resume. Wording only.
refs: __reports__/wave-09/reproducer-w09-1/workers.tsv, __pondus__/w09-c1.md
