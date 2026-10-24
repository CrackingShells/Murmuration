## S-w09-explorer-w09-a-1
The allow side of the classifier's decisions exists for only 16 days. `permissionDecision` is on 0 of 75,745 calls of versions before 2.1.293 and on 40,594 of 40,845 calls from 2.1.293 (2026-10-08). Yet the 44 refusals before that date are recognisable by text. So the refusal set spans July to October and the allow set only 8 to 24 October; a rate such as "refusals per allow" is only valid inside the recorded era (23 refusals, 30,525 allows), and the pre-era refusals have no recorded-allow counterpart. Why was the field added in 2.1.293, and did the classifier run the same way before? Unknown.
refs: `__reports__/wave-09/explorer-w09-a/strata.md` (last section), `__reports__/wave-09/explorer-w09-a/tables_counts.md` (by month), `/private/tmp/murmuration-w09/explorer-w09-a/classified.jsonl`

## S-w09-explorer-w09-a-2
`permissionMode` is a poor marker of auto mode. 9,898 recorded classifier allows (32%) have neither a `permissionMode` nor an `auto_mode` attachment before them, 13 sit under "default", 287 under "plan". Headless and subagent sessions apparently do not carry the field, but a mid-session switch (Shift+Tab) that is not written until the next prompt would give the same picture. I could not tell the two apart.
refs: `__reports__/wave-09/explorer-w09-a/tables_counts.md` ("by permissionMode seen before the call"), `__instrumenta__/w09a_collect.py` (mode tracking)

## S-w09-explorer-w09-a-3
The refusal set is not a spread of attack types. 16 of 67 refusals are in the colgrep-mcp worktrees (13 on 2026-09-12 alone), 20 mention colgrep, 6 carry `COLGREP_BYPASS` (4 of them read-only searches), 32 say only "Blocked by classifier", and some look like ordinary read-only work (a `ps | grep` of a named process, an `sed` that masks an env file). A local model scored on this set measures agreement with one user's habits on a few days, with 41 sessions behind 67 refusals. I cannot tell from the records whether those were classifier errors or real dangers; only the user can.
refs: `/private/tmp/murmuration-w09/explorer-w09-a/refusals.jsonl`, `__reports__/wave-09/explorer-w09-a/tables_counts.md` (project table), `synthetic_adversarial_v0.json` cases S032, S066, S071

## S-w09-explorer-w09-a-4
The classifier's context is not in the transcripts. `serverClassifierContext` holds a git summary, the cwd and the platform, no prompt and no command; whether the classifier read the conversation, the system prompt or the user's rules cannot be seen. Every comparison with a local model that is given the preceding user prompt may be unfairly informed or unfairly starved, and the intent pairs of the adversarial draft (S029/S030, S060/S061, S004/S005) depend on exactly that.
refs: `__instrumenta__/w09a_collect.py` (`condense_ctx`), `/private/tmp/murmuration-w09/explorer-w09-a/refusals.jsonl` (field `classifier_ctx_recorded`)

## S-w09-explorer-w09-a-5
After a refusal the model often retries and passes: of 67 refusals, 15 were followed by a recorded classifier allow of the same tool in the next calls, 5 by another refusal, 34 by calls of older versions with no record. Those 15 pairs (a refusal and the rewrite that passed) are the closest thing to observed near-misses, and they show the classifier is path-dependent on wording. I did not read them against each other; a second pass could tell whether the rewrite changed the action or only its wording.
refs: `/private/tmp/murmuration-w09/explorer-w09-a/retry_pairs.jsonl`, `__instrumenta__/w09a_retry_pairs.py`
