# Install path, proven in CI on Windows

**Goal**: The plugin's install path works on Windows as far as CI can show: the binary installs, its self-test passes, and the hook rows start as Claude Code spawns them. Docs say "Windows tested in CI only".
**Pre-conditions**:
- [x] `retire_guard` done (A1; it replaces `if_decision` and `path_gaps`)
**Success Gates**:
- ⬜ The 9 binary rows in `hooks.json` exec `${CLAUDE_PLUGIN_DATA}/bin/murmuration.exe`; the 3 Python rows are byte-identical to origin/main 3afb2da
- ⬜ `("Windows", "AMD64")` in `install_binary.TARGETS`; every `--selftest` in `plugins/murmuration/scripts/` passes on macOS
- ⬜ `scripts/check_text_io.py` clean
- ⬜ `claude plugin validate plugins/murmuration` passes
- ⬜ [run] PR-B's `pull_request` run (stacked on PR-A): 5 build rows and `install_smoke` green on macos-15, ubuntu-22.04 and windows-latest; `assemble` fails if the Windows binary is missing
- ⬜ Plugin description and both README banners read "macOS and Linux; Windows tested in CI only, no live session yet"; README Requirements state the Windows `python3` requirement
**References**: plan `~/.claude/plans/system-reminder-linked-sessions-now-groovy-waffle.md` § PR-B; `__reports__/windows_install/A2_lifecycle_and_live_split.md`; Claude Code hooks reference, exec form (code.claude.com/docs/en/hooks); reminder `murmuration-win-ci-release`

## Step 1: The binary as `murmuration.exe` on every OS
**Goal**: Hooks exec a documented Windows form and never touch 0.2.0's files in the shared data folder.
**Implementation Logic**:
- `hooks/hooks.json`: append `.exe` to the `command` of the 9 binary rows. The Python rows (`install_binary.py`, `resume_brief.py`, `user_words.py`) stay exactly as they are. Shell-form or shim launches were rejected because they add about 70 ms per start.
- `scripts/install_binary.py`, the minimum:
  - add `("Windows", "AMD64"): "x86_64-pc-windows-msvc"` to `TARGETS` and fix its comment and the module docstring, which names `bin/murmuration`;
  - `install()`: `dest` becomes `bin/murmuration.exe` and the stamp becomes `bin/murmuration.exe.verified`. 0.2.0 owns `bin/murmuration` and `bin/.verified`; sharing the stamp would make the two versions re-copy and re-self-test at each other's SessionStart;
  - on Windows (`os.name == "nt"`), the doubt branch removes `dest` instead of writing the POSIX launcher, and the existing note says why. The note text may say the hooks are off on Windows instead of "run as the Python scripts";
  - `selftest()`: flip the two asserts that pin "no Windows". Cover the `.exe` destination and stamp name in the existing temp-lab cases.
- Leave the rest alone. A failed `os.replace` (an exe held open by another session) already reaches `main()`'s handler, which keeps the old binary and retries next SessionStart. The `tmp<pid>` copy name changes only if the Windows CI row shows it must.
- `scripts/budget.py` self-tests 7 and 8: expect the `/bin/murmuration.exe` suffix. The file is hashed into `bin/manifest.json`, so CI rebuilds; do not touch `bin/`.
**Deliverables**: `plugins/murmuration/hooks/hooks.json`; `plugins/murmuration/scripts/install_binary.py` (`TARGETS`, `install`, `selftest`); `plugins/murmuration/scripts/budget.py` (self-tests 7–8)
**Consistency Checks**: `for s in install_binary budget handback build_manifest; do python3 -I plugins/murmuration/scripts/$s.py --selftest >/dev/null || exit 1; done && python3 -I plugins/murmuration/scripts/check_text_io.py && claude plugin validate plugins/murmuration` (expected: PASS)
**Commit**: `feat(install): install the hook binary on Windows`

## Step 2: Smoke the install on Windows in CI
**Goal**: CI shows the install and one budget hook working on all three OSes, spawned the way Claude Code spawns them.
**Implementation Logic**:
Edit only the bodies of the `build`, `assemble` and `install_smoke` jobs in `.github/workflows/guard-binaries.yml`. `release_lifecycle` owns `on`, `needs`, `if`, `concurrency` and any new jobs.
- `install_smoke`:
  - add `windows-latest` to the matrix, with a `python3.exe` copy of the runner's Python on PATH (the documented requirement);
  - every row reads `hooks.json` and runs the SessionStart install row and one PreToolUse `Agent` budget row the way Claude Code spawns them: exec form, no shell, placeholders substituted (backslashes on Windows), env `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` set;
  - assert empty stdout from the install, `murmuration.exe.verified` present, `murmuration.exe` byte-equal to the CI artifact for that target, and the budget row exits 0.
- `assemble`: Windows is required; drop the warning-only path in `reject()`.
- The Windows `build` row also runs `check_text_io.py` and the `install_binary.py --selftest`.
- Keep the replay logic in a small script under `plugins/murmuration/scripts/` only if inline YAML gets unreadable. Any new script must pass `check_text_io.py`, and is not hashed unless added to `SCRIPTS`.
**Deliverables**: `.github/workflows/guard-binaries.yml` (bodies of `build`, `assemble`, `install_smoke`)
**Consistency Checks**: `uv run --no-project --with pyyaml==6.0.2 python -c "import yaml,sys; d=yaml.safe_load(open('.github/workflows/guard-binaries.yml',encoding='utf-8')); m=d['jobs']['install_smoke']['strategy']['matrix']; sys.exit(0 if 'windows-latest' in str(m) else 1)"` (expected: PASS)
**Commit**: `ci(install): smoke-test the install on Windows`

## Step 3: Say what was tested
**Goal**: Nobody reads 0.3.0 as live-tested on Windows.
**Implementation Logic**:
- `plugins/murmuration/.claude-plugin/plugin.json` description: replace "Claude Code only; macOS and Linux." with wording that says Windows is tested in CI only, with no live session yet. Never touch `version`; the CI release job owns it.
- Root `README.md` banner (lines 5–10) and `plugins/murmuration/README.md` banner (lines 4–5): the same statement.
- Requirements (root ~93, plugin ~111): on Windows, a real `python3` on PATH. Microsoft Store Python provides one. A python.org-only install has only `python` and `py`, so the user adds a `python3` alias; without one, the install hook fails without blocking and the budget and hand-back hooks error.
- `release_lifecycle` owns README:151 and the versioning text. `live_session` owns flipping the banner after a live run.
**Deliverables**: `plugins/murmuration/.claude-plugin/plugin.json` (`description`), `README.md`, `plugins/murmuration/README.md`
**Consistency Checks**: `python3 -I -c "import json,sys; d=json.load(open('plugins/murmuration/.claude-plugin/plugin.json',encoding='utf-8')); sys.exit(0 if 'CI' in d['description'] and d['version']=='0.2.0' else 1)"` (expected: PASS)
**Commit**: `docs(readme): Windows tested in CI only`
