# murmuration

## Context
Build roadmap for Murmuration, from the build reference [architecture v4](../../__reports__/genesis/11-architecture_v4.md). Planned one wave at a time: wave 1 (platform probes, instrument validation) is detailed; the `build/` nodes are amended from what wave 1 finds.

## Goal
Ship Murmuration as an installable Claude Code plugin whose pilot shows judgement-led exploration, independent hardening, and anomalies that reopen exploration.

## Pre-conditions
- [x] Architecture v4 approved by the PI (2026-10-18)
- [x] Local repository scaffolded under CrackingShells

## Success Gates
- ✅ A pilot study runs end to end on the plugin, and its knowledge-transfer report states spend by mode, scrupuli raised and followed, and verifier catches
- ✅ The puzzle-following replay of the genesis study is scored
- ✅ Nothing is published on GitHub or in Nest without the PI's explicit go-ahead

## Status
```mermaid
graph TD
    repository[Local repository scaffold]:::done
    platform_probes[Platform probes]:::planned
    instrument_validation[Instrument validation on the genesis study]:::planned
    build[Build]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `repository.md` | 📄 Leaf Task | ✅ Done |
| `platform_probes.md` | 📄 Leaf Task | ⬜ Planned |
| `instrument_validation.md` | 📄 Leaf Task | ⬜ Planned |
| `build/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
