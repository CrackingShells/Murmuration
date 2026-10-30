# 0.3.0, cut by CI, tested on Windows in CI only

**Goal**: PR-B's merge makes CI build the binaries and cut 0.3.0; it installs from Nest on macOS with no regression, and the campaign closes with a knowledge-transfer note.
**Pre-conditions**:
- [x] `install` done (PR-B open and green on 3 OS)
- [x] `release_lifecycle` done (PR-A merged, first push run released nothing)
**Success Gates**:
- ✅ [run] PR-B merged as a merge commit (Eliott's yes, given when PR-B is green ×3 OS and its `preview` printed 0.3.0)
- ✅ [run] The push run: `build(bin)` by `github-actions[bot]` carries all 5 targets; `install_smoke` green ×3 OS; `release` committed `chore(release): murmuration 0.3.0 [skip ci]`, pushed tag `v0.3.0` and created the GitHub Release
- ✅ Manifest hashes on `v0.3.0` equal its sources (`build_manifest.py sources-hash`); `plugin.json` version 0.3.0 only on that commit
- ✅ Nest unchanged (its entry names no version)
- ✅ [behavioral] Installed from Nest in a scratch project on macOS: cache holds 0.3.0; data dir `murmuration.exe` equals CI's aarch64-apple-darwin binary and `murmuration.exe.verified` exists; no launcher note; one Agent call in a scratch lab appends `harness.jsonl` lines; 0.2.0's `bin/murmuration` untouched
- ✅ Knowledge-transfer note `__reports__/windows_install/kt_windows_install.md`; this campaign's Progress tables filled
**References**: plan `~/.claude/plans/system-reminder-linked-sessions-now-groovy-waffle.md` § Landing; writing-release `references/recovery.md`; reminder `murmuration-win-ci-release`; Nest at `../Nest`

## Step 1: Merge PR-B and let CI release
**Goal**: The release comes from CI, after the binaries.
**Implementation Logic**:
Coordinator, behind Eliott's conditional yes: after PR-A merges, PR-B retargets to `main`; merge it as a merge commit; `env -u GH_TOKEN -u GITHUB_TOKEN gh run watch` in the background, no polling; check the bot commit, the tag, the Release; pull `main`. If `release` reports nothing to release or fails, follow `recovery.md` and ask Eliott before any re-run that would push.
**Deliverables**: results in this leaf's Progress row
**Consistency Checks**: `git fetch -q --tags origin && test "$(git ls-tree --name-only origin/main plugins/murmuration/bin/ | wc -l | tr -d ' ')" -ge 6 && git rev-parse -q --verify refs/tags/v0.3.0` (expected: PASS)
**Commit**: `merge(install): install the hook binary on Windows`

## Step 2: macOS install from Nest, then close
**Goal**: No regression on the platform we can run live, and the campaign's lessons kept.
**Implementation Logic**:
In a scratchpad project, at project scope: `claude plugin marketplace update`, `claude plugin install murmuration@cracking-shells --scope project`, one headless session that runs `/lab` and one Agent call; read the data dir and the cache. Write the KT note (writing-reports, knowledge-transfer). `live_session` stays open on reminder `murmuration-win-live`.
**Deliverables**: `__reports__/windows_install/kt_windows_install.md`; Progress rows in this campaign's READMEs
**Consistency Checks**: `test -f __reports__/windows_install/kt_windows_install.md` (expected: PASS)
**Commit**: `rdm(windows_install): record the 0.3.0 release and the install from Nest`
