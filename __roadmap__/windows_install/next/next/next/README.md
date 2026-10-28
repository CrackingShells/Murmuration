# Install

## Context
After `if_decision` and `path_gaps`: the install implements the decision and ships a guard that reads every Windows form.

## Goal
A Windows session observed end to end.

## Pre-conditions
- [ ] `if_decision` and `path_gaps` done

## Success Gates
- ⬜ `install.md` gates pass

## Status
```mermaid
graph TD
    install[Install path and first Windows session]:::planned
    next[Release]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `install.md` | 📄 Leaf Task | ⬜ Planned |
| `next/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
