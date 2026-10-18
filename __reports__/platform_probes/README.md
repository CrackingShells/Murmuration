# platform_probes

Reports from the platform-probe wave: what Claude Code actually delivers for each mechanism Murmuration's
architecture v4 relies on. Probe code and the exact runs are in `probes/` (`probes/run_probes.md`).

## Documents

### Round 00

| Document | Type | Latest |
|:--|:--|:--|
| [00-findings_v0.md](00-findings_v0.md) | findings (logged-out CLI: 14 of 25 mechanisms resolved) | no, superseded by 01 |

### Round 01

| Document | Type | Latest |
|:--|:--|:--|
| [01-findings_v1.md](01-findings_v1.md) | findings (CLI logged in: 27 of 28 mechanisms resolved; amendments for the build nodes) | yes |

`evidence/` holds the curated raw material the findings cite (hook inputs, debug-log excerpts, recorded system
prompts with and without the main-thread agent, the transcripts of the two messaging subagents, hand-back shapes).
`v1_*` files belong to round 01. The full logs are in `probes/out/`, which is gitignored.

## Status

- Claude Code 2.1.296. 23 mechanisms VERIFIED, 4 FAILED with a fallback that was itself run, 1 NOT TESTABLE HEADLESS
  (Agent Teams; the manual procedure is in v1).
- Minimum Claude Code version for the v4 hook set: 2.1.271 (documented floor; probes ran on 2.1.296 only).
- The amendments to `__roadmap__/murmuration/build/` are described in v1, not applied; the PI amends the roadmap.
