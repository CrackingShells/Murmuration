---
type: findings
topic: reflective_run/w02/explorer-w02-b
author: explorer-w02-b
date: 2026-10-19
version: v0
decision-required: none
---

# Report names, skill listing, cache lifetime (findings v0)

Full report is the hand-back message. All runs: `claude -p --model haiku` 2.1.302 from a scratch folder outside the worktree, scratch plugin `w02b`, USD 0.2453 by `total_cost_usd` for 19 finished runs, plus the two long runs unfinished. Scripts and probe agents are in this folder.

| item | result | label |
|:--|:--|:--|
| `00-findings_v0.md`, `01-observation_v0.md`, `02-analysis_v0.md` by a subagent | written | MEASURED (w_pre1) |
| `FINDINGS.md`, `findings_v0.md` by a subagent | refused | MEASURED (w_pre1) |
| sonnet, explicit brief, `__reports__/arithmetic_facts/00-findings_v0.md` | written 2 of 2 | MEASURED (s1_1, s1_2) |
| skill from another plugin via `skills:` (qualified and short name), and via the Skill tool | all load | MEASURED |
| skill that is not installed | agent starts, skill silently absent | MEASURED (w_missing) |
| start context, with Skill tool / without | 16,999 / 5,885 tokens | MEASURED (A0, A1) |
| listing budget fraction 0.0005 | 9,364 chars, start 10,068 tokens | MEASURED (A4) |
| `--disable-slash-commands` | no listing, but also no preloaded skill | MEASURED (A2, A3) |
| subagent cache lifetime 1h by env var, setting, frontmatter, ENABLE_PROMPT_CACHING_1H | all four give 1h writes | MEASURED (ttl_*) |

Worst-fitting case: haiku with `skills: writing-reports` refused to write any report-named file (0 Write calls) on the strength of the platform's soft rule, though the hard rule would have allowed the digit-led names.
