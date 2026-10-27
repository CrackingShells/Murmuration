# Integration

## Context
Runs after the four depth-1 siblings are merged. The coordinator checks the joints no single leaf owned and exercises the install path the way Nest will serve it, without touching the public repository.

## Goal
Evidence, before any public push, that the release branch installs by git-subdir and that its CI runs green.

## Pre-conditions
- [ ] All depth-1 siblings done

## Success Gates
- ✅ `integrate.md` gates pass

## Status
```mermaid
graph TD
    integrate[Integrate and probe the install path]:::planned
    next[Publish]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `integrate.md` | 📄 Leaf Task | ⬜ Planned |
| `next/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
