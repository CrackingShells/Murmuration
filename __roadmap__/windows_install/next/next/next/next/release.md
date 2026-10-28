# 0.2.0 release with Windows support

**Goal**: Ship what the Windows cycle built, as 0.2.0, from Nest.
**Pre-conditions**:
- [ ] `install` done
**Success Gates**:
- ⬜ [run] Merged to `main` and pushed (Eliott's yes); the `build(bin)` commit by `github-actions[bot]` carries all 5 targets; `install_smoke` green on every row
- ⬜ `plugin.json` at 0.2.0 only after that commit is on `main` (a bump ahead of the binaries ships the Python launcher); README banner no longer says Windows is deferred
- ⬜ [behavioral] Nest entry updated and pushed (Eliott's yes); `murmuration@cracking-shells` installed from Nest on Windows and on macOS; a01 denied, `ls` allowed
- ⬜ This roadmap closed with a knowledge-transfer note
**References**: reminder `murmuration-win-release`; Nest at `../Nest`

## Step 1: Merge, binaries, bump, Nest
**Goal**: Each public step behind its own yes.
**Implementation Logic**:
Push `main`, wait for `guard-binaries` with a background `gh run watch`, check the `build(bin)` commit, bump to 0.2.0, update the README banner, update and push Nest, install on both OSes and repeat the guard check.
**Deliverables**: `plugins/murmuration/.claude-plugin/plugin.json`, `README.md`, Nest entry; knowledge-transfer note
**Consistency Checks**: `git ls-tree origin/main plugins/murmuration/bin` lists 5 targets (expected: PASS)
**Commit**: `chore(release): 0.2.0`
