# P2 v0: `user_words.py` records only prompts a person typed (registered before any run)

registered: 2026-10-22, by research-pi, before author-w07-2 starts. Claim: w07-c2. Open item 28.

## The change

`scripts/user_words.py` looks up the transcript record of the prompt it is called for (the user
record whose `promptId` equals the payload's `prompt_id`, read from the transcript's tail, polling
for at most 0.3 s) and decides by the platform's own origin marker
[source: `__reports__/wave-07/explorer-w07-f/00-findings_v0.md`, rule section]:

- keep when `origin.kind` is `human` (typed prompts, `!` commands);
- drop when the record marks another session or the harness: `peer`, `task-notification`,
  `scheduled`, and a Desktop session's `sdk`-origin prompt (the first message of a session started
  by another session);
- keep an `sdk-cli` prompt (a headless `claude -p`). PI decision: a person may run a lab headless,
  and the lab's own headless probes run in throwaway labs under `/private/tmp`, where a recorded
  prompt does no harm. The author reports which fields tell a Desktop `sdk` prompt from an
  `sdk-cli` one; if none does, the rule keeps both and the claim says so.
- when no record is found in time, fall back to today's text rule (today's behaviour, no
  regression).

## Measured ceiling and noise, before the rule (open item 27)

- explorer-w07-f's offline check: the origin rule keeps 20 of 20 typed prompts and drops 476 of 476
  sdk-origin ones in the lab's transcripts. The offline metric is exact (a count over a fixed
  population), so its threshold is all-or-nothing.
- On-disk timing is not known: record creation preceded the hook's start by 0.2 s and 0.9 s
  (n = 2), flush time unmeasured (S-w07-explorer-w07-f-3). So q2's threshold is set low on purpose,
  and q2 decides effectiveness only, not safety: a miss falls back to today's rule.
- The hook runs once per prompt, not per tool call, so its cost matters only at the extremes.

## Metrics and rule

- **q1 (classification, offline, exact):** over every user record in the lab's recorded transcripts
  (both project folders explorer-w07-f read), the new decision function keeps every `human`-origin
  prompt and drops every `peer`, `task-notification`, `scheduled` and Desktop-`sdk` one, with 0
  errors; the `sdk-cli` decision follows the rule above.
- **q2 (the record is there in time, live):** in 10 headless sessions with a probe hook on
  UserPromptSubmit (a throwaway plugin, scratch labs), the record with the payload's `prompt_id` is
  found within 0.3 s in at least 8 of 10 first prompts. Report the distribution of the wait.
- **q3 (no regression):** the script's existing selftests pass; on recorded payloads the new script
  and main's give identical files except where q1's rule drops a prompt; its own wall time (measured
  inside the process, 20 runs) rises by at most 30 ms at the median and stays under 0.4 s at the
  maximum.
- **q4 (failure):** an unreadable transcript, a missing `prompt_id`, a malformed record and a
  transcript of 50 MB each fall back to the text rule without an exception, a hang or a lost prompt.

**Landing:** q1–q4 pass and reproducer-w07-2 supports them. `user_words.md`'s three known wrong
entries are not edited (no agent edits that file); the synthesis names them.

**Not covered, said now:** a live Desktop typed prompt and a live spawned-session message. The first
of each after the merge is the check.
