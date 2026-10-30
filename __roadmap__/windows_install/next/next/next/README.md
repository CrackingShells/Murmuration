# Install

## Context
After `retire_guard` (A1), which replaced `if_decision` and `path_gaps`. Two parallel leaves (A2): `install` makes the install path work on Windows as far as CI can show (PR-B), and `release_lifecycle` adopts writing-release v2.0.0 (PR-A). Both edit `guard-binaries.yml`, split by hunk: `release_lifecycle` owns `on`, `concurrency`, `needs`/`if` and new jobs; `install` owns the bodies of `build`, `assemble` and `install_smoke`.

## Goal
The install proven in CI on macOS, Linux and Windows, and releases cut by CI.

## Pre-conditions
- [x] `retire_guard` done (A1)

## Success Gates
- ✅ `install.md` and `release_lifecycle.md` gates pass

## Status
```mermaid
graph TD
    install[Install path and first Windows session]:::done
    next[Release]:::inprogress
    release_lifecycle[Adopt the writing-release lifecycle]:::done
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `install.md` | 📄 Leaf Task | ✅ Done |
| `next/` | 📁 Directory | 🔄 In Progress |
| `release_lifecycle.md` | 📄 Leaf Task | ✅ Done |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A2 | 2026-10-30 | `__reports__/windows_install/A2_lifecycle_and_live_split.md` | ["release_lifecycle.md"] | Releases cut by CI after a merge (writing-release v2.0.0), adopted before 0.3.0 |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
| `release_lifecycle.md` | `ci/release-lifecycle` | 3 (`.cz.toml`, `ci(release)`, `docs(contributing)`); merge 396a4cc | PR-A ([#1](https://github.com/CrackingShells/Murmuration/pull/1)) green; Eliott merged it as a merge commit with the PR title and body ("Merged and there was indeed only a merge commit with correct title and body"). Push run 41044928851 green: `build(bin)` 2e6fe7c by the bot, `release` printed "nothing to release since v0.2.0", only tag `v0.2.0`; the Release step created the missing v0.2.0 GitHub Release ("Let CI create it") |
| `install.md` | `task/win-install` | 3 (cb225fd `feat(install)`, 9c3dda6 `ci(install)`, a1bf47c `docs(readme)`); merge e0fc40c | PR-B ([#2](https://github.com/CrackingShells/Murmuration/pull/2)), stacked on PR-A. Three Windows smoke rounds: `SameFileError` on the `python3.exe` copy, Rust `lab_root` POSIX paths (`nt_*` helpers), CRLF from `os.open` without `O_BINARY`. Run 41046693211 green on 3 OS, `preview` printed "a merge would release v0.3.0". Verifier round 4: no blockers; hardening deferred to 0.3.1 (side-session note `win-hardening-0.3.1.md`) |
