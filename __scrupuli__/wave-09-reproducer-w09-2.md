## S-w09-reproducer-w09-2-1
The explorer's classifier drops the paths of any Bash command that contains the string "lab_status" and has no write. A PI call such as `cat __scrupuli__/wave-07-explorer-w07-d.md | cut -c1-600; sed -n ... report; grep -n ... scripts/lab_status.py` is coded as a lab_status call, not as a raw open. Five hand-backs of waves 5-8 are hidden this way (explorer 18 to 21, author 9 to 10, reproducer 5 to 6 on 121 hand-backs). Both the explorer and the author reran the same code, so a re-run cannot find it.
refs: __instrumenta__/w09d_turns.py (call_info, the `"lab_status" in c1` branch); __instrumenta__/w09c2v_labstatus_bug.py

## S-w09-reproducer-w09-2-2
The head says the PI opened the claim file "in an earlier turn" for w01-c2 and w06-c3. Both calls are checks that read no content: `ls __pondus__/w01-c2.md` and `grep -c . __pondus__/w06-c3.md`. By content the claim file was read before the decision for 0 of the 10 escalations, and the head's words "is a read, view or query command" hide the difference.
refs: transcript ab96c5ed line 1064; transcript 74fa512e line 680; __instrumenta__/w09c2v_escalation_open.py

## S-w09-reproducer-w09-2-3
Wake-level agreement between two codings that produce the same totals is lower than the totals suggest. Mine (R2, linked to the returning worker) and the author's (any artifact class) both give 33 raw opens in waves 5-8 by role, but agree on 106 of 121 wakes (kappa 0.70), with 15 disagreements in both directions. Equal totals are not equal sets of wakes.
refs: __instrumenta__/w09c2v_agreement.py; /private/tmp/murmuration-w09/reproducer-w09-2/out/wakes.jsonl (not committed)

## S-w09-reproducer-w09-2-4
The reproducer denominator of 41 in waves 5-8 holds 6 reproducer peer messages that are not hand-backs (questions or verdict notes sent by SendMessage). With hand-backs only it is 35, so 5/35 (14%) instead of 5/41 (12%).
refs: transcripts 6b0e1f2a, 74fa512e, 70daedf1 (peer records with origin.name reproducer-w05-8, w06-1, w06-2, w08-6, w08-5 and a body not starting "[Subagent hand-back]")

## S-w09-reproducer-w09-2-5
Four claim files carry an ESCALATE verdict (w01-c5, w01-c8, w05-c1, w08-c1) with no reproducer hand-back, task notice or peer message carrying it in the six PI transcripts. How did the PI learn of them? The reproducers' verdicts may have arrived through a message form the transcripts do not hold, which would also limit what any count of wake turns can say about them.
refs: __pondus__/w01-c5.md, w01-c8.md, w05-c1.md, w08-c1.md; my scan in /private/tmp/murmuration-w09/reproducer-w09-2/ (not committed)

## S-w09-reproducer-w09-2-6
My first extraction mis-split awk programs at the semicolons inside the quotes and read heredoc bodies as commands: it gave 18/10/5 for explorer/author/reproducer, the same as the author's, and the match was a coincidence of two errors in opposite directions. After fixing it I got 20/11/7. A matching headline total from two coders is weak evidence when the rules differ.
refs: __instrumenta__/w09c2v_extract.py (segs)
