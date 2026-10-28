# Windows CI row green

**Goal**: The `build (windows-latest, x86_64-pc-windows-msvc)` row of `guard-binaries` passes, so a Windows binary is built, compared with the Python guard and assembled.
**Pre-conditions**:
- [x] 0.1.1 on `origin/main` (72a61d0) with the 4 Unix binaries committed by CI
**Success Gates**:
- ⬜ [run] A `workflow_dispatch` of `guard-binaries` on this leaf's branch (`commit_back=false`) has the Windows row green
- ⬜ [run] `assemble` in that run accepts the Windows artefact: its `targets:` line lists `x86_64-pc-windows-msvc`, and no "left out of bin/" warning appears
- ⬜ [observation] The Windows row's "The Rust guard equals the Python guard" table is recorded here, with any difference between the two guards under nt named as a finding (not hidden)
**References**: reminder `murmuration-win-ci-green`; runs 40633506781 and 40659559118 (Windows row red); `../claude_code_release/next/next/next/publish.md` step 2 results

## Step 1: Escape the temp dir where the harness pastes it into JSON text
**Goal**: `{T}` substitution yields valid JSON whatever the separators in `T`.
**Implementation Logic**:
1. `check_guard_equal.py` replaces `{T}` in JSON text in two places: the fixture files in `registered_events` (the crash: `D:\a\…` becomes invalid escapes, `JSONDecodeError: Invalid \escape: line 90 column 21`) and every payload in `run_one` (fuzz cwd `{T}`, file paths `{T}/…`). The second does not crash: it makes those payloads invalid JSON, which both guards reject the same way, so on Windows they would test nothing while the step stayed green.
2. Substitute `json.dumps(T)[1:-1]` (`json_fragment`) in both. On POSIX it equals `T`, so the events are byte for byte what they were and the Unix rows decide exactly as before.
3. Run the check quick and full locally: both must say "gated sets equal".
4. `permission_guard.py` `selftest()` has the same pattern but CI never runs `--selftest`; it stays untouched (it is a hashed input: a change would need new binaries and a 0.1.2 bump). Recorded in Gotchas of the campaign README.
**Deliverables**: `plugins/murmuration/scripts/check_guard_equal.py` — `json_fragment`, `registered_events`, `run_one`
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/check_guard_equal.py --quick` (expected: PASS)
**Commit**: `test(guard): escape the temp dir the equality check pastes into JSON`

## Step 2: Prove it on the Windows runner from a branch
**Goal**: The gates above, observed in a real run, without touching `main`.
**Implementation Logic**:
1. With Eliott's yes, push only this branch and run `env -u GH_TOKEN -u GITHUB_TOKEN gh workflow run guard-binaries.yml --ref <branch> -f commit_back=false`; watch it with a background `gh run watch`.
2. Read the Windows row's equality table and `assemble`'s `targets:` line; record both here.
3. Landing on `main` is a separate yes. `check_guard_equal.py` is not a hashed input (`build_manifest.SCRIPTS`), so the manifest stays valid; the push to `main` still starts the workflow (`scripts/**`), whose `commit_back` then adds the Windows binary to `bin/`.
**Deliverables**: run id and results in this leaf
**Consistency Checks**: `env -u GH_TOKEN -u GITHUB_TOKEN gh run view <id> --json jobs` shows the Windows row `success` (expected: PASS)
**Commit**: `docs(roadmap): record the first green Windows row`
