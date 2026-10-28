# Switchover, push, CI binaries, Nest

**Goal**: `main` is public on GitHub with CI-built binaries, and `murmuration@cracking-shells` installs from Nest.
**Pre-conditions**:
- [x] `integrate` done
- [x] The user's go-ahead #2 (push `main`), asked in a fresh session after the switchover — 2026-10-28 09:58, the user: "Yes, push main"; then, for the manual run when the push started no workflow: "Yes, dispatch it"
- [x] The user's go-ahead #3 (push Nest), asked only after `build(bin)` is on `main` — 2026-10-28, Eliott: "Yes, push Nest"
**Success Gates**:
- ✅ [run] The coordinator's local session reads the plugin from `plugins/murmuration` (`claude plugin list` shows the new path) after the switchover — 2026-10-28: after the switchover all 10 `murmuration@murmuration-local` entries read from `…/Murmuration/plugins/murmuration`; `claude plugin validate plugins/murmuration` passes
- ✅ [run] `origin/main` has a `build(bin): …` commit by `github-actions[bot]`; `git ls-tree` shows the Unix binaries with mode 100755; `install_smoke` green in that run — 2026-10-28: 7509378 `build(bin): guard binaries for 8e80df5` by `github-actions[bot]`, from run 40633506781 (`workflow_dispatch`, `commit_back=true`); `git ls-tree origin/main plugins/murmuration/bin` lists the 4 Unix binaries (aarch64/x86_64 apple-darwin, aarch64/x86_64 unknown-linux-gnu) at 100755 plus `manifest.json` (100644); `install_smoke` green on macos-15 and ubuntu-22.04; the 4 Unix build rows, `assemble` and `commit_back` green. The Windows row is red (see the step 2 results), so the run's overall conclusion is `failure`. Local `main` fast-forwarded to 7509378; local `doubt()` now returns None
- ✅ [behavioral] A scratch install from GitHub (git-subdir, `https://github.com/CrackingShells/Murmuration.git`) gives `.verified` in the data dir on macOS — 2026-10-28: `.verified` and a Mach-O arm64 binary in `data/murmuration-murm-gh/bin/` after one session; a01 denied, `ls` allowed (step 3 results)
- ✅ [behavioral] After the Nest push: `claude plugin marketplace update cracking-shells` then `claude plugin install murmuration@cracking-shells`; the cache holds the subdir only (or what it holds is reported); `/lab` in a scratch folder creates the lab files; the installed guard denies fixture attack `a01` and allows `ls` — 2026-10-28: all observed (step 3 results); `claude plugin list` in the scratch folder shows `murmuration@cracking-shells`
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
- Test install from GitHub (gate 3): scratch marketplace `murm-gh` (a `git-subdir` entry on `https://github.com/CrackingShells/Murmuration.git`, path `plugins/murmuration`, declared at local scope in a scratch git folder), `claude plugin install murmuration@murm-gh --scope project` (wrote only `enabledPlugins` to the scratch `.claude/settings.json`), then one `claude -p` session. `data/murmuration-murm-gh/bin/` got `murmuration` (Mach-O arm64, 636512 B) and `.verified` (binary sha256 9c013758…, the `aarch64-apple-darwin` hash in `bin/manifest.json` at 7509378). Cache `cache/murm-gh/murmuration/0.1.0/` holds the plugin subtree only (`.claude-plugin`, `LICENSE`, `README.md`, `agents`, `bin`, `hooks`, `rust`, `scripts`, `skills`, plus the loader's `.in_use`), 3.6 MB. The installed binary denied fixture `a01` and allowed `ls`. Uninstall removed the data dir but left the cache dir, which was removed by hand along with the scratch marketplace.
- Go-ahead #3, asked after the GitHub test, 2026-10-28: Eliott answered "Yes, push Nest". In a temporary worktree of `../Nest` on `main` (so `../Nest` itself stayed on `feat/list-murmuration`): `git merge --no-ff feat/list-murmuration` gave 807bc81; `claude plugin validate .` passed on the merged tree; `env -u GH_TOKEN -u GITHUB_TOKEN git push origin main` moved Nest `main` 6318249..807bc81. Temp worktree removed.
- Install from Nest (gate 4): `claude plugin marketplace update cracking-shells` passed. In a scratch git folder, `claude plugin install murmuration@cracking-shells --scope project` wrote only `{"enabledPlugins": {"murmuration@cracking-shells": true}}` to `.claude/settings.json` (the marketplace is known from user settings on this machine). After one `claude -p` session, `data/murmuration-cracking-shells/bin/` held `murmuration` (Mach-O arm64, 636512 B) and `.verified`. The cache `cache/cracking-shells/murmuration/0.1.0/` holds the plugin subtree only (`.claude-plugin`, `LICENSE`, `README.md`, `agents`, `bin`, `hooks`, `rust`, `scripts`, `skills`, `.in_use`), 3.6 MB. The installed binary denied fixture `a01` and allowed `ls`.
- `/lab Does a scratch lab initialise from the Nest install?` through `claude -p` created `__statera__/` (`user_words.md` with the question, `wave-01.md`), `__pondus__/`, `__scrupuli__/`, `__design__/framing.md`, `__instrumenta__/`, `.ignore` (4 patterns) and `.claude/settings.local.json` with `agent` and the two deny rules (0.1.0 behaviour; `lab_pi_choice` changes it), and a colgrep index. It printed plain `claude` as the next step, so `plugin_is_installed` recognises a project-scope install. A new `claude -p` there said its system prompt makes it the team leader (the PI).
- Plan puzzle, partly settled: a plain `claude -p` in the Murmuration repo, where `agent` is gone, answered that it is not the PI. The research-pi prompt seen in this side session therefore comes from the Desktop app starting it from a PI session, not from the repo settings.
- `claude plugin list` lists every install on the machine, and outside its project it shows the entry as `✘ disabled`. It never omits it, so gates must test "not enabled", not "absent".

