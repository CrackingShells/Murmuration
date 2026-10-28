# First real project

## Context
Amendment A1, level 6: the scaffold in daily use, in one of Eliott's own projects, chosen with him.

## Goal
One real project runs as a lab from `murmuration@cracking-shells` at project scope.

## Pre-conditions
- [x] 0.1.1 installed from Nest (`ship_update`, 72a61d0)

## Success Gates
- ✅ `first_project.md` gates pass

## Status
```mermaid
graph TD
    first_project[First real project as a lab]:::inprogress
    posix_gaps[Close the remaining posix guard gaps]:::inprogress
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `first_project.md` | 📄 Leaf Task | 🔄 In Progress |
| `posix_gaps.md` | 📄 Leaf Task | 🔄 In Progress |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A1 | 2026-10-29 | reminder `murmuration-posix-gaps` (Murmuration list), with the publish session's corrections | `posix_gaps.md` | The posix bypass gaps left after posix_redirects (fd6088d), both guards agreeing, recorded in the campaign Gotchas; Eliott scheduled them as 0.1.2, before the Windows guard work that edits the same files |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
| `posix_gaps.md` | `task/posix-gaps` | 7 (d12238f..f69cfd1; merge 2d554c1 on `posix-gaps`) | impl-posix-gaps (Sonnet); verify-posix-gaps (Sonnet), four rounds: FAIL (length cap did not bound `[` runs or `cd a;` chains; `>|` skipped the new rules), then PASS WITH FINDINGS three times, signed off on f69cfd1. Per gap: `bash -c $'..'` and escaped substitutions closed; a shell fed by a pipe, here-string, `<`, `/dev/stdin` or process substitution denied when the command names a settings file; unknown, glob, variable and substitution targets denied when they name a settings file with its `.claude` folder (also from the cwd, `cd`/`pushd` state or `CLAUDE_CONFIG_DIR`); NUL in a command or path denied; Bash over MAX_CHARS 200000, Write/Edit over WRITE_MAX_CHARS 10,000,000, and work over WORK/CWD_MAX/CWD_WORK denied as too long or too complex. Worst time at the caps over 264 hostile forms: Python 1.37 s, Rust 0.47 s (posix). Verifier: 0 deny->allow against origin/main and against each round over about 100,000 forms; Python = Rust on all. Coordinator rerun on 2d554c1: selftest (posix_gaps 297 x 2), cargo test 22/22, gated sets equal, check_text_io clean. `--selftest` loader fixed for Windows. Residuals in campaign Gotchas. Release (step 3) waits for Eliott's yes |
