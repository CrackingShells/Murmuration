# P2 v1: the origin rule from an async hook (registered after v0's results, before v1's runs)

registered: 2026-10-22, by research-pi, after author-w07-2's v0 results and saying so. Claim:
w07-c5 (a new mechanism, so a new claim; w07-c2 stands as v0's result).

## Why v1

v0 failed q2: the prompt's transcript record becomes readable only after the UserPromptSubmit hooks
exit (0.30–0.38 s after hook start with a 0.3 s poll, 10 of 10; 0.045–0.088 s after a hook that
returned at once, n = 2). A synchronous hook can never see its own prompt's record, and its poll is
0.3 s of wait added to every prompt for nothing [source: `__pondus__/w07-c2.md` on branch
`w07-p2-origin`, `__reports__/wave-07/author-w07-2/q2_live.txt`].

explorer-w07-c measured `async: true` command hooks: the loop does not wait for them, their start
costs 1–4 ms as the platform records it, and one still running when a `-p` session ends is
cancelled [source: `__reports__/wave-07/explorer-w07-c/00-findings_v0.md`].

## The change (B against main)

- `hooks/hooks.json`: the `user_words.py` row gains `"async": true`; nothing else in the file.
- `scripts/user_words.py`: v0's origin rule (branch `w07-p2-origin`, b2ab80d), with the poll
  raised to at most 3 s. A detached child of its own is not used: the platform owns the background
  process.

## Ceiling and noise, before the rule (open item 27)

- The record appeared 0.045–0.088 s after a fast hook exited (n = 2). A 3 s poll leaves a margin of
  about 30 times that. The shape of the wait is unknown beyond n = 2, so r2's threshold stays at
  8 of 10 rather than 10 of 10.
- A `-p` session's first model request takes seconds, so an async hook that needs 0.1 s finishes
  long before the session ends, unless the session ends at once.

## Metrics and rule

- **r1 (classification, offline, exact):** v0's q1, rerun on the v1 script: 0 errors.
- **r2 (live):** in 10 headless first prompts, the async hook finds the record and decides by
  origin in at least 8 of 10, and the entry it writes (or its drop) matches the rule.
- **r3 (no wait):** in 10 of 10 sessions the platform records the hook as async (it does not
  block the prompt); report the time from prompt to first API request for main and for B.
- **r4 (nothing lost):** in 10 of 10 sessions of r2, a prompt that the rule keeps is in
  `user_words.md` when the session has ended; two prompts in one resumed session appear once each,
  in order.
- **r5 (failure):** v0's q4 cases pass again under async; a crash of the script leaves the same
  visible trace as on main or less, stated as found.

**Landing:** r1–r5 pass and reproducer-w07-2 supports them. The entrypoint field stays as v0 found
it: a `claude -p` started from a Desktop session's Bash inherits `claude-desktop`, so the lab's own
headless probes are dropped like spawned sessions; a person's `-p` run from a terminal is kept.
