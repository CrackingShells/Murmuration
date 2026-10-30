# Path gaps

## Context
After `shell_gaps`, because both edit `permission_guard.py` and `rust/`.

## Goal
The remaining Windows path forms are decided.

## Pre-conditions
- [x] `shell_gaps` closed as blocked (A1)

## Success Gates
- ⬜ `path_gaps.md` gates pass

## Status
```mermaid
graph TD
    path_gaps[8.3 short names and odd path forms]:::blocked
    next[Install]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `path_gaps.md` | 📄 Leaf Task | 🚫 Blocked |
| `next/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
