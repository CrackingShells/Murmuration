# One binary naming and target contract

**Goal**: One module says which targets exist, what each binary is called, and which may be installed; the manifest refuses a missing, extra or stale binary.
**Pre-conditions**:
- [ ] `relocate_plugin` merged into `release/claude-code`
**Success Gates**:
- ⬜ [run] `python3 -I plugins/murmuration/scripts/build_manifest.py binary-name x86_64-pc-windows-msvc` prints `murmuration.exe`; for each of the 4 Unix targets it prints `murmuration`
- ⬜ [run] `build_manifest.py --expect-targets <list>` exits 1 and writes nothing when a listed target's binary is absent, or when `bin/` holds a target not in the list
- ⬜ [run] `build_manifest.py sources-hash` prints the same value as the manifest's `rust_sources_sha256` written in the same tree
- ⬜ [run] Each mutation is rejected by `doubt()` with its own reason: one source byte flipped ("sources changed"), one binary byte flipped ("does not match its hash"), the manifest's entry for the host target removed, a CRLF rewrite of a hashed `.rs` file
- ⬜ [run] `install_binary.TARGETS` maps `("Linux","x86_64")` and `("Linux","aarch64")`, and no Windows key; all 7 `--selftest` modes still exit 0
- ⬜ [static] The pre-commit hook writes neither `bin/` nor `bin/manifest.json`
**References**: `plugins/murmuration/scripts/build_manifest.py` (`build`, `sources_hash`); `scripts/install_binary.py` (`TARGETS`, `doubt`, `install`, the launcher note in `main`); `scripts/check_guard_equal.py` (`default_rust`); `scripts/git-hooks/pre-commit`

## Step 1: Targets and names in build_manifest.py
**Goal**: The contract has one home and a CLI that CI can call.
**Implementation Logic**:
1. `ALL_TARGETS` (the 5 triples CI builds: aarch64-apple-darwin, x86_64-apple-darwin, x86_64-unknown-linux-gnu, aarch64-unknown-linux-gnu, x86_64-pc-windows-msvc); `binary_name(target)` returns `murmuration.exe` when `"windows"` is in the triple, else `murmuration`; `host_target()` maps `platform.system()`/`machine()` to a triple or `None` (Windows `AMD64` included).
2. `build(root)` hashes `bin/<t>/<binary_name(t)>` for each folder under `bin/` and ignores anything else.
3. CLI (argument order free, stdlib `argparse`): `binary-name <t>` prints the name; `sources-hash` prints the combined Rust sources hash; `--expect-targets t1,t2,...` makes the write fail (exit 1, message on stderr, manifest untouched) unless the set of present binaries equals the list exactly; `--root DIR` as today. The bare call keeps writing the manifest.
4. Unit-style checks under a new `--selftest` of build_manifest.py over a temp tree.
**Deliverables**: `plugins/murmuration/scripts/build_manifest.py` (`ALL_TARGETS`, `binary_name`, `host_target`, `build`, `main` with subcommands `binary-name`, `sources-hash`, options `--expect-targets`, `--root`, `--selftest`)
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/build_manifest.py --selftest && test "$(python3 -I plugins/murmuration/scripts/build_manifest.py binary-name x86_64-pc-windows-msvc)" = murmuration.exe` (expected: PASS)
**Commit**: `feat(manifest): one target list and binary-name contract with an exact-target check`

## Step 2: Installer and replay use the contract
**Goal**: `doubt()`, `install()` and `check_guard_equal` find binaries only through `binary_name`, and Linux installs the binary.
**Implementation Logic**:
1. `install_binary.TARGETS` gains `("Linux","x86_64"): "x86_64-unknown-linux-gnu"` and `("Linux","aarch64"): "aarch64-unknown-linux-gnu"`. Windows stays out (Windows installs are a later cycle: the SessionStart rows exec `python3` and the data path is `bin/murmuration`).
2. `doubt()` and `install()` resolve `bin/<t>/<binary_name(t)>` via the already-loaded `build_manifest` module; a manifest whose `binaries` lacks the target is a doubt with its own reason.
3. `check_guard_equal.default_rust()` uses `host_target()` and `binary_name()` (today it guesses `<arch>-apple-darwin`).
4. The launcher note in `install_binary.main()` no longer tells the user to run the pre-commit hook to rebuild; it says the binary comes from CI and the Python scripts decide meanwhile.
**Deliverables**: `plugins/murmuration/scripts/install_binary.py` (`TARGETS`, `doubt`, `install`, `main` note); `plugins/murmuration/scripts/check_guard_equal.py` (`default_rust`)
**Consistency Checks**: `cd plugins/murmuration && for s in permission_guard budget handback lab_init lab_status user_words resume_brief; do python3 -I scripts/$s.py --selftest >/dev/null || exit 1; done` (expected: PASS)
**Commit**: `feat(install): install the Linux binaries and resolve every binary through binary_name`

## Step 3: Mutation tests of the trust oracle
**Goal**: Show that each way a binary can be wrong is caught before install.
**Implementation Logic**:
1. Add the mutations to `install_binary`'s own test surface (a `--selftest` mode or an extension of the existing one) on a temp copy of the plugin tree: flip a byte in a hashed `.rs` file; flip a byte in the binary; delete the host entry from `binaries`; rewrite a hashed `.rs` file with CRLF; put a binary under a target the manifest does not list. Each must give a non-`None` `doubt()` with the expected reason, and `install()` must end in state `launcher`.
2. Stale binary: a binary whose manifest was written over different sources is caught by `sources_hash` (sources changed) or by `self_test`; state which one in a comment.
**Deliverables**: `plugins/murmuration/scripts/install_binary.py` (`selftest` with the mutation cases)
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/install_binary.py --selftest` (expected: PASS)
**Commit**: `test(install): reject flipped sources, flipped binaries, missing targets and CRLF`

## Step 4: Pre-commit replays, never writes bin/
**Goal**: Local commits check the guard without producing binaries that CI owns.
**Implementation Logic**:
1. Trigger regex: `^plugins/murmuration/(scripts/permission_guard\.py|rust/)`.
2. Build the host target into `plugins/murmuration/rust/target/` (`cargo build --release --offline`), then `exec python3 -I plugins/murmuration/scripts/check_guard_equal.py --quick --rust plugins/murmuration/rust/target/release/murmuration`. No `cp` into `bin/`, no `build_manifest.py`, no `git add`.
3. Header comment: install with `ln -s ../../plugins/murmuration/scripts/git-hooks/pre-commit .git/hooks/pre-commit`; CI owns `bin/`.
**Deliverables**: `plugins/murmuration/scripts/git-hooks/pre-commit`
**Consistency Checks**: `! grep -Eq 'build_manifest\.py|git add|cp .*bin/' plugins/murmuration/scripts/git-hooks/pre-commit` (expected: PASS)
**Commit**: `build(hooks): pre-commit replays the guard and leaves bin/ to CI`
