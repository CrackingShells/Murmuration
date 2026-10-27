# Publish

## Context
Last step, by the coordinator with the user's go-aheads: switch the local session to the new layout, push `main`, let CI commit the binaries, then list the plugin in Nest.

## Goal
`murmuration@cracking-shells` installs from Nest with CI-built binaries.

## Pre-conditions
- [ ] `integrate` done

## Success Gates
- ✅ `publish.md` gates pass

## Status
```mermaid
graph TD
    publish[Switchover, push, CI binaries, Nest]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `publish.md` | 📄 Leaf Task | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
