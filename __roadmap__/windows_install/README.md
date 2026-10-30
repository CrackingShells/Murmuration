# windows_install

## Context
The Windows cycle of Murmuration, after 0.1.1 shipped the 4 Unix binaries. CI already builds a Windows row, but installs stay deferred: hooks exec `python3` and the data path is `bin/murmuration`. One leaf per `murmuration-win-*` reminder (macOS Reminders, list Murmuration); depth follows each reminder's `after:`.

## Goal
`murmuration@cracking-shells` installs on Windows as far as CI can show, released as 0.3.0 by CI; the live Windows session follows (`live_session`, A2).

## Pre-conditions
- [x] 0.1.1 on `origin/main` (72a61d0)

## Success Gates
- ⬜ Every leaf's gates pass; `release.md` closes the cycle with a knowledge-transfer note

## Gotchas
- **Hashed inputs.** `budget.py`, `handback.py`, `run_hook.py` and the Rust sources are hashed into `bin/manifest.json` (`build_manifest.SCRIPTS`, `RUST_FILES`). A change to any of them needs CI's `build(bin)` commit on `main` before a version bump.
- **Version numbers.** 0.1.1 is taken; the next guard change (reminder `murmuration-posix-gaps`) shipped as 0.1.2. Eliott, 2026-10-29: the guard's retirement ships as 0.2.0, since it removes a feature, and the Windows release moves to 0.3.0.
- **The guard is retired (A1).** Eliott, 2026-10-29: first "deprecate Python" once Windows is judged sound, then, after the `shell_gaps` round-3 verdict and the threat-model review, "Yes, retire it": the whole guard goes, not only its Python half (`retire_guard.md`). `if_probe`, `next/if_decision`, `next/shell_gaps` and `next/next/path_gaps` change or probe the guard, so they close as blocked when `retire_guard` is done. Eliott, the same day: every Python script that has a working Rust equivalent on macOS, Linux and Windows retires too, so `budget.py` and `handback.py` go once the Windows binary passes `hook_selftest` on Windows; until then they stay as the launcher's fallback.
- **One data folder for every installed version.** All projects share `~/.claude/plugins/data/murmuration-cracking-shells/bin/`, and each SessionStart installs its own version's binary there. A 0.1.x project's guard rows (`onFailure: "block"`) exec that binary with `guard`; the 0.2.0 binary answers with usage and exit 2, so a 0.1.x session that runs after a 0.2.0 session started blocks every Bash and settings-file write until it restarts. Update every project to 0.2.0 (`claude plugin update murmuration@cracking-shells --scope project` in its folder). Found 2026-10-30 at the 0.2.0 release check. From 0.3.0 the binary is `bin/murmuration.exe` with its own stamp `bin/murmuration.exe.verified` on every OS, so 0.3.0 and 0.2.0 no longer overwrite each other's files.
- **Windows needs a real `python3` on PATH (A2).** The three Python rows stay `python3 -S -I …` in exec form; a shim that found `python`/`py` cost about 70 ms per start on macOS and was rejected (Eliott, 2026-10-30). Microsoft Store Python provides `python3`; a python.org-only install does not.
- **Releases are cut by CI (A2).** From PR-A on, `plugin.json`'s version is written only by the `release` job of `guard-binaries.yml` after a merge to `main` (writing-release v2.0.0); no leaf bumps it by hand.

## Status
```mermaid
graph TD
    ci_green[Windows CI row green]:::done
    if_probe[Probe hook if filters on Windows]:::blocked
    next[Decision and shell gaps]:::inprogress
    retire_guard[Retire the permission guard]:::done
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
| `retire_guard.md` | 📄 Leaf Task | ✅ Done |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A1 | 2026-10-29 | `__reports__/windows_install/A1_retire_guard.md` | ["retire_guard.md"] | The guard's Windows reading cannot converge; Claude Code's own settings cover the risk |
| A2 | 2026-10-30 | `__reports__/windows_install/A2_lifecycle_and_live_split.md` | ["next/next/next/release_lifecycle.md", "next/next/next/next/next/", "next/next/next/next/next/live_session.md"] | Adopt writing-release v2.0.0; split the live Windows session out of `install` (no Windows machine this week) |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
| `retire_guard.md` | `win-shell-gaps` | 5 (0efcb00..d501344; merge a5eab49) | Probe on 2.1.304 (27 children, USD 0.09); Eliott set the key at user scope himself and closed the measurement. Guard code, fixtures, pre-commit hook and CI step removed (11,907 lines). Eliott's yes "Yes, merge and push" (2026-10-30): rebased onto local `main` (b30c773), `main` pushed 60d6efb..a5eab49; run 40901438091 green on 5 targets, `build(bin)` b421854, manifest hashes = merged sources. "Yes, release 0.2.0": 1f164ae pushed; Nest entry names no version, unchanged. Installed from Nest in a scratch project: cache 0.2.0, data binary = CI's aarch64-apple-darwin binary, a Bash `ls` and a Write ran with no Murmuration PreToolUse hook (the one `PreToolUse:Bash` was colgrep's), `murmuration guard` exits 2 with usage |
