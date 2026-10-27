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
    rust_portability[Rust portability by conditional compilation]:::done
    targets_contract[One binary naming and target contract]:::done
    ci_workflow[CI builds and commits the binaries]:::done
    readme_and_nest_prep[READMEs and the Nest entry]:::done
    next[Integration]:::inprogress
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `rust_portability.md` | 📄 Leaf Task | ✅ Done |
| `targets_contract.md` | 📄 Leaf Task | ✅ Done |
| `ci_workflow.md` | 📄 Leaf Task | ✅ Done |
| `readme_and_nest_prep.md` | 📄 Leaf Task | ✅ Done |
| `next/` | 📁 Directory | 🔄 In Progress |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
| `rust_portability.md` | `task/rust-portability` | 2 (bc7403d, bd18970; merge 4c491ce) | Verifier PASS WITH FINDINGS: Unix differential 27,193 events + 30,591 timestamps, 0 differences. Open: `text.rs` path helpers are POSIX-only, so a Windows guard binary allows backslash settings paths (G3); deferred to the Windows cycle, see campaign Gotchas. Gate amended (python3 spawn, d80f356) |
| `targets_contract.md` | `task/targets-contract` | 6 (3c056eb..71d12cc; merge 30182ec) | Verifier PASS WITH FINDINGS; six findings fixed in 5b7c489, 71d12cc (hash allowlist incl. build.rs, .cargo/, nested src; bin/ strays refused; symlink refused; launcher survives a broken build_manifest). Known limit: a stale binary under a regenerated manifest is caught only on the self-test payloads |
| `ci_workflow.md` | `task/ci-workflow` | 4 (merge 48bff52) | Verifier PASS WITH FINDINGS; timeouts, mkdir, ALL_TARGETS tie and universal-binary refusal fixed in ebd4d4b. Deviations accepted and amended (d80f356): macos-15, commit_back on main dispatch. Not run on GitHub; `act` skipped (no docker daemon) |
| `readme_and_nest_prep.md` | `release/claude-code` (coordinator) | 3 (084bc5a, db28904, 888b18b) | Nest entry on `../Nest` `feat/list-murmuration` c00093d, not pushed |
