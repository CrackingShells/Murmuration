# Decision and shell gaps

## Context
Runs after `ci_green` and `if_probe`: the decision needs the probe's report, the shell gaps need a Windows row that compares the two guards (and reminder `murmuration-posix-gaps`, which edits the same files).

## Goal
The `if` decision is recorded and the Windows shell bypasses are closed.

## Pre-conditions
- [ ] `ci_green` and `if_probe` done

## Success Gates
- ⬜ `if_decision.md` and `shell_gaps.md` gates pass

## Status
```mermaid
graph TD
    if_decision[Keep, widen or drop if]:::planned
    shell_gaps[cmd, PowerShell and script bypasses]:::inprogress
    next[Path gaps]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `if_decision.md` | 📄 Leaf Task | ⬜ Planned |
| `shell_gaps.md` | 📄 Leaf Task | 🔄 In Progress |
| `next/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
