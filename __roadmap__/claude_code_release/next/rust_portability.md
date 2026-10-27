# Rust portability by conditional compilation

**Goal**: The `murmuration` crate compiles for macOS, Linux and Windows through one `platform` module, and its Unix decisions stay byte-identical.
**Pre-conditions**:
- [ ] `relocate_plugin` merged into `release/claude-code` (the crate is at `plugins/murmuration/rust/`)
- [ ] `rustup target add aarch64-unknown-linux-gnu x86_64-pc-windows-msvc` done (check targets only; no linker needed for `cargo check`)
**Success Gates**:
- ⬜ [run] `cargo test --manifest-path plugins/murmuration/rust/Cargo.toml` passes, including new unit tests of the pure functions in `platform`
- ⬜ [run] `cargo check --release --target T` passes for T in aarch64-apple-darwin, x86_64-apple-darwin, x86_64-unknown-linux-gnu, aarch64-unknown-linux-gnu, x86_64-pc-windows-msvc
- ⬜ [run] Differential: the binary built from the `release/claude-code` tip before this leaf and the binary built after it give identical exit code and stdout on every payload of `scripts/guard_selftest_payloads.json` and on `check_guard_equal.py --quick --no-recorded --rust <new>` (macOS host)
- ⬜ [run] `install_binary.hook_selftest(root, <new binary>)` returns `None` on the macOS host
- ⬜ [static] No `std::os::unix`, `extern "C"` or `"python3"` literal outside `src/platform.rs`
**References**: `plugins/murmuration/rust/src/{guard.rs:1038, hook.rs:154-182, text.rs:277, main.rs:66-90}` — the four Unix-only sites; `plugins/murmuration/scripts/install_binary.py` `self_test`, `hook_selftest` — the equality oracle

## Step 1: Introduce the platform module, Unix arms only
**Goal**: The four Unix-only sites call one module, with no behaviour change.
**Implementation Logic**:
1. New `src/platform.rs` with `pub(crate) fn local_offset(epoch_s: i64) -> i64`, `pub(crate) fn home_dir() -> Option<String>`, `pub(crate) fn path_from_bytes(bytes: Vec<u8>) -> PathBuf`, `pub(crate) fn python_cmd() -> &'static str`.
2. Move the existing code into `#[cfg(unix)]` arms unchanged: `localtime_r` with its `Tm` struct and SAFETY comment (layout is the same on macOS and glibc Linux), `HOME` then `std::env::home_dir`, `OsStringExt::from_vec`, `"python3"`.
3. Call sites in `hook.rs`, `text.rs`, `guard.rs`, `main.rs` use the module. `expanduser`'s `/` handling stays in `text.rs` (it emulates `posixpath`).
**Deliverables**: `plugins/murmuration/rust/src/platform.rs` (`local_offset`, `home_dir`, `path_from_bytes`, `python_cmd`); `src/main.rs` (`mod platform`)
**Consistency Checks**: `cargo test --manifest-path plugins/murmuration/rust/Cargo.toml && cargo build --release --manifest-path plugins/murmuration/rust/Cargo.toml && python3 -I plugins/murmuration/scripts/check_guard_equal.py --quick --no-recorded --rust plugins/murmuration/rust/target/release/murmuration` (expected: PASS)
**Commit**: `refactor(rust): route the Unix-only calls through a platform module`

## Step 2: Windows arms, with the decision logic pure and tested everywhere
**Goal**: The crate compiles for `x86_64-pc-windows-msvc`, and what differs by OS is decided by pure functions tested on every host.
**Implementation Logic**:
1. Pure, OS-independent helpers that take their inputs: `home_from(home: Option<OsString>, userprofile: Option<OsString>, os: Os) -> Option<String>` and `python_for(os: Os) -> &'static str` with `enum Os { Unix, Windows }`. The `#[cfg]` wrappers only read the environment and pass `Os`.
2. `#[cfg(windows)]` arms: offset from `_localtime64_s` and `_mkgmtime64` (the MSVC CRT names; there is no `tm_gmtoff`); `home_dir` from `USERPROFILE` then `HOME`; `path_from_bytes` through `String::from_utf8` (a non-UTF-8 path is an error path, never an allow); `python_for(Windows)` is `"python"`.
3. No arm may return a default that allows what Unix would deny: a Windows failure falls back to offset 0, no home (path left unexpanded), or a failed spawn, exactly as the Unix error paths already do.
4. Unit tests for `home_from` and `python_for` on all `Os` values, including empty and absent variables, run under `cargo test` on any host.
**Deliverables**: `src/platform.rs` (`Os`, `home_from`, `python_for`, `#[cfg(windows)]` arms, `#[cfg(test)] mod tests`)
**Consistency Checks**: `for t in aarch64-apple-darwin x86_64-apple-darwin x86_64-unknown-linux-gnu aarch64-unknown-linux-gnu x86_64-pc-windows-msvc; do cargo check --release --target $t --manifest-path plugins/murmuration/rust/Cargo.toml || exit 1; done` (expected: PASS)
**Commit**: `feat(rust): compile for Windows through cfg arms with pure, tested OS logic`

## Step 3: Differential evidence on the host
**Goal**: Show the port changed no Unix decision.
**Implementation Logic**:
1. Build the pre-leaf binary from the merge-base with `release/claude-code` into a scratch dir; build the new one.
2. Feed every payload of `scripts/guard_selftest_payloads.json` to both (`guard` subcommand) and compare exit code and stdout byte for byte; run `install_binary.hook_selftest` on the new binary.
3. Record the commands and their outputs in the hand-back (no file is committed for this step unless a test is added to `rust/tests/`).
**Deliverables**: hand-back section "Differential" with the two build commits, payload count, and zero differences; optional `plugins/murmuration/rust/tests/platform_equivalence.rs`
**Consistency Checks**: `python3 -I -c "import sys; sys.path.insert(0,'plugins/murmuration/scripts'); import install_binary as i; r=i.hook_selftest('plugins/murmuration','plugins/murmuration/rust/target/release/murmuration'); print(r); sys.exit(r is not None)"` (expected: PASS)
**Commit**: `test(rust): record the Unix differential for the platform port`
