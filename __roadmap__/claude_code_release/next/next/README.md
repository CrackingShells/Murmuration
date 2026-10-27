# Integration

## Context
Runs after the four depth-1 siblings are merged. The coordinator checks the joints no single leaf owned and exercises the install path the way Nest will serve it, without touching the public repository.

## Goal
Evidence, before any public push, that the release branch installs by git-subdir and that its CI runs green.

## Pre-conditions
- [ ] All depth-1 siblings done

## Success Gates
- ✅ `integrate.md` gates pass

## Status
```mermaid
graph TD
    integrate[Integrate and probe the install path]:::planned
    next[Publish]:::planned
    windows_paths[Windows path semantics in both guards]:::done
    posix_redirects[Bash redirections the guard does not read]:::done
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `integrate.md` | 📄 Leaf Task | ⬜ Planned |
| `next/` | 📁 Directory | ⬜ Planned |
| `windows_paths.md` | 📄 Leaf Task | ✅ Done |
| `posix_redirects.md` | 📄 Leaf Task | ✅ Done |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A1 | 2026-10-27 | user, after the rust_portability verifier's finding | `windows_paths.md` | The Rust guard's path helpers are POSIX-only and the Python guard compares case-sensitively with a literal `/`; on Windows both would allow settings writes Windows resolves to the denied file. The user asked for a dedicated implementer. Runs beside `integrate`; must land before `publish`. |
| A2 | 2026-10-27 | user, after verify-windows-paths' finding F5 | `posix_redirects.md` | Both guards miss a Bash redirect onto a settings file when the target is quoted with a space or uses `>|`; this is on macOS and Linux, the shipping platforms. The user asked for an implementer and a verifier, landing before `publish`. |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
| `posix_redirects.md` | `task/posix-redirects` | 3 (99b7b0b, 2c6ff32, 6a50eff; merge fd6088d) | impl-posix-redirects; verify-posix-redirects PASS WITH FINDINGS. Deviations accepted: old regex kept and a quote-aware second pass added (replacing it would turn a deny into an allow); `>|` read whole only when a segment ends in `>`; bash quote removal hand-written (shlex cannot read `$'..'`). Verifier: 0 deny-to-allow over lists, payloads, holes, 22,201 recorded Bash commands and 15,000 fuzz commands; the only new deny among recorded calls is a heredoc whose prose names a settings path; Python vs Rust 0 differences over 34,000 commands, except NUL-after-`~` (Python denies, Rust allows; bash cannot receive NUL). Coordinator rerun on the merged tip: selftest (redirects 110 x 2), cargo test 19/19, gated sets equal, check_text_io clean, hook_selftest None |
| `windows_paths.md` | `task/windows-paths` | 5 (cf825a5..641c04e; merge a77b78b) | impl-windows-paths; verifier verify-windows-paths FAIL on two nt fail-opens new in the branch (a dots/spaces-only segment before `..`; the inert test stripping `.cmd/.bat/.com`), fixed in 641c04e with nt `CLAUDE_CONFIG_DIR` case-folding and `.ps1`, then PASS WITH FINDINGS. Coordinator rerun after rebase: selftest (106 x 2 flavours), cargo test 15/15, check_text_io clean, check_guard_equal gated sets equal, hook_selftest None. Verifier: posix 0 differences vs ef5a3b6 over 3,859 events; nt Python vs Rust 0 differences over 220k fuzz events. Residuals in campaign Gotchas. Not run on real Windows |
| `integrate.md` | `release/claude-code` (coordinator) | b78ac5d, bd3cd88 | Probe: git-subdir install from a bare clone took the binary path, both variables resolved, guard denies a01-a03 and a settings Write. CI dry run in private `LittleCoinCoin/murmuration-ci-scratch` (user's go-ahead #1): run 40480512648 at bd3cd88 had 4 Unix rows and assemble green, Windows red, install_smoke and commit_back skipped (implicit success() over all ancestors), fixed in b78ac5d; run 40481091474 at b78ac5d: 4 Unix rows, assemble, install_smoke (macos-15, ubuntu-22.04) green, commit_back skipped (not main), Windows red on `UnicodeDecodeError` cp1252 in check_guard_equal.py:307 (routed to windows_paths). The run-1 `bin-and-manifest` artefact holds exactly the 4 Unix targets with the right `file` types; its aarch64-apple-darwin binary gave `doubt()` None and installed with `.verified` on the coordinator's Mac. Open: live Bash call through the hook. Scratch repo deleted by the user, 2026-10-27 (`gh api` 404 afterwards). |
