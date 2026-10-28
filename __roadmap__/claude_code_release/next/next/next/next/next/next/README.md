# First real project

## Context
Amendment A1, level 6: the scaffold in daily use, in one of Eliott's own projects, chosen with him.

## Goal
One real project runs as a lab from `murmuration@cracking-shells` at project scope.

## Pre-conditions
- [x] 0.1.1 installed from Nest (`ship_update`, 72a61d0)

## Success Gates
- ✅ `first_project.md` gates pass

## Status
```mermaid
graph TD
    first_project[First real project as a lab]:::inprogress
    posix_gaps[Close the remaining posix guard gaps]:::inprogress
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `first_project.md` | 📄 Leaf Task | 🔄 In Progress |
| `posix_gaps.md` | 📄 Leaf Task | 🔄 In Progress |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A1 | 2026-10-29 | reminder `murmuration-posix-gaps` (Murmuration list), with the publish session's corrections | `posix_gaps.md` | The posix bypass gaps left after posix_redirects (fd6088d), both guards agreeing, recorded in the campaign Gotchas; Eliott scheduled them as 0.1.2, before the Windows guard work that edits the same files |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
