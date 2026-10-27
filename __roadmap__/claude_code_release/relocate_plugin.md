# Relocate the plugin into plugins/murmuration

**Goal**: The installable plugin is one self-contained tree, `plugins/murmuration/`, whose selftests pass with no research store beside it.
**Pre-conditions**:
- [x] `release/claude-code` cut from `main` at b28572b, worktree clean apart from hook noise in `__statera__/`
- [x] Baseline measured in the worktree (2026-10-27): the 7 `--selftest` modes exit 0; the 7 guard lists hold 121 cases (attacks 50, ordinary 28, mention 6, evasions 13, e3v1 14, e3v2 6, e3v3 4)
**Success Gates**:
- ⬜ [run] Every `--selftest` (permission_guard, budget, handback, lab_init, lab_status, user_words, resume_brief) exits 0 inside an extraction of `git archive HEAD plugins/murmuration`, with no `__reports__/` anywhere above it
- ⬜ [run] `permission_guard.py --selftest` exits 1 when `scripts/fixtures/guard_lists/` is removed from that extraction
- ⬜ [run] Right after the pure move (step 1), `install_binary.doubt(plugin_root, "aarch64-apple-darwin")` returns `None`: the manifest's relative paths survive the move
- ⬜ [static] `rust/Cargo.toml` says `license = "AGPL-3.0-only"`
**References**: `scripts/install_binary.py` `doubt()` — what the move must not break; `scripts/permission_guard.py:563` and `scripts/check_guard_equal.py:26` — the two readers of `__reports__/wave-06/author-w06-5/`

## Step 1: Move the runtime as one unit
**Goal**: `plugins/murmuration/` holds everything Claude Code loads and everything `doubt()` hashes.
**Implementation Logic**:
1. `git mv` `.claude-plugin/ agents/ skills/ hooks/ scripts/ rust/ bin/` into `plugins/murmuration/`; copy `LICENSE` into it (Claude Code caches only the subdir, so the licence must be inside).
2. Add `.gitattributes`: `* text=auto eol=lf`, and `plugins/murmuration/bin/** binary`, so a Windows checkout does not rewrite the hashed sources with CRLF.
3. `.gitignore`: `rust/target/` becomes `plugins/murmuration/rust/target/`.
4. Content of moved files is untouched in this step, so the manifest still matches.
**Deliverables**: `plugins/murmuration/{.claude-plugin/plugin.json, agents/, skills/, hooks/hooks.json, scripts/, rust/, bin/manifest.json, LICENSE}`; `.gitattributes`; `.gitignore`
**Consistency Checks**: `python3 -I -c "import sys; sys.path.insert(0,'plugins/murmuration/scripts'); import install_binary as i; r=i.doubt('plugins/murmuration','aarch64-apple-darwin'); print(r); sys.exit(r is not None)"` (expected: PASS)
**Commit**: `refactor(plugin): move the plugin runtime into plugins/murmuration`

## Step 2: Guard lists become pinned fixtures inside the plugin
**Goal**: The guard selftest no longer reads `__reports__/` and can no longer pass on empty lists.
**Implementation Logic**:
1. Copy the 7 list files `e3_attacks e3_ordinary e3_mention e3_evasions e3v1_cases e3v2_cases e3v3_cases` (`.json`) from `__reports__/wave-06/author-w06-5/` to `plugins/murmuration/scripts/fixtures/guard_lists/`. The originals stay as the research record.
2. `permission_guard.selftest()`: read from `HERE/fixtures/guard_lists`; a missing file is a FAIL, and the counts are pinned in a constant `FIXTURE_COUNTS = {"attacks": 50, "ordinary": 28, "mention": 6, "evasions": 13}`; a count that differs is a FAIL.
3. `check_guard_equal.LISTS` points to the same folder. `default_rust` is left for targets_contract.
**Deliverables**: `plugins/murmuration/scripts/fixtures/guard_lists/*.json` (7 files); `plugins/murmuration/scripts/permission_guard.py` (`selftest`, `FIXTURE_COUNTS`); `plugins/murmuration/scripts/check_guard_equal.py` (`LISTS`)
**Consistency Checks**: `X=$(mktemp -d) && git archive HEAD plugins/murmuration | tar -x -C $X && python3 -I $X/plugins/murmuration/scripts/permission_guard.py --selftest && rm -r $X/plugins/murmuration/scripts/fixtures && ! python3 -I $X/plugins/murmuration/scripts/permission_guard.py --selftest` (expected: PASS)
**Commit**: `fix(guard): read the selftest lists from pinned fixtures inside the plugin`

## Step 3: Crate licence matches the plugin
**Goal**: The Rust crate is licensed like the rest of the plugin.
**Implementation Logic**:
1. `rust/Cargo.toml`: `license = "MIT"` becomes `license = "AGPL-3.0-only"` (the plugin and repository are AGPL-3.0-only).
2. This changes a hashed source, so local `doubt()` now says "Rust sources changed" until CI rebuilds. Expected; recorded in Gotchas of the campaign README.
**Deliverables**: `plugins/murmuration/rust/Cargo.toml` (`license`)
**Consistency Checks**: `cargo metadata --no-deps --format-version 1 --manifest-path plugins/murmuration/rust/Cargo.toml | python3 -I -c "import json,sys; sys.exit(json.load(sys.stdin)['packages'][0]['license']!='AGPL-3.0-only')"` (expected: PASS)
**Commit**: `chore(rust): license the crate AGPL-3.0-only like the plugin`
