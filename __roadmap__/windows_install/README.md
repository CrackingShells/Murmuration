# windows_install

## Context
The Windows cycle of Murmuration, after 0.1.1 shipped the 4 Unix binaries. CI already builds a Windows row, but installs stay deferred: hooks exec `python3` and the data path is `bin/murmuration`. One leaf per `murmuration-win-*` reminder (macOS Reminders, list Murmuration); depth follows each reminder's `after:`.

## Goal
`murmuration@cracking-shells` installs on Windows, released as 0.3.0.

## Pre-conditions
- [x] 0.1.1 on `origin/main` (72a61d0)

## Success Gates
- ⬜ Every leaf's gates pass; `release.md` closes the cycle with a knowledge-transfer note

## Gotchas
- **Hashed inputs.** `budget.py`, `handback.py`, `run_hook.py` and the Rust sources are hashed into `bin/manifest.json` (`build_manifest.SCRIPTS`, `RUST_FILES`). A change to any of them needs CI's `build(bin)` commit on `main` before a version bump.
- **Version numbers.** 0.1.1 is taken; the next guard change (reminder `murmuration-posix-gaps`) shipped as 0.1.2. Eliott, 2026-10-29: the guard's retirement ships as 0.2.0, since it removes a feature, and the Windows release moves to 0.3.0.
- **The guard is retired (A1).** Eliott, 2026-10-29: first "deprecate Python" once Windows is judged sound, then, after the `shell_gaps` round-3 verdict and the threat-model review, "Yes, retire it": the whole guard goes, not only its Python half (`retire_guard.md`). `if_probe`, `next/if_decision`, `next/shell_gaps` and `next/next/path_gaps` change or probe the guard, so they close as blocked when `retire_guard` is done. Eliott, the same day: every Python script that has a working Rust equivalent on macOS, Linux and Windows retires too, so `budget.py` and `handback.py` go once the Windows binary passes `hook_selftest` on Windows; until then they stay as the launcher's fallback.

## Status
```mermaid
graph TD
    ci_green[Windows CI row green]:::done
    if_probe[Probe hook if filters on Windows]:::blocked
    next[Decision and shell gaps]:::inprogress
    retire_guard[Retire the permission guard]:::inprogress
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `ci_green.md` | 📄 Leaf Task | ✅ Done |
| `if_probe.md` | 📄 Leaf Task | 🚫 Blocked |
| `next/` | 📁 Directory | 🔄 In Progress |
| `retire_guard.md` | 📄 Leaf Task | 🔄 In Progress |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A1 | 2026-10-29 | `__reports__/windows_install/A1_retire_guard.md` | ["retire_guard.md"] | The guard's Windows reading cannot converge; Claude Code's own settings cover the risk |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
