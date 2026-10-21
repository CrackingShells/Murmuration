# Wave 6, E3 v3: one unconditional Bash row (pre-registered)

Written by research-pi on 2026-10-21, after w06-c10 (E3 v2) passed its rule and after author-w06-5's
correction of the `$` share, before any v3 run. v0–v2 are not edited.

## Why v3

v2's cost metric (h3) was built on a premise that turned out wrong. A command with an unresolved `$`
matches every `if` row, and I took such commands to be 17.7% of Bash calls. That share pooled about
1,900 headless probe sessions. In the lab's own sessions it is **45.1% of 5,135 Bash calls**
(author-w06-5; reproducer-w06-5 got 45.5%; `__instrumenta__/w06c7_dollar_share.py`). So v2's
3 gated rows cost about 0.45 × 3 ≈ 1.35 guard starts per Bash call. One unconditional Bash row costs
exactly 1. It also sees what `if` strips: a leading `CLAUDE_CONFIG_DIR=`, redirect writes of
settings files, heredoc bodies. v0's unconditional arm denied the 7 v0 pass-throughs 7 of 7. If that
holds, v3 is cheaper and stronger than v2. v3 lands **only if it beats v2 on both counts**.
Otherwise v2 stands, subject to its verification.

## The v3 build

v2's script-path and settings-path Write/Edit rows are unchanged. The 3 Bash `if` rows are replaced
by one Bash row with no `if`, `onFailure: block`, `timeout: 10`. The guard reads the full command,
heredoc bodies included, and denies G1, G2 and Bash writes of settings files (G3), as the script
already parses them.

## Metrics and rule

| Metric | Pass when |
|:--|:--|
| k1 v2's cases | every v2 h1, h2, h4 and h6 case gives v2's outcome |
| k2 stronger | the 7 v0 pass-throughs (b-list `CLAUDE_CONFIG_DIR=` forms and `--setting-sources ""`; d01, d02, d09, d12, d13) and the heredoc bypass flags (k01, k02 of reproducer-w06-5) are denied, at least 8 of 9 |
| k3 cost | exactly 1 guard start per Bash call on v0's ordinary list and on the `$` commands; 0 on non-script Writes |
| k4 no false denial | 0 of v0's ordinary Bash commands denied; the mention-only commands are reported, not gated |
| k5 load | as v2's h5: 10 of 10 `$(...)` calls with five parallel sessions run, none blocked; median and max hook time reported, max under 10 s |

**Rule.** Land v3 instead of v2 if k1–k5 all pass. Otherwise land v2, if its verification supports it.
