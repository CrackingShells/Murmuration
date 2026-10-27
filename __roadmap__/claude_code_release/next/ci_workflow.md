# CI builds and commits the binaries

**Goal**: GitHub Actions builds the guard for 5 targets, checks each against the Python scripts, smoke-installs, and commits `bin/` back to `main` only when everything agrees.
**Pre-conditions**:
- [ ] `relocate_plugin` merged into `release/claude-code` (paths are under `plugins/murmuration/`)
- [ ] The contract CLI is pinned (implemented in parallel by targets_contract): `build_manifest.py binary-name <t>` prints the file name; `build_manifest.py sources-hash` prints the combined Rust sources hash; `build_manifest.py --expect-targets t1,t2,...` exits 1 and writes nothing unless the binaries present equal the list
**Success Gates**:
- ⬜ [run] `actionlint .github/workflows/guard-binaries.yml` exits 0
- ⬜ [static] Matrix targets equal `ALL_TARGETS` (the 5 triples); every runner label is one GitHub lists as current, checked against GitHub's runner-images documentation (cite the page and date in the hand-back)
- ⬜ [static] The commit-back job runs only on `push` to `main`, needs the smoke job, holds `permissions: contents: write` alone (all other jobs `contents: read`), and sits in `concurrency: { group: bin-commit, cancel-in-progress: false }`
- ⬜ [static] On `workflow_dispatch` with input `commit_back: false` (the default), nothing is pushed; the assembled `bin/` is uploaded as an artefact
- ⬜ [static] The Windows row cannot fail the run: its absence is detected by the presence of its artefact, never by `continue-on-error`
**References**: `.github/workflows/guard-binaries.yml` (today: 4 rows, `macos-13` retired, no commit); `plugins/murmuration/scripts/check_guard_equal.py` usage line; the targets_contract leaf for the CLI

## Step 1: Build rows that check before they upload
**Goal**: Each row uploads a binary only after it equals the Python guard on that runner and has the right architecture.
**Implementation Logic**:
1. Triggers: `push` with `paths: ["plugins/murmuration/rust/**", "plugins/murmuration/scripts/**"]` (all hashed scripts live there; `bin/**` is excluded, so the bot's commit cannot retrigger), and `workflow_dispatch` with boolean input `commit_back` default `false`.
2. Matrix: aarch64-apple-darwin on `macos-14`; x86_64-apple-darwin on the current Intel macOS label (verify; `macos-13` is retired); x86_64-unknown-linux-gnu on `ubuntu-22.04`; aarch64-unknown-linux-gnu on `ubuntu-22.04-arm`; x86_64-pc-windows-msvc on `windows-latest`. `actions/setup-python` 3.12 on every row; `defaults.run.shell: bash`.
3. Per row: `cargo test`, `cargo build --release --target`, copy to `bin/<t>/$(build_manifest.py binary-name <t>)`, `check_guard_equal.py --quick --no-recorded --rust <that file>`, then a `file` check that the architecture matches the triple, then write `sources-hash` into `sources.sha256` beside the binary; upload `murmuration-<t>` containing both files.
4. The Windows row runs the same steps; if any fails, the row is red, uploads nothing, and the run continues (`fail-fast: false`).
**Deliverables**: `.github/workflows/guard-binaries.yml` (`on`, job `build` with the 5-row matrix)
**Consistency Checks**: `actionlint .github/workflows/guard-binaries.yml` (expected: PASS)
**Commit**: `ci(bin): build and check the guard on five targets before upload`

## Step 2: Assemble, smoke-install, then commit back
**Goal**: The committed `bin/` is exactly what the rows built from this commit, and it installs.
**Implementation Logic**:
1. Job `assemble` (`needs: build`, `if: always()`, so a red Windows row does not skip it): download all artefacts, clear `plugins/murmuration/bin/*/`, copy each in, `chmod +x` the Unix ones; refuse if any `sources.sha256` differs from this checkout's `sources-hash` (a binary from other sources); expected targets = the 4 Unix triples plus Windows only if its artefact exists (emit a `::warning::` when it does not); `build_manifest.py --expect-targets "$expected"`; upload `bin-and-manifest`. A missing Unix artefact fails the job.
2. Job `install_smoke` (`needs: assemble`) on `macos-14` and `ubuntu-22.04`: copy the plugin tree, drop in the artefact, run `install_binary.py` with `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` set to temp folders, and assert `$CLAUDE_PLUGIN_DATA/bin/.verified` exists and stdout is empty (the launcher writes a note; the binary path writes nothing).
3. Job `commit_back` (`needs: install_smoke`, `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`): fetch `origin/main`; if it moved past `github.sha`, recompute the manifest on the new tip with the assembled binaries and continue only when `rust_sources_sha256` and `scripts_sha256` are unchanged, else exit 0 with a notice (the newer push runs its own build); skip when `git diff --quiet` shows nothing new; commit as `github-actions[bot]` with message `build(bin): guard binaries for <short sha>` and push.
**Deliverables**: `.github/workflows/guard-binaries.yml` (jobs `assemble`, `install_smoke`, `commit_back`; `permissions`; `concurrency`)
**Consistency Checks**: `actionlint .github/workflows/guard-binaries.yml && python3 -I -c "import sys; t=open('.github/workflows/guard-binaries.yml').read(); sys.exit(not all(k in t for k in ('bin-commit','commit_back','install_smoke','expect-targets','sources-hash')))"` (expected: PASS)
**Commit**: `ci(bin): assemble, smoke-install and commit the binaries back to main`

## Step 3: Local evidence
**Goal**: Show what can be shown without pushing.
**Implementation Logic**:
1. If `act` and Docker are available, run the x86_64 Linux build row with `act`; `act` is not installed on the coordinator's machine (checked 2026-10-27), so install it only if that is a single Homebrew command, else skip and say so.
2. Replace the header comment of the workflow (today it says "not pushed by the lab" and "untested") with one line per adversarial case and the job that handles it: `main` moving mid-run, a commit-back loop, token scope, an artefact under the wrong target name, Windows absent, a wrong-architecture binary.
**Deliverables**: `.github/workflows/guard-binaries.yml` (header comment); hand-back section "Local evidence"
**Consistency Checks**: `actionlint .github/workflows/guard-binaries.yml` (expected: PASS)
**Commit**: `docs(ci): note how the binary workflow handles races, loops and missing rows`
