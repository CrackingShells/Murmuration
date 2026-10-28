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
| `publish.md` | `main` (coordinator) | b7f455d, 485d339, 7509378 | Step 1 done 2026-10-28 on the user's "Start switchover": gitignored local marketplace source set to `./plugins/murmuration` (backup in the session scratchpad), `release/claude-code` merged into local `main` (485d339, not pushed), `claude plugin marketplace update murmuration-local` passed, `claude plugin list` reads the new path; stale ignored root `scripts/__pycache__` removed; the fresh session confirmed the new path, the Python launcher (sources changed), a01 denied, `ls` allowed, and user_words written. Step 2 done 2026-10-28 on the user's "Yes, push main": `origin` added, `main` pushed (8e80df5); the push started no run (the `paths` filter did not fire on the first push to an empty repository), so on "Yes, dispatch it" run 40633506781 ran by hand with `commit_back=true`; CI committed 7509378 `build(bin)` (4 Unix binaries at 100755 plus the manifest), `install_smoke` green on macOS and Linux, Windows row red (`check_guard_equal.py` puts a backslash temp path into the fixture JSON; harness bug, not cp1252); local `main` fast-forwarded. Next: step 3 (scratch install from GitHub, then go-ahead #3 for Nest) waits for the user |
