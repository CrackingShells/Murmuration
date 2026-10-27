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
    publish[Switchover, push, CI binaries, Nest]:::inprogress
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `publish.md` | 📄 Leaf Task | 🔄 In Progress |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
| `publish.md` | `main` (coordinator) | b7f455d, 485d339 | Step 1 done 2026-10-28 on the user's "Start switchover": gitignored local marketplace source set to `./plugins/murmuration` (backup in the session scratchpad), `release/claude-code` merged into local `main` (485d339, not pushed), `claude plugin marketplace update murmuration-local` passed, `claude plugin list` reads the new path; stale ignored root `scripts/__pycache__` removed. Next: restart, then go-ahead #2 asked in the fresh session |
