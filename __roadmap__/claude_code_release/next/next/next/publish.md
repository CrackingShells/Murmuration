# Switchover, push, CI binaries, Nest

**Goal**: `main` is public on GitHub with CI-built binaries, and `murmuration@cracking-shells` installs from Nest.
**Pre-conditions**:
- [x] `integrate` done
- [x] The user's go-ahead #2 (push `main`), asked in a fresh session after the switchover — 2026-10-28 09:58, the user: "Yes, push main"; then, for the manual run when the push started no workflow: "Yes, dispatch it"
- [ ] The user's go-ahead #3 (push Nest), asked only after `build(bin)` is on `main`
**Success Gates**:
- ✅ [run] The coordinator's local session reads the plugin from `plugins/murmuration` (`claude plugin list` shows the new path) after the switchover — 2026-10-28: after the switchover all 10 `murmuration@murmuration-local` entries read from `…/Murmuration/plugins/murmuration`; `claude plugin validate plugins/murmuration` passes
- ✅ [run] `origin/main` has a `build(bin): …` commit by `github-actions[bot]`; `git ls-tree` shows the Unix binaries with mode 100755; `install_smoke` green in that run — 2026-10-28: 7509378 `build(bin): guard binaries for 8e80df5` by `github-actions[bot]`, from run 40633506781 (`workflow_dispatch`, `commit_back=true`); `git ls-tree origin/main plugins/murmuration/bin` lists the 4 Unix binaries (aarch64/x86_64 apple-darwin, aarch64/x86_64 unknown-linux-gnu) at 100755 plus `manifest.json` (100644); `install_smoke` green on macos-15 and ubuntu-22.04; the 4 Unix build rows, `assemble` and `commit_back` green. The Windows row is red (see the step 2 results), so the run's overall conclusion is `failure`. Local `main` fast-forwarded to 7509378; local `doubt()` now returns None
- ⬜ [behavioral] A scratch install from GitHub (git-subdir, `https://github.com/CrackingShells/Murmuration.git`) gives `.verified` in the data dir on macOS
- ⬜ [behavioral] After the Nest push: `claude plugin marketplace update cracking-shells` then `claude plugin install murmuration@cracking-shells`; the cache holds the subdir only (or what it holds is reported); `/lab` in a scratch folder creates the lab files; the installed guard denies fixture attack `a01` and allows `ls`
**References**: `integrate.md` results; the campaign README Gotchas (version bump rule)

## Step 1: Switchover on the coordinator's machine
**Goal**: The local session runs the relocated plugin before `main` moves anywhere public.
**Implementation Logic**:
1. Edit the gitignored `.claude-plugin/marketplace.json` at the repo root: plugin `source` becomes `./plugins/murmuration`.
2. Fast-forward `main` to `release/claude-code` (`git merge --no-ff` of the branch, message via `-F`).
3. `claude plugin marketplace update murmuration-local`; restart the session.
**Deliverables**: `main` at the release merge; local marketplace file edited (not tracked)
**Consistency Checks**: `claude plugin list 2>&1 | grep -q 'plugins/murmuration'` (expected: PASS)
**Commit**: `merge(release): Claude Code release layout into main`

## Step 2: Push main and let CI commit the binaries
**Goal**: The public repository holds binaries built by CI from its own sources.
**Implementation Logic**:
1. In the fresh session, ask the user (go-ahead #2), then `git push -u origin main`.
2. The push touches `plugins/murmuration/rust/**` and `scripts/**`, so the workflow runs; wait for it with a background watcher, not a poll loop.
3. Pull the `build(bin)` commit; check modes and the smoke job.
**Deliverables**: `origin/main` with the `build(bin)` commit; local `main` fast-forwarded to it
**Consistency Checks**: `git log origin/main -1 --format=%s | grep -q '^build(bin)'` (expected: PASS)
**Commit**: `docs(roadmap): record the first public push and the CI binaries`
**Results (2026-10-28)**:
- Fresh-session check before the push: `claude plugin list` read all 10 `murmuration@murmuration-local` entries from `…/Murmuration/plugins/murmuration`. SessionStart had written `${CLAUDE_PLUGIN_DATA}/bin/murmuration` as the `#!/bin/sh` Python launcher (no `.verified`), and `doubt()` said "scripts/permission_guard.py changed since the binaries were built". That launcher, fed fixture `a01` from a Python script, returned `permissionDecision: deny` (G1) and allowed `ls`. The UserPromptSubmit hook wrote the user's 09:58 prompt to `__statera__/user_words.md`.
- The checkout had no `origin` remote. Added `https://github.com/CrackingShells/Murmuration.git`, then `env -u GH_TOKEN -u GITHUB_TOKEN git push -u origin main` pushed 8e80df5 to the empty repository.
- The push started no `guard-binaries` run: the workflow was registered and active, but no run appeared about 3 minutes later. The `push.paths` filter did not fire on the first push of a branch to an empty repository. On the user's second yes the workflow was dispatched by hand (run 40633506781). Later pushes that touch `rust/**` or `scripts/**` should trigger it as designed (not yet observed).
- Windows row red, for a new reason (cp1252 is gone: the step reads the fixtures as UTF-8). `cargo test` passed (18 tests). "The Rust guard equals the Python guard" failed before comparing anything: `check_guard_equal.py` `registered_events` substitutes `{T}` (a temp dir, `C:\…` on Windows) into the fixture JSON text, so the backslashes become invalid JSON escapes (`JSONDecodeError: Invalid \escape: line 90 column 21`). The fault is in the test harness, not the guard. `assemble` left Windows out as designed. A fix such as substituting `json.dumps(T)[1:-1]` belongs to the Windows-install cycle.

## Step 3: Nest push and the real install
**Goal**: The published install string works for a stranger.
**Implementation Logic**:
1. Scratch install from GitHub first (git-subdir); check `.verified`.
2. Ask the user (go-ahead #3); push `feat/list-murmuration` in `../Nest` as Nest's workflow requires (merge to its `main` with `--no-ff`, then push).
3. Install from Nest in a scratch folder; run `/lab`; check the guard; report the cache contents.
**Deliverables**: Nest `main` listing `murmuration`; Progress table notes
**Consistency Checks**: `claude plugin list 2>&1 | grep -q 'murmuration@cracking-shells'` (expected: PASS)
**Commit**: `docs(roadmap): record the Nest listing and the first install from it`
**Results (2026-10-28, session murmuration-publish-step3)**:
- Data-dir check before anything else: `~/.claude/plugins/data/murmuration-murmuration-local/bin/` holds `murmuration` (Mach-O 64-bit arm64, 636512 B) and `.verified`, both dated 14:59 (`ls -la`, `file`).
- Plan approved by Eliott with three answers: scope "Project (Recommended)", PI agent "Never set it", update check "Ship 0.1.1 as the check (Recommended)". Amendment A1 adds `local_cleanup`, `lab_pi_choice`, `readme_install`, `ship_update`, `first_project`.
