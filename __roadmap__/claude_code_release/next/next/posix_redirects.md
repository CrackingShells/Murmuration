# Bash redirections the guard does not read

**Goal**: Both guards (`permission_guard.py`, the exact judge, and its Rust port) read every Bash redirection that bash itself would open for writing, so that a redirect onto a Claude Code settings file is denied whatever its quoting or operator, while every decision that does not involve a redirect stays byte-identical.
**Pre-conditions**:
- [x] `windows_paths` merged into `release/claude-code` (a77b78b)
- [x] The user asked for this leaf, 2026-10-27 ("add a leaf for the posix redirect gap (quoted paths with spaces, >|), with an implementer and a verifier, and land it before publish")
**Success Gates**:
- ✅ [run] A new list `scripts/fixtures/guard_lists/redirects.json` (pinned count, fails if missing, run under both flavours) denies, under G3, a redirect onto a settings target spelled as: a double- or single-quoted path containing a space; a backslash-escaped space (`First\ Last`); adjacent quoted and bare pieces (`".cl"aude/settings.json`); ANSI-C `$'...'`; and the operators `>`, `>>`, `>|`, `&>`, `&>>`, `N>`, `N>>`, `N>|`, `>&word` (a non-digit word), `<>`, with and without spaces between operator and word
- ✅ [run] The same list allows: a `>` inside quotes (`echo "a > b"`, `grep '>' f`); a redirect to an ordinary file whose quoted name contains a space; `2>&1`, `>&2`, `>&-`; a here-doc or here-string; and a pipeline `a | b` that writes nothing protected
- ✅ [run] `python3 -I plugins/murmuration/scripts/permission_guard.py --selftest` exits 0; `cargo test --manifest-path plugins/murmuration/rust/Cargo.toml` passes and runs the list under both `Os` values; `cargo check --release` is clean on the 5 targets
- ✅ [run] Differential against the dispatch base (old vs new Python, old vs new binary), on every existing list, `guard_selftest_payloads.json`, `guard_selftest_holes.json` and `windows_paths.json`: identical exit code and stdout, except cases the hand-back lists one by one, each an allow becoming a deny with a reason. No deny becomes an allow.
- ✅ [run] `check_guard_equal.py --quick --no-recorded --rust <new>` prints "gated sets equal" and replays `redirects.json`; Python vs Rust fuzz over redirect-heavy commands shows 0 differences
**References**: `plugins/murmuration/scripts/permission_guard.py` (`split_segments` and `_split` near line 200-235, which split on `|` and so cut `>|`; the redirect regex at line 644, whose target class `[^\s;&|<>'"]+` stops at a space or quote); `plugins/murmuration/rust/src/guard.rs` (`redirect_targets` at line 786, used at 998); campaign README Gotchas ("Guard gaps found by verify-windows-paths")

## Step 1: Read redirections as bash does, in the Python guard
**Goal**: Each segment's redirection targets are the words bash would open for writing, after quote removal.
**Implementation Logic**:
1. The splitter does not cut at the `|` of `>|` (as it already keeps `>&` and `&>`).
2. Replace the regex with a quote-aware scan of the segment that finds each output redirection operator outside quotes (`>`, `>>`, `>|`, `&>`, `&>>`, an optional fd number before `>`, `>&` followed by a non-digit and non-`-` word, `<>`) and takes the following shell word, quote-removed, as in `words()` (shlex, posix). A word that contains `$` or a backtick is unknown and handled as today's unknown targets are.
3. Feed the targets to `protected()` unchanged; the Windows flavour uses the same scan (Claude Code's Bash tool on Windows runs Git Bash).
4. New list `redirects.json`: each case names a Bash command, a cwd and the expected decision under `posix` and `nt`, covering every form in the gates. The selftest runs it under both flavours with a pinned count and fails if the file is missing.
**Deliverables**: `plugins/murmuration/scripts/permission_guard.py` (e.g. `redirect_targets(seg)`; splitter change; selftest wiring), `plugins/murmuration/scripts/fixtures/guard_lists/redirects.json`
**Consistency Checks**: `cd plugins/murmuration/scripts && python3 -I permission_guard.py --selftest` (expected: PASS)
**Commit**: `fix(guard): read every Bash redirection target, quoted or not`

## Step 2: The same reading in the Rust guard
**Goal**: The Rust port decides exactly as the Python guard on every redirect form.
**Implementation Logic**:
Port the splitter change and the scan one for one into `guard.rs` (`redirect_targets`), keep the doc comment true, and add a unit test that reads `redirects.json` through `CARGO_MANIFEST_DIR` (no `include_str!`) under both `Os` values.
**Deliverables**: `plugins/murmuration/rust/src/guard.rs`, a test module reading the fixture
**Consistency Checks**: `cargo test --manifest-path plugins/murmuration/rust/Cargo.toml && for t in aarch64-apple-darwin x86_64-apple-darwin x86_64-unknown-linux-gnu aarch64-unknown-linux-gnu x86_64-pc-windows-msvc; do cargo check --release --manifest-path plugins/murmuration/rust/Cargo.toml --target $t || exit 1; done` (expected: PASS)
**Commit**: `fix(rust): port the redirection reading to the guard`

## Step 3: Differential and the equality replay
**Goal**: Prove that only allow-to-deny changes happened, each named, and that both guards agree.
**Implementation Logic**:
Build the old binary from the dispatch base; run old and new Python and old and new binary on every existing list; list each changed case with its reason. Add `redirects.json` to `check_guard_equal.py`'s lists, then run it and `install_binary.hook_selftest`.
**Deliverables**: `plugins/murmuration/scripts/check_guard_equal.py` (list wiring); the differential evidence in the hand-back
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/check_guard_equal.py --quick --no-recorded --rust plugins/murmuration/rust/target/release/murmuration` (expected: PASS)
**Commit**: `test(guard): replay the redirection list in the equality check`
