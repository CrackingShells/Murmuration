# P6 v0: a 1-hour prompt cache for authors (registered before any run)

registered: 2026-10-22, by research-pi, before author-w07-6 starts. Claim: w07-c7.

## The change (B against A)

- A = `agents/author.md` at the commit this protocol is committed in.
- B = A with `experimental:` / `cacheTtl: "1h"` in its frontmatter, nothing else. Only authors:
  explorer-w07-g's break-even (ESTIMATE, three waves) nets authors +USD 4.49 of 43.90 and loses on
  reproducers (−2.27) and explorers (−1.52), because a 1-hour write costs 4.0 against 2.5 per Mtok
  (Sonnet 5.5) and only authors wait long between requests (verifier exchanges, long runs)
  [source: `__reports__/wave-07/explorer-w07-g/ttl_breakeven.md`]. The key was found by reading the
  2.1.304 binary, below the env var and the setting in precedence, and is not tested.

## Ceiling and noise, before the rule (open item 27)

- The effect is binary per request: a request after a gap of 5–60 minutes either reads the cache or
  re-writes it. The usage records name the TTL of each write
  (`cache_creation.ephemeral_1h_input_tokens` against `ephemeral_5m_input_tokens`). So the metrics
  below are exact counts, with no timing noise.
- The money is an ESTIMATE over recorded authors; it is recomputed, not gated.

## Metrics and rule

Headless haiku sessions (Claude Code 2.1.304, `CLAUDE_CODE_SHELL=/bin/bash`, auto mode, exports of
A and B with agent files set to haiku), a main thread that dispatches one `murmuration:author`.

- **c1 (honoured):** in B, the author's cache writes are recorded as 1-hour writes in every request
  that writes; in A, as 5-minute writes. 2 sessions each.
- **c2 (it keeps the cache across a gap):** the author makes one tool call that waits 6–7 minutes
  (a bounded `until` loop inside one Bash call with an explicit timeout), then one more request. In
  B that request reads the prefix from cache (cache read at least 90% of the previous request's
  context); in A it re-writes it. 1 session each.
- **c3 (nothing else changes):** the B author's tools, request 0 size (within 300 tokens of A) and
  hand-back are the same as A's.
- **c4 (value, ESTIMATE):** the break-even recomputed on every author of waves 4–7 with the
  measured write prices of c1; reported, not gated.

**Landing:** c1–c3 pass and reproducer-w07-6 supports them. If c1 fails (the key is ignored for a
plugin agent), nothing lands and the claim says so; no setting or env var is changed, since those
are the user's.
