# Portability, contracts, CI, docs

## Context
Runs after `relocate_plugin`. Four siblings on disjoint trees run at once: `rust_portability` (`plugins/murmuration/rust/`), `targets_contract` (`plugins/murmuration/scripts/` incl. `git-hooks/`), `ci_workflow` (`.github/`), each dispatched to a Sonnet implementer with an adversarial Sonnet verifier; `readme_and_nest_prep` (`README.md`, `plugins/murmuration/README.md`, `plugin.json`, `../Nest`) by the coordinator. Their joint (CLI names, matrix vs targets, manifest keys) is checked in `next/integrate`.

## Goal
Portable crate, one target contract, a CI that owns `bin/`, and public-facing docs, each verified on its own.

## Pre-conditions
- [ ] `relocate_plugin` merged into `release/claude-code`

## Success Gates
- ✅ Each leaf's own Success Gates pass on its branch, then again after its rebase onto the `release/claude-code` tip
- ✅ Each dispatched leaf has a verifier verdict with no open finding, recorded in Progress

## Status
```mermaid
graph TD
    rust_portability[Rust portability by conditional compilation]:::planned
    targets_contract[One binary naming and target contract]:::planned
    ci_workflow[CI builds and commits the binaries]:::planned
    readme_and_nest_prep[READMEs and the Nest entry]:::planned
    next[Integration]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `rust_portability.md` | 📄 Leaf Task | ⬜ Planned |
| `targets_contract.md` | 📄 Leaf Task | ⬜ Planned |
| `ci_workflow.md` | 📄 Leaf Task | ⬜ Planned |
| `readme_and_nest_prep.md` | 📄 Leaf Task | ⬜ Planned |
| `next/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
