# Retire the permission guard

**Goal**: Murmuration ships without its permission guard (G1–G4); the README tells users how to turn on `permissions.disableBypassPermissionsMode`, with what each scope covers measured rather than assumed.
**Pre-conditions**:
- [x] Eliott's decision, 2026-10-29: "Yes, retire it" (after the `shell_gaps` round-3 verdict and the threat-model review in `__reports__/windows_install/A1_retire_guard.md`)
- [ ] A macOS machine where Eliott can install a `managed-settings.json` (admin rights) for Step 1, chosen by Eliott
**Success Gates**:
- ⬜ [behavioral] A table under `__reports__/windows_install/` of escape forms × scope (managed, user, none) × refused or ran, observed with Claude Code: a child started with `--permission-mode bypassPermissions` and with the `--dangerously-skip-permissions` flag, each plain, with `--setting-sources project`, with `CLAUDE_CONFIG_DIR=<empty dir>`, with `--bare`, and with `--settings` carrying the key set back; plus a `cp` with a trailing `2>&1` onto `.claude/settings.json` in default mode
- ⬜ No file under `plugins/` or `.github/` refers to `permission_guard`, `murmuration guard`, `check_guard_equal` or `guard_lists`; `hooks.json` has no guard row
- ⬜ `cargo test`, `install_binary.py --selftest`, `build_manifest.py --selftest` and `check_text_io.py --selftest` pass; `murmuration budget` and `murmuration handback` decide as before on `hook_selftest`'s events
- ⬜ The README's hardening section names the setting, the managed-settings path on macOS and Linux, the user-scope fallback and its caveat from the Step 1 table, and what Claude Code already does for `.claude` (protected paths)
- ⬜ [run] CI `guard-binaries` green on all five targets; installed from Nest in a scratch project, a Bash call and a Write start no guard process
**References**: `__reports__/windows_install/A1_retire_guard.md` (evidence and impact); code.claude.com/docs/en/permissions, /permission-modes, /settings; branch `task/win-shell-gaps` (tip 31096ce, parked, not merged)

## Step 1: Measure what the setting covers at each scope
**Goal**: The README states coverage that was observed, not read off the docs.
**Implementation Logic**:
A Python probe reads its cases from a JSON file, so no bypass word appears on a command line or in a script. For each scope (managed `managed-settings.json`, user `~/.claude/settings.json`, none), it starts each escape form of the gate in a scratch folder without the plugin, with a one-word prompt and a short timeout. It records whether Claude Code refused the mode or ran in it, and the exit code and first line of stderr. The `cp … 2>&1` case runs in default mode with `-p`, where a prompt shows as a denial. Eliott installs and removes the managed file himself. The probe never writes outside the scratch folder and `~/.claude/settings.json`, and it restores that file afterwards. This step is a measurement: if a form escapes the managed scope, stop and bring the table to Eliott before Step 2.
**Deliverables**: `__instrumenta__/retire_guard_scope_probe.py` (`main`, `run_case`, `restore_user_settings`); `__instrumenta__/retire_guard_scope_cases.json`; `__reports__/windows_install/retire_guard_scopes.md` (the table)
**Consistency Checks**: `python3 -I __instrumenta__/retire_guard_scope_probe.py --dry-run __instrumenta__/retire_guard_scope_cases.json` (expected: PASS)
**Commit**: `docs(reports): measure what disableBypassPermissionsMode covers at each scope`

## Step 2: Remove the guard
**Goal**: No guard process, code, fixture or CI step is left.
**Implementation Logic**:
1. Delete `scripts/permission_guard.py`, `scripts/check_guard_equal.py`, `scripts/fixtures/guard_lists/`, `scripts/guard_selftest_payloads.json`, `scripts/guard_selftest_holes.json`, `rust/src/guard.rs` and `rust/tests/fuzz_vocab.json`.
2. `rust/src/main.rs` loses the `guard` subcommand. Delete `shlex.rs`, the `nt_*` part of `text.rs` and `tables.rs`/`gen_tables.py` only if nothing but the guard uses them; the compiler says which.
3. `hooks/hooks.json` loses the PreToolUse `Bash` row and every `Write|Edit|NotebookEdit` guard row.
4. `scripts/install_binary.py` drops the `permission_guard.py` hash check, `self_test` over the guard payloads and `m_guard`. It keeps `hook_selftest` for `budget` and `handback`, and its fallback launcher runs only `run_hook.py`.
5. `build_manifest.py` drops the file from `SCRIPTS` and `guard.rs` from the sources it lists; `check_text_io.py` drops the guard locale case.
6. `scripts/git-hooks/pre-commit` stops replaying the corpus.
7. `.github/workflows/guard-binaries.yml` drops "The Rust guard equals the Python guard". Keep the workflow's name, so its history and the release notes still point at it.

Leave `__pondus__/`, `__scrupuli__/`, `__statera__/`, `__reports__/` and `__instrumenta__/` as they are: they are the lab's record of how the guard came about. Never type a bypass word on a command line while the old guard is installed; it still denies it.
**Deliverables**: the deletions above; `plugins/murmuration/rust/src/main.rs` (`main` without `run_guard`); `plugins/murmuration/hooks/hooks.json`; `plugins/murmuration/scripts/install_binary.py` (`doubt`, `hook_selftest`, `launcher_body`, `install`, `selftest`); `plugins/murmuration/scripts/build_manifest.py` (`SCRIPTS`); `plugins/murmuration/scripts/check_text_io.py` (`selftest`); `plugins/murmuration/scripts/git-hooks/pre-commit`; `.github/workflows/guard-binaries.yml`
**Consistency Checks**: `cargo test --manifest-path plugins/murmuration/rust/Cargo.toml && python3 -I plugins/murmuration/scripts/install_binary.py --selftest && python3 -I plugins/murmuration/scripts/build_manifest.py --selftest && python3 -I plugins/murmuration/scripts/check_text_io.py --selftest` (expected: PASS)
**Commit**: `feat(guard): retire the permission guard in favour of Claude Code's own settings`

## Step 3: Document the hardening setting
**Goal**: A user who wants the protection back knows the one setting to set and what it does not cover.
**Implementation Logic**:
In `plugins/murmuration/README.md` and the root `README.md`, add a short "Hardening" section:
- `permissions.disableBypassPermissionsMode: "disable"` in managed settings, with the system path on macOS and Linux (taken from the managed-settings docs page and checked on the probe machine);
- the user-scope fallback in `~/.claude/settings.json`, with the escapes the Step 1 table shows;
- one sentence that Claude Code never auto-approves writes under `.claude` outside bypass mode.

Rewrite the "Do not install it at user scope" paragraph: its reason was the guard. Keep project scope as the advice if the other hooks (`budget`, `handback`, `user_words`) still make it right, and say so.
**Deliverables**: `plugins/murmuration/README.md` (section "Hardening"); `README.md`
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/check_text_io.py` (expected: PASS)
**Commit**: `docs(readme): point to disableBypassPermissionsMode instead of the guard`

## Step 4: Release and close the superseded leaves
**Goal**: The retirement reaches Nest, and the roadmap and reminders say what became of the guard's leaves.
**Implementation Logic**:
1. Rebase and merge with `--no-ff -F` into `main`.
2. Push, after Eliott's yes.
3. Wait for CI `build(bin)` on the five targets.
4. Bump `plugin.json` and push, after Eliott's yes. Use 0.2.0 if Eliott agrees: the release removes a feature, and the Windows release then moves to 0.3.0. Otherwise 0.1.3.
5. Install from Nest in a scratch project and check the success gate.

Then:
- mark `if_probe`, `next/if_decision`, `next/shell_gaps` and `next/next/path_gaps` blocked with `dirtree-rdm`, each with a line naming A1;
- update the windows_install Goal ("installs and guards" → "installs") and the version Gotcha;
- complete reminders `murmuration-win-shell-gaps`, `murmuration-win-if-probe` and `murmuration-win-if-decision`, and the path-gaps reminder, with a log line (scheduling-work skill);
- delete the `impl-`, `base-` and `verify-win-shell-gaps` worktrees only after Eliott says the parked branch can go.
**Deliverables**: `plugins/murmuration/.claude-plugin/plugin.json` (`version`); `__roadmap__/windows_install/README.md`; the four superseded leaves (status only)
**Consistency Checks**: `bash ~/.claude/plugins/cache/cracking-shells/managing-roadmaps/1.2.0/skills/managing-roadmaps/scripts/dirtree-rdm.sh validate __roadmap__/windows_install/` (expected: PASS)
**Commit**: `chore(release): murmuration 0.2.0`
