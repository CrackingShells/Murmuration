# 8.3 short names and odd path forms

**Goal**: Each Windows path form the guard does not read yet is denied, resolved, or accepted and recorded, by Win32's real behaviour.
**Pre-conditions**:
- [ ] Blocked by amendment A1, 2026-10-30: the permission guard this leaf changes or probes is retired (`../../retire_guard.md`)
- [ ] `shell_gaps` done (same files)
**Success Gates**:
- ⬜ 8.3 short names (`SETTIN~1.JSO`, `CLAUDE~1`) decided
- ⬜ the mixed reading of dots-and-spaces segments decided (probe on Windows where the docs are silent)
- ⬜ G4 applies the second reading, or the gap is recorded
- ⬜ [run] `check_guard_equal.py` equal on every CI row; an adversarial verifier's report
**References**: reminder `murmuration-win-path-gaps`; `../claude_code_release/README.md` Gotchas, verify-windows-paths residuals

## Step 1: Decide per form, implement, verify
**Goal**: Same method as the other guard leaves.
**Implementation Logic**:
Implementer in a worktree, Python and Rust together, fixtures, equality on every row, then an adversarial verifier.
**Deliverables**: `plugins/murmuration/scripts/permission_guard.py`, `plugins/murmuration/rust/src/guard.rs`, `scripts/fixtures/guard_lists/windows_paths.json`
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/check_guard_equal.py` (expected: PASS)
**Commit**: `fix(guard): read 8.3 short names and the remaining Windows path forms`
