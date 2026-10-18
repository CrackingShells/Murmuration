# platform_probes

Reports from the platform-probe wave: what Claude Code actually delivers for each mechanism Murmuration's
architecture v4 relies on. Probe code and the exact runs are in `probes/` (`probes/run_probes.md`).

## Documents

### Round 00

| Document | Type | Latest |
|:--|:--|:--|
| [00-findings_v0.md](00-findings_v0.md) | findings | yes |

`evidence/` holds the curated raw material the findings cite (hook inputs, debug-log excerpts, the recorded system
prompts with and without the main-thread agent, the transcripts of the two messaging subagents). The full logs are
in `probes/out/`, which is gitignored.

## Status

- Claude Code 2.1.296. 14 of 25 mechanisms have a run-backed verdict (9 VERIFIED, 1 PARTLY VERIFIED, 4 FAILED with a fallback).
- 10 mechanisms are blocked on a model: the CLI is logged out. After `claude auth login`, run
  `probes/run_model_probes.sh` and `probes/analyze.sh <tag>`, then revise the findings as v1.
- 1 mechanism (Agent Teams) is NOT TESTABLE HEADLESS; the manual procedure is in the findings.
- The amendments to `__roadmap__/murmuration/build/` are described in the findings, not applied.
