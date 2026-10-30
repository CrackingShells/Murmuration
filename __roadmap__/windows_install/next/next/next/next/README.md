# Release

## Context
Behind Eliott's go-aheads: PR-B merges, CI commits the binaries for 5 targets and then cuts 0.3.0; macOS install from Nest. The live Windows session (A2) runs one level deeper.

## Goal
0.3.0, cut by CI and tested on Windows in CI only, installs from Nest.

## Pre-conditions
- [ ] `install` and `release_lifecycle` done

## Success Gates
- ⬜ `release.md` gates pass

## Status
```mermaid
graph TD
    release[0.2.0 release with Windows support]:::planned
    next[Live Windows session]:::amendment
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `release.md` | 📄 Leaf Task | ⬜ Planned |
| `next/` | 📁 Directory | 🔵 Amendment |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A2 | 2026-10-30 | `__reports__/windows_install/A2_lifecycle_and_live_split.md` | ["next/"] | The live Windows session moves after the release |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
