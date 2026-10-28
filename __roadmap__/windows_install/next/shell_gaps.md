# cmd, PowerShell and script bypasses

**Goal**: The guard reads the Windows shell forms it misses today, Python and Rust together, still equal on every CI row.
**Pre-conditions**:
- [ ] `ci_green` done (the Windows row compares the two guards)
- [ ] reminder `murmuration-posix-gaps` done (it edits the same files)
**Success Gates**:
- ⬜ G2 sees through `cmd /c`, `powershell -c`, and `set` / `$env:` assignments
- ⬜ Windows builtins (`copy`, `move`, `Set-Content`, `Out-File` and the like) are read as writes to settings files
- ⬜ G4 covers `.ps1` / `.bat` / `.cmd` scripts; `claude.ps1.` with a trailing dot no longer passes G1
- ⬜ [run] `check_guard_equal.py` equal on every CI row, the Windows row included; an adversarial verifier's report
**References**: reminder `murmuration-win-shell-gaps`; `../claude_code_release/README.md` Gotchas, "Windows cycle"; merge a77b78b (windows_paths)

## Step 1: Implement in a worktree, then verify adversarially
**Goal**: Same method as posix_redirects.
**Implementation Logic**:
An implementer changes `scripts/permission_guard.py` and `rust/` together (the Windows reading is ntpath), adds fixture cases to `scripts/fixtures/guard_lists/windows_paths.json` or a new list; then an adversarial verifier.
**Deliverables**: `plugins/murmuration/scripts/permission_guard.py`, `plugins/murmuration/rust/src/guard.rs`, fixture list
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/check_guard_equal.py` (expected: PASS)
**Commit**: `fix(guard): read cmd, PowerShell and Windows script writes`
