## S-w02-reproducer-w02-8-1
The B4 overshoot is explained in the claim title by "one request alone cost 0.55-0.81 B". The harness log shows the author's second request (the one that wrote the claim head) cost 0.0855 USD = 1.7 B. At USD 0.05 the deliverable alone is larger than the budget, so the overshoot is not a one-request accident. The hook's per-worker USD uses output = max(recorded, chars/1.3) while recorded output is about 5% of exact (B4: 417 recorded against 21949 exact for Sonnet), so every per-worker fraction is an estimate; the exact Sonnet total 0.3782 for two workers implies a mean near 3.8 B, above both reported fractions.
refs: /private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/expC/B4/lab/__statera__/harness.jsonl (stop and end lines for author-w01-1); __reports__/reflective_run/w02/explorer-w02-c/output_table.md (M1 token table, B4 rows)

## S-w02-reproducer-w02-8-2
The 0.8 note path (the one meant to make workers finish gracefully) fired in no arm: 0 notes in A..B4 against 4 stops. The "budget hook lands" decision therefore rests on the stop path only, with n = 2 and no run of B4 budgets without the hook. In B4 the deliverables were written after the first stop, but both workers were three to seven requests from done anyway; whether the stop changed anything is not measured.
refs: B4 harness.jsonl; B4 handbacks/*.md; output_table.md "Arm B4" section

## S-w02-reproducer-w02-8-3
B3 and B4 plugins are not identical to B2 although the protocol and claim call the later commits docs-only: scripts/lab_status.py (verdict logic changed in b396fd1), SKILL.md (first -> last `verdict:` line) and briefs.md differ. budget.py differs by one comment line. The PI and verifiers in B3 and B4 read the changed SKILL.md. I did not check whether that changed any worker behaviour; it probably did not, but "docs-only" is not accurate.
refs: diff -r of w02/expC/B2/plugin and w02/expC/B3/plugin; git show b396fd1

## S-w02-reproducer-w02-8-4
Text timestamps in the addenda disagree with commit times: B2 addendum "about 15:15 JST" but committed 15:40:28 (run start 15:40:49); B4 addendum "about 16:25 JST" but committed 16:21:32 (run start 16:21:46, run end about 16:27). The commits are the evidence and precede each run by 12-25 s, but each addendum was written after the previous arm's result was known, and B4 was designed so that a rule would fire.
refs: git log --format='%h %ci' -- __reports__/reflective_run/w02/00-experiment_protocol_v0.md; start.txt of each arm

## S-w02-reproducer-w02-8-5
A's missing synthesis is a ceiling effect (its PI ended its turn with "I'll write the synthesis when it returns", and the background wait ended after 603 s). B ran with the same default ceiling and finished because its PI kept 4 background shell tasks alive. The A-versus-candidate contrast in the title therefore measures PI polling behaviour, not the plugin, and the title does not say so.
refs: A/stderr.txt; A/stdout.jsonl last result event; output_table.md "Ceiling" section
