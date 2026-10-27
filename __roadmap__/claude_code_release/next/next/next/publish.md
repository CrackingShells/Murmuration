# Switchover, push, CI binaries, Nest

**Goal**: `main` is public on GitHub with CI-built binaries, and `murmuration@cracking-shells` installs from Nest.
**Pre-conditions**:
- [ ] `integrate` done
- [ ] The user's go-ahead #2 (push `main`), asked in a fresh session after the switchover
- [ ] The user's go-ahead #3 (push Nest), asked only after `build(bin)` is on `main`
**Success Gates**:
- ⬜ [run] The coordinator's local session reads the plugin from `plugins/murmuration` (`claude plugin list` shows the new path) after the switchover
- ⬜ [run] `origin/main` has a `build(bin): …` commit by `github-actions[bot]`; `git ls-tree` shows the Unix binaries with mode 100755; `install_smoke` green in that run
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

## Step 3: Nest push and the real install
**Goal**: The published install string works for a stranger.
**Implementation Logic**:
1. Scratch install from GitHub first (git-subdir); check `.verified`.
2. Ask the user (go-ahead #3); push `feat/list-murmuration` in `../Nest` as Nest's workflow requires (merge to its `main` with `--no-ff`, then push).
3. Install from Nest in a scratch folder; run `/lab`; check the guard; report the cache contents.
**Deliverables**: Nest `main` listing `murmuration`; Progress table notes
**Consistency Checks**: `claude plugin list 2>&1 | grep -q 'murmuration@cracking-shells'` (expected: PASS)
**Commit**: `docs(roadmap): record the Nest listing and the first install from it`
