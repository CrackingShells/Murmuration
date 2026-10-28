# Install path and first Windows session

**Goal**: The plugin installs and runs on Windows, observed end to end in a real session.
**Pre-conditions**:
- [ ] `if_decision` and `path_gaps` done
**Success Gates**:
- ⬜ Hook rows start on Windows (`python3` is usually absent; the binary is `murmuration.exe`), with `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` substitution checked
- ⬜ The `if` decision implemented
- ⬜ `("Windows", "AMD64")` in `install_binary.TARGETS` (its self-test updated) and a windows row in `install_smoke`
- ⬜ `scripts/check_text_io.py` clean: every text open and stdin/stdout explicit UTF-8
- ⬜ [behavioral] On a real Windows machine, installed from a branch (git-subdir): a session starts, `/lab` works, `.verified` and `murmuration.exe` in the data dir, the guard denies `a01` and a Write to `.claude\settings.json`, allows `dir` / `ls`
**References**: reminder `murmuration-win-install`; `plugins/murmuration/scripts/install_binary.py` (comment on `TARGETS`)

## Step 1: Launcher, targets, smoke, then the real session
**Goal**: Unblock the Windows install and watch it work.
**Implementation Logic**:
Choose how hook rows start on Windows; implement the `if` decision; extend `TARGETS` and `install_smoke`; run `check_text_io.py`; install on Windows and run the behavioural checks.
**Deliverables**: `plugins/murmuration/hooks/hooks.json`, `plugins/murmuration/scripts/install_binary.py`, `.github/workflows/guard-binaries.yml`; results in this leaf
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/install_binary.py --selftest` (expected: PASS)
**Commit**: `feat(install): install the guard binary on Windows`
