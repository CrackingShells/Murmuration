# Close the remaining posix guard gaps

**Goal**: Each Mac/Linux bypass gap left open after posix_redirects (fd6088d) is closed, denied by default, or recorded as accepted with a reason, in both guards at once (`permission_guard.py`, the exact judge, and its Rust port), with no case that is denied today becoming allowed; shipped as 0.1.2.
**Pre-conditions**:
- [x] 0.1.1 is on `origin/main` with CI binaries for the 5 targets (c2fdb56, `build(bin)` for 680001f)
- [x] Reminder `murmuration-posix-gaps` (Murmuration list, id 7E22E7F2-CB95-495A-9AA6-F344FD2998A9) is the spec, corrected by the coordinator: the bump is 0.1.2, not 0.1.1
- [x] Work branch `posix-gaps` from `origin/main`, so a push does not carry the 5 docs commits on local `main` that are not approved for push
**Success Gates**:
- ✅ [run] For each of the five gaps below, the hand-back names the decision (close, deny by default, accept) and its reason; each closed or denied form has deny cases, and each nearby ordinary form an allow case, in a new list `scripts/fixtures/guard_lists/posix_gaps.json` (pinned count, fails if missing, run under both flavours by the selftest, the Rust tests and `check_guard_equal.py`)
- ✅ [run] No deny becomes an allow: old (origin/main) vs new Python, and old vs new binary, over every existing list, `guard_selftest_payloads.json`, `guard_selftest_holes.json`, under both flavours, give identical exit code and stdout except cases listed one by one, each an allow becoming a deny with a reason
- ✅ [run] `python3 -I plugins/murmuration/scripts/permission_guard.py --selftest` exits 0; `cargo test --manifest-path plugins/murmuration/rust/Cargo.toml` passes; `cargo check --release` is clean on the 5 targets
- ✅ [run] `check_guard_equal.py` prints "gated sets equal", quick and full, with Python vs Rust 0 differences on the new list and on fuzz over the new forms
- ✅ [review] An independent adversarial verifier attacks each gap and signs off
- ⬜ [run] After CI's `build(bin)` for the merged sources is on `main` (5 targets), `plugin.json` is 0.1.2; `murmuration@cracking-shells` installed from Nest denies fixture attack `a01` and allows `ls`
**References**: campaign README Gotchas ("Guard gaps found by verify-windows-paths", posix residuals after fd6088d); `posix_redirects.md` (the method); `__roadmap__/windows_install/README.md` Gotchas (`--selftest` loader on Windows); `plugins/murmuration/scripts/permission_guard.py` (`expand`, `_shell_script`, `redirect_targets`, `_g3_bash`, `protected`, `decide`, `selftest`); `plugins/murmuration/rust/src/guard.rs`; `plugins/murmuration/scripts/check_guard_equal.py` (`json_fragment`)

## Step 1: Decide and implement each gap in both guards
**Goal**: Both guards decide the same on every gap form, each gap with the decision below or a better one the hand-back argues for.
**Implementation Logic**:
The coordinator's starting decisions; the implementer may tighten any of them, and must argue in the hand-back for any change of kind (close vs deny vs accept):
1. **Nested shell strings.** `sh -c '..'` strings are already read again by `expand` (depth 3); `bash -c $'..'` is not, because `words()` (shlex) does not read ANSI-C quoting. Close: the `-c` string is quote-removed as bash does (the `_ansi_c` reading `redirect_targets` already uses) before it is expanded. A script piped to a shell (`.. | sh`, `.. | bash -s`), or fed by a here-doc, here-string or `<` redirect to a shell with no `-c` and no script file, cannot be read in general: deny by default when such a command names a settings file anywhere in its text (the `NAMES_*` pattern), as the interpreter rule of G3 does; a here-doc body fed to a shell may also be expanded as commands.
2. **`${..:-".."}` with nested quotes inside a double-quoted target.** The target holds a `$`, so it is unknown. Deny when an unknown redirect target, read as written, names a settings file (`.claude/settings*.json`, `managed-settings*`).
3. **Variable, command-substitution and glob targets.** Glob: bash opens a glob target when it matches one file; deny when the target, read as a glob (`*`, `?`, `[..]`), could match a protected path. Variable and substitution: deny when the target is unknown and the command assigns a value naming a settings file (`F=..`, `export F=..`, `declare`/`local`/`readonly`) or the substitution inside the target names one. A name built from pieces, base64 or a file's contents stays accepted: the guard is for the direct and casual forms, as its docstring says, and only a managed setting holds against those.
4. **NUL after `~`.** Python denies (an exception in the user lookup, failing closed), Rust allows. Bash cannot receive a NUL. Close: both deny a Bash command that holds a NUL, with the same reason, before any other reading.
5. **A ~5M-character command.** Python times out at 20 s and Rust allows. Whatever Claude Code does on a hook timeout (the rows carry `"onFailure": "block"`; the coordinator cites the documented behaviour in the hand-back record), the two guards must agree. Close: both deny a Bash command, and a Write/Edit/NotebookEdit input, longer than a cap chosen by measurement (the Python guard on the slowest form at the cap well under the 20 s timeout; no recorded real command near the cap), as "too long to be checked", like TooComplex.
6. **`--selftest` on Windows.** The loader at `permission_guard.py` `selftest()` pastes `{T}` raw into the fixture JSON; use `json.dumps(T)[1:-1]`, as `check_guard_equal.json_fragment` does.
Every new reading is added after the old ones (as in posix_redirects), never in place of them, so a denial keeps its reason.
**Deliverables**: `plugins/murmuration/scripts/permission_guard.py` (the new readings, the length cap constant, the NUL rule, the selftest loader, the docstring kept true), `plugins/murmuration/rust/src/guard.rs` (one-for-one port and a test reading `posix_gaps.json` under both `Os` values), `plugins/murmuration/scripts/fixtures/guard_lists/posix_gaps.json`
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/permission_guard.py --selftest && cargo test --manifest-path plugins/murmuration/rust/Cargo.toml` (expected: PASS)
**Commit**: `fix(guard): close the posix gaps left after the redirection reading`

## Step 2: Differential and the equality replay
**Goal**: Prove that only allow-to-deny changes happened, each named, and that both guards agree.
**Implementation Logic**:
Build the old binary from `origin/main`; run old and new Python and old and new binary over every list and payload file under both flavours; list each changed case with its reason. Add `posix_gaps.json` to `check_guard_equal.py`, run it quick and full, and `install_binary.hook_selftest`.
**Deliverables**: `plugins/murmuration/scripts/check_guard_equal.py` (list wiring); the differential evidence in the hand-back
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/check_guard_equal.py --quick --no-recorded --rust plugins/murmuration/rust/target/release/murmuration` (expected: PASS)
**Commit**: `test(guard): replay the posix gap list in the equality check`

## Step 3: Release 0.1.2
**Goal**: The merged sources ship with their CI binaries under a new version.
**Implementation Logic**:
Each push waits for Eliott's yes. Merge into `main` (rebase, then `merge --no-ff`); push `main`; wait for CI's `build(bin)` commit covering the 5 targets; then bump `plugin.json` to 0.1.2, update the Nest entry if needed and push it; install from Nest and check `a01` denied and `ls` allowed.
**Deliverables**: `plugins/murmuration/.claude-plugin/plugin.json` (version 0.1.2); the Nest entry in `../Nest` if it names a version
**Consistency Checks**: `claude plugin validate plugins/murmuration` (expected: PASS)
**Commit**: `chore(release): murmuration 0.1.2`
