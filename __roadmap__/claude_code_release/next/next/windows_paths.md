# Windows path semantics in both guards

**Goal**: On Windows, both guards (`permission_guard.py`, the exact judge, and its Rust port) deny every direct form of a settings-file write and of a `claude` program name that Windows itself would resolve to the denied target, while macOS and Linux decisions stay byte-identical.
**Pre-conditions**:
- [x] rust_portability and targets_contract merged into `release/claude-code` (platform module, `Os`, hash allowlist)
- [x] The user asked for this repair, 2026-10-27 ("Dispatch a dedicated implementer in its worktree for reparing this hole")
**Success Gates**:
- ✅ [run] `python3 -I plugins/murmuration/scripts/permission_guard.py --selftest` exits 0 and runs the new list `fixtures/guard_lists/windows_paths.json` under both flavours (posix and nt) on any host, with its pinned count
- ✅ [run] `cargo test --manifest-path plugins/murmuration/rust/Cargo.toml` passes and runs the same list under both `Os` values, with the same expected decisions
- ✅ [run] Unix unchanged: old (`release/claude-code` tip at dispatch) vs new binary, and old vs new Python guard, give identical exit code and stdout on all 7 existing fixture lists, `guard_selftest_payloads.json` and `guard_selftest_holes.json`; `check_guard_equal.py --quick --no-recorded --rust <new>` prints "gated sets equal"
- ✅ [run] The nt flavour denies at least: `C:\Users\u\.claude\settings.json`, `.claude\settings.json`, `.claude\settings.local.json`, mixed separators, `.Claude\Settings.JSON`, a trailing dot or space (`settings.json.`, `settings.json `), an alternate data stream (`settings.json::$DATA`, `settings.json:x`), `\\?\C:\...`, a UNC path, drive-relative `C:.claude\settings.json`, and `managed-settings` under the same variations; and treats `claude.exe`, `CLAUDE`, `C:\...\claude.cmd` as the `claude` program for G1/G2
- ✅ [static] The posix flavour keeps a backslash as an ordinary filename character (a Unix file named `.claude\settings.json` is not a settings file) and stays case-sensitive
- ✅ [static] `check_guard_equal.py` replays `windows_paths.json` too, so the Windows CI row compares both guards natively on Windows
- ✅ [static] No text-mode `open()` without an encoding in `plugins/murmuration/scripts` (`python3 -I plugins/murmuration/scripts/check_text_io.py` exits 0; it also covers `read_text`, `write_text`, text-mode subprocess pipes, and the UTF-8 stdin and stdout of every `main()`)
**References**: `plugins/murmuration/scripts/permission_guard.py` (settings-path check near lines 386-400, `"/" not in p` at 393; program names via `os.path.basename` at 157, 169, 361, 379, 426, 445, 472; G4 extensions); `plugins/murmuration/rust/src/text.rs` (posix-only isabs, basename, normpath, join), `rust/src/guard.rs`, `rust/src/platform.rs` (`Os`); campaign README Gotchas ("Windows guard binary is not trustworthy yet")

## Step 1: Flavour-parametrised path logic in the Python guard
**Goal**: The Python guard's path and program-name decisions take a flavour (posix or nt) so both are testable on any host, and the nt flavour closes the Windows forms.
**Implementation Logic**:
1. Route every path and program-name operation the decisions use through one small set of pure helpers that take a flavour: posix uses `posixpath` exactly as today; nt uses `ntpath` (importable on every OS) plus Windows name resolution: case-fold, strip trailing dots and spaces per component, drop an alternate-data-stream suffix, accept `\\?\` and UNC prefixes, drive-relative paths; program names case-folded with `.exe`, `.cmd`, `.bat`, `.com` stripped.
2. The runtime flavour is `nt` when `os.name == "nt"`, else posix. Nothing changes for posix: same calls, same order, same results.
3. The G3 Bash write forms (redirection, tee, cp, mv, ...) and the G4 script extensions (`.PY`, `.Sh` on nt) go through the helpers too.
4. New list `scripts/fixtures/guard_lists/windows_paths.json`: each case names a tool event, a cwd, and the expected decision under `posix` and under `nt`. The selftest runs it under both flavours with a pinned count, and fails if the file is missing.
**Deliverables**: `plugins/murmuration/scripts/permission_guard.py` (flavour helpers, e.g. `_pathmod(flavour)`, `settings_target(path, cwd, flavour)`, `prog_name(token, flavour)`; selftest wiring), `plugins/murmuration/scripts/fixtures/guard_lists/windows_paths.json`
**Consistency Checks**: `cd plugins/murmuration/scripts && python3 -I permission_guard.py --selftest` (expected: PASS)
**Commit**: `fix(guard): read Windows paths and program names as Windows does`

## Step 2: The same semantics in the Rust guard
**Goal**: The Rust port decides exactly as the Python guard on both flavours.
**Implementation Logic**:
1. Give the `text.rs` path helpers an `Os` parameter (from `platform.rs`); the guard passes the compile-time `Os`. The Unix arm keeps today's code path unchanged.
2. Port the nt resolution rules of step 1 one for one.
3. A unit test reads `windows_paths.json` (path from `CARGO_MANIFEST_DIR`, at test time only; no `include_str!`, so the binary does not embed it) and asserts the expected decision under both `Os` values.
**Deliverables**: `plugins/murmuration/rust/src/text.rs`, `plugins/murmuration/rust/src/guard.rs`, `plugins/murmuration/rust/src/platform.rs` (if `Os` needs a constructor), a test module reading the fixture
**Consistency Checks**: `cargo test --manifest-path plugins/murmuration/rust/Cargo.toml && for t in aarch64-apple-darwin x86_64-apple-darwin x86_64-unknown-linux-gnu aarch64-unknown-linux-gnu x86_64-pc-windows-msvc; do cargo check --release --manifest-path plugins/murmuration/rust/Cargo.toml --target $t || exit 1; done` (expected: PASS)
**Commit**: `fix(rust): port the Windows path semantics to the guard`

## Step 3: Unix differential and the native Windows replay
**Goal**: Prove nothing moved on Unix, and let the Windows CI row compare both guards on Windows itself.
**Implementation Logic**:
1. Build the old binary from the dispatch base and the new one; run both, and old and new Python, on every existing list; report differences (expected none).
2. Add `windows_paths.json` to the lists `check_guard_equal.py` replays, so the CI Windows row (real `ntpath`, real binary) compares them.
3. Run `check_guard_equal.py --quick --no-recorded --rust <new>` and `install_binary.hook_selftest`.
**Deliverables**: `plugins/murmuration/scripts/check_guard_equal.py` (list wiring); the differential evidence in the hand-back
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/check_guard_equal.py --quick --no-recorded --rust plugins/murmuration/rust/target/release/murmuration` (expected: PASS)
**Commit**: `test(guard): replay the Windows path list in the equality check`

## Step 4: Read and write text as UTF-8 on every OS
**Goal**: No script depends on the locale's code page, so the Windows CI row neither fails on a non-ASCII byte (`UnicodeDecodeError: 'charmap' codec can't decode byte 0x81` at `check_guard_equal.py` line 307) nor lets Python and Rust decide differently on non-ASCII input.
**Implementation Logic**:
1. Every text-mode `open()` in `plugins/murmuration/scripts/*.py` gets `encoding="utf-8"`, keeping any `errors=`; so does every text-mode subprocess call (`text=True`). Binary opens are left alone.
2. The guard's log is opened with `newline="\n"`, so a Windows run appends the same bytes as the Rust guard.
3. Each script's `main()` starts with `_utf8_stdio()`, which reconfigures stdin, stdout and stderr to UTF-8 (stdout and stderr with `\n` newlines), because `python -I` ignores `PYTHONUTF8` and `PYTHONIOENCODING`. On a UTF-8 locale this changes nothing.
4. `scripts/check_text_io.py` is the static check (ast, no regex) with a `--selftest` that proves it catches each kind of finding and that the guard reads a UTF-8 payload under the C locale with UTF-8 mode off.
**Deliverables**: every `plugins/murmuration/scripts/*.py` that opened text without an encoding, `plugins/murmuration/scripts/check_text_io.py`; the manifest scripts hash changes (expected)
**Consistency Checks**: `cd plugins/murmuration/scripts && python3 -I check_text_io.py && python3 -I check_text_io.py --selftest && python3 -I permission_guard.py --selftest` (expected: PASS); Unix unchanged: old and new Python guard, started as the hook starts it with `LC_ALL=en_US.UTF-8`, give identical exit code, stdout and log line on the lists, holes, payloads and non-ASCII variants of them
**Commit**: `fix(scripts): read and write text as UTF-8 on every OS`
