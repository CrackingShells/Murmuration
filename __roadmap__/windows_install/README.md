# windows_install

## Context
The Windows cycle of Murmuration, after 0.1.1 shipped the 4 Unix binaries. CI already builds a Windows row, but installs stay deferred: hooks exec `python3` and the data path is `bin/murmuration`. One leaf per `murmuration-win-*` reminder (macOS Reminders, list Murmuration); depth follows each reminder's `after:`.

## Goal
`murmuration@cracking-shells` installs and guards on Windows, released as 0.2.0.

## Pre-conditions
- [x] 0.1.1 on `origin/main` (72a61d0)

## Success Gates
- ⬜ Every leaf's gates pass; `release.md` closes the cycle with a knowledge-transfer note

## Gotchas
- **Hashed inputs.** `permission_guard.py`, `budget.py`, `handback.py`, `run_hook.py` and the Rust sources are hashed into `bin/manifest.json` (`build_manifest.SCRIPTS`, `RUST_FILES`). A change to any of them needs CI's `build(bin)` commit on `main` before a version bump. `check_guard_equal.py` and the fixtures are not hashed.
- **`permission_guard.py --selftest` on Windows.** Its loader pastes the temp dir into the fixture JSON text (`.replace("{T}", T)`), like the harness did before `ci_green`. On Windows the backslashes are invalid escapes; the `except ValueError` reports the e3 lists as missing, so the selftest fails instead of crashing. CI never runs `--selftest`, so `ci_green` left it alone (a fix changes a hashed file). Fix it with the next leaf that edits `permission_guard.py` (`shell_gaps`), with `json.dumps(T)[1:-1]`.
- **Version numbers.** 0.1.1 is taken; the next guard change (reminder `murmuration-posix-gaps`) ships as 0.1.2, the Windows release as 0.2.0.

## Status
```mermaid
graph TD
    ci_green[Windows CI row green]:::done
    if_probe[Probe hook if filters on Windows]:::planned
    next[Decision and shell gaps]:::planned
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
| `if_probe.md` | 📄 Leaf Task | ⬜ Planned |
| `next/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
