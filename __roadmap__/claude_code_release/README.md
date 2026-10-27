# claude_code_release

## Context
First public release of Murmuration as a Claude Code plugin, a pure-dev cycle (no waves, no claims) following the user's decisions of 2026-10-26/27: one repository with the plugin in `plugins/murmuration/` and the research record kept beside it; Claude Code only, stated in a README banner; conditional compilation for macOS, Linux and Windows with binaries built and committed by GitHub Actions, Windows installs deferred; listed in Nest only (`murmuration@cracking-shells`). Two later dev cycles take other harnesses. It replaces the publishing part of `__roadmap__/murmuration` (amendment A2 there).

## Reference Documents
- [R01 settings record](../../__design__/settings_record/README.md) — why `.claude/settings.local.json` is no longer tracked (Phase 0, on `main`, commits 86fa0ca and b28572b)

## Goal
`main` is on GitHub with CI-built binaries and `claude plugin install murmuration@cracking-shells` works on macOS and Linux.

## Pre-conditions
- [x] Remote `https://github.com/CrackingShells/Murmuration` exists, public and empty (`gh api`, 2026-10-26)
- [x] `.claude/settings.local.json` untracked on `main`, on-disk copy unchanged (`cmp` against the backup, 2026-10-27)
- [x] Integration branch `release/claude-code` in its own worktree; the coordinator's live session keeps reading the plugin from the `main` checkout's root until the switchover in `publish`

## Success Gates
- ✅ Each dispatched leaf passes its gates and an adversarial verifier's attacks
- ✅ The git-subdir probe install shows `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` resolved and the guard live
- ✅ `origin/main` holds a `build(bin)` commit by CI and `install_smoke` passed in that run
- ✅ `murmuration@cracking-shells` installs from Nest and the guard denies `pkill`
- ✅ Nothing is pushed to GitHub or Nest without the user's go-ahead (three: scratch CI repo, `main`, Nest)

## Gotchas
- `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` were verified only under `--plugin-dir` before this campaign; a missing `${CLAUDE_PLUGIN_DATA}/bin/murmuration` blocks every Bash call (guard rows use `onFailure: block`). `integrate` settles this with a git-subdir install from a bare clone.
- Once a hashed source changes (relocate step 3 already does, through `rust/Cargo.toml`), local `doubt()` reports "sources changed" and installs the Python launcher until CI's `build(bin)` lands. Correct, slower.
- The org's `check_plugin.py` is advisory here: it rejects exec-form `args`, `if`, `onFailure` and `PostToolBatch`, rules that exist for cross-harness portability, which this cycle does not claim.
- Version stays `0.1.0` under the new identity `murmuration@cracking-shells`. Bump `plugin.json` only after CI's `build(bin)` commit for the same sources is on `main`: a cached copy does not refresh under an unchanged version, and a bump ahead of the binaries ships the launcher.
- Research records (`probes/`, `validation/`, `__instrumenta__/`) cite root-relative paths such as `scripts/permission_guard.py@<commit>`. They are read at their commit and are not rewritten.
- Subagents: Grep and `grep -r` are blocked by the colgrep hook; use colgrep `index_build` on the worktree path, then `search` with that path. No mamba or uv on this machine: system `python3` 3.12 (stdlib, `-I`), cargo 1.99.

## Status
```mermaid
graph TD
    relocate_plugin[Relocate the plugin into plugins/murmuration]:::planned
    next[Portability, contracts, CI, docs]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `relocate_plugin.md` | 📄 Leaf Task | ⬜ Planned |
| `next/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
