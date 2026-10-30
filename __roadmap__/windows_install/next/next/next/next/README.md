# Release

## Context
Behind Eliott's go-aheads: PR-B merges, CI commits the binaries for 5 targets and then cuts 0.3.0; macOS install from Nest. The live Windows session (A2) runs one level deeper.

## Goal
0.3.0, cut by CI and tested on Windows in CI only, installs from Nest.

## Pre-conditions
- [x] `install` and `release_lifecycle` done

## Success Gates
- ⬜ `release.md` gates pass

## Status
```mermaid
graph TD
    release[0.2.0 release with Windows support]:::done
    next[Live Windows session]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `release.md` | 📄 Leaf Task | ✅ Done |
| `next/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A2 | 2026-10-30 | `__reports__/windows_install/A2_lifecycle_and_live_split.md` | ["next/"] | The live Windows session moves after the release |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
| `release.md` | `main` | 43b5815 `build(bin)`, 70879e3 `chore(release)` (both by the bot) | Eliott merged PR-B (e0fc40c). Push run 41077273398 green, `install_smoke` ×3 OS; `bin/` holds 5 targets and `manifest.json`; tag `v0.3.0` at 70879e3, Release v0.3.0 notes "install the hook binary on Windows"; the bump touched only `plugin.json`; `manifest_matches.py` on `v0.3.0` passes (rust 7950233b90d9). Nest unchanged (c00093d). Installed from Nest in a scratch project on macOS: cache 0.3.0, `murmuration.exe` = CI's aarch64-apple-darwin binary (a35735d1…), its stamp present, no launcher; one `murmuration:explorer` Agent call wrote `harness.jsonl` lines and an LF hand-back; 0.2.0's `bin/murmuration` and `.verified` unchanged. KT note `__reports__/windows_install/kt_windows_install.md` |
