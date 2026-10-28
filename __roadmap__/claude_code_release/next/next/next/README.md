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
    publish[Switchover, push, CI binaries, Nest]:::done
    local_cleanup[Local installs and worktrees cleanup]:::done
    next[PI choice and README]:::inprogress
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `publish.md` | 📄 Leaf Task | ✅ Done |
| `local_cleanup.md` | 📄 Leaf Task | ✅ Done |
| `next/` | 📁 Directory | 🔄 In Progress |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A1 | 2026-10-28 | side-session-notes/local_e5401f72-36a6-4b56-a47d-fcd5561cc982/plan-murmuration-publish-step3.md | ["local_cleanup.md", "next/lab_pi_choice.md", "next/readme_install.md", "next/next/ship_update.md", "next/next/next/first_project.md"] | Installable on macOS for many projects: project scope (no user scope), /lab stops setting agent, README install, 0.1.1 as the update-path check, cleanup of the local installs, a first real project; Eliott approved the plan 2026-10-28 |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
| `publish.md` | `main` (coordinator); Nest `main` | b7f455d, 485d339, 7509378, Nest 807bc81 | Step 1 done 2026-10-28 on the user's "Start switchover": gitignored local marketplace source set to `./plugins/murmuration` (backup in the session scratchpad), `release/claude-code` merged into local `main` (485d339, not pushed), `claude plugin marketplace update murmuration-local` passed, `claude plugin list` reads the new path; stale ignored root `scripts/__pycache__` removed; the fresh session confirmed the new path, the Python launcher (sources changed), a01 denied, `ls` allowed, and user_words written. Step 2 done 2026-10-28 on the user's "Yes, push main": `origin` added, `main` pushed (8e80df5); the push started no run (the `paths` filter did not fire on the first push to an empty repository), so on "Yes, dispatch it" run 40633506781 ran by hand with `commit_back=true`; CI committed 7509378 `build(bin)` (4 Unix binaries at 100755 plus the manifest), `install_smoke` green on macOS and Linux, Windows row red (`check_guard_equal.py` puts a backslash temp path into the fixture JSON; harness bug, not cp1252); local `main` fast-forwarded. Step 3 done 2026-10-28: GitHub git-subdir scratch install gave `.verified` + Mach-O; on Eliott's "Yes, push Nest" Nest `main` got 807bc81 (`--no-ff`); `murmuration@cracking-shells` 0.1.0 installed at project scope in a scratch folder, `.verified` + Mach-O, a01 denied, `ls` allowed, `/lab` created the lab files; cache holds the subtree only (3.6 MB) |
| `local_cleanup.md` | none (machine state) | (this record) | On Eliott's three selections: 7 local installs and 2 orphaned `/private/tmp` entries uninstalled, 13 merged worktrees removed (6 with `--force`), stale cache `murmuration-w5` and data `murmuration-inline` deleted; the main checkout's install and data dir kept |
