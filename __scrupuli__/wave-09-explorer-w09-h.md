## S-w09-explorer-w09-h-1
Three of the 14 escalation hand-backs reached the PI as queued attachments (`queued_command`), not as `user` peer records: w01-c5 (transcript `ab96c5ed` line 750, 02:37:35Z), w05-c1 (`6b0e1f2a` line 1421, 07:13:54Z), w08-c1 (`70daedf1` line 383, 16:19:25Z). `w09d_turns.py` opens no hand-back turn for them, so they are outside the 120 wakes and the 10 escalation wakes of w09-c4; one of them (w01-c5) is the only wake in which the PI opened the verdict section. The "0 of 10" is right for messages and wrong as "0 of all"; the raw-open rate by wake may also be affected (how many of the 120 are missing is not known).
refs: `__instrumenta__/w09h_find_mentions.py` on the three transcripts; `__instrumenta__/w09h_pi_after.py <transcript> 750|1421|383`; `__reports__/wave-09/explorer-w09-h/01-escalation_table.md` rows w01-c5, w05-c1, w08-c1

## S-w09-explorer-w09-h-2
In w01-c5 the PI read the verdict section 2 s after the hand-back with `awk '/^## verdict:/{p=1} p' __pondus__/w01-c5.md | cut -c1-500`: 87% of the characters, with 4 of the 15 lines of the exchange part cut at 500. A read that truncates exactly the long question and answer lines is a read of the headline, not of the exchange. Did the PI mean to skip them, or is `cut -c1-500` a habit for output size? It bears on whether "the PI read the file" is a yes/no variable at all.
refs: `__instrumenta__/w09h_pi_after.py <ab96c5ed> 750 40` (line 754); `__reports__/wave-09/explorer-w09-h/out/claim_at_verdict/w01-c5.md`

## S-w09-explorer-w09-h-3
w07-c7: the hand-back says the 1-hour result "holds only for the 6-tool, 12k-token headless author", "never tested a resume" and "sign not determined"; the PI's wake text says "it lands by its registered rule ... one line, reversible, and fails safe" and the branch is merged for the real author agent. The decision section written 2 days later narrows to the 6-tool headless author and says "kept by risk attitude, not by a measured gain". The information was in the notice and the decision still went first the other way, so a lever that adds the file would not have reached this case. Why did the registered rule decide it, when the hand-back said the rule's premise (the real author's configuration) was not run?
refs: `__reports__/wave-09/explorer-w09-h/out/wakes.json` (w07-c7); `__pondus__/w07-c7.md` decision section; `__statera__/wave-07.md:363`

## S-w09-explorer-w09-h-4
In 8 of the 9 decisions the PI wrote the restated wording "in place" at the wake (`restate the head in place`, w04-c4 T10) while `SKILL.md` says the author's head is never edited and the decision goes in a section. The 9 decision sections were all written 2 to 5 days later (82aa750: 4; dd8357f: 5), so for those days `lab_status` showed the claims as escalated while the wave notes said decided. Four heads differ from the verdict commit by 800 to 1,100 chars (w04-c4, w04-c7, w04-c10, w05-c1): the authors edited them after the wake. Is the wake decision the decision, or the decision section? The 5 supersede decisions have no section and need none.
refs: `git log -S'## decision: research-pi' -- __pondus__/<id>.md`; `__reports__/wave-09/explorer-w09-h/01-escalation_table.md`; `__pondus__/w08-c9.md` independent result (2, content)

## S-w09-explorer-w09-h-5
The verifier's section of w01-c2 says "4 of 156 other cells are inexact" (scope item 5) and its own independent result gives 78 exact and 2 inexact per binary, i.e. 4 of 160. The PI's wake text wrote 160. Which figure the decision section carries: 160 (`statement:` of w01-c2). A small case, but it is the one place where the PI's decision text is more right than the file it did not read.
refs: `__pondus__/w01-c2.md` verdict section items 1 and 5; `__statera__/wave-01.md:278`

## S-w09-explorer-w09-h-6
I could not test whether `additionalContext` returned by a synchronous `UserPromptSubmit` hook reaches the model when the prompt is a peer message or a queued attachment. The repo says the hook "fires per user prompt and per queued task notification" and `user_words.py` knows the peer origin (`DROP_KINDS`), but nothing in the records shows what the model sees of a hook's output on those prompts. If it does not reach the model, the PI-side lever fails and only the verifier-side gate (extend `gate()` to reproducer/proof-adversary) is left; that one depends on a once-only deny and on the verifier complying.
refs: `scripts/user_words.py:42,60`; `rust/src/handback.rs:331-362`; `rust/src/budget.rs:708`; `__reports__/wave-06/explorer-w06-b/00-findings_v0.md:36`
