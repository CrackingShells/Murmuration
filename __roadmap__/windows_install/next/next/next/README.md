# Install

## Context
After `retire_guard` (A1), which replaced `if_decision` and `path_gaps`. Two parallel leaves (A2): `install` makes the install path work on Windows as far as CI can show (PR-B), and `release_lifecycle` adopts writing-release v2.0.0 (PR-A). Both edit `guard-binaries.yml`, split by hunk: `release_lifecycle` owns `on`, `concurrency`, `needs`/`if` and new jobs; `install` owns the bodies of `build`, `assemble` and `install_smoke`.

## Goal
The install proven in CI on macOS, Linux and Windows, and releases cut by CI.

## Pre-conditions
- [x] `retire_guard` done (A1)

## Success Gates
- ⬜ `install.md` and `release_lifecycle.md` gates pass

## Status
```mermaid
graph TD
    install[Install path and first Windows session]:::planned
    next[Release]:::planned
    release_lifecycle[Adopt the writing-release lifecycle]:::planned
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
| `release_lifecycle.md` | 📄 Leaf Task | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A2 | 2026-10-30 | `__reports__/windows_install/A2_lifecycle_and_live_split.md` | ["release_lifecycle.md"] | Releases cut by CI after a merge (writing-release v2.0.0), adopted before 0.3.0 |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
