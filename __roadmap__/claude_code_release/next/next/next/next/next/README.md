# Ship 0.1.1

## Context
Amendment A1, level 5: ships the level-4 changes as 0.1.1 and checks once the update path a user follows.

## Goal
An install of 0.1.0 from `cracking-shells` updates to 0.1.1 with the marketplace update and the plugin update.

## Pre-conditions
- [ ] Level 4 merged into `main`

## Success Gates
- ✅ `ship_update.md` gates pass

## Status
```mermaid
graph TD
    ship_update[Ship 0.1.1 and check the update path]:::planned
    next[First real project]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `ship_update.md` | 📄 Leaf Task | ⬜ Planned |
| `next/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
