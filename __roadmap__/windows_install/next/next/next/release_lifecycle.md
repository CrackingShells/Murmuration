# Adopt the writing-release lifecycle

**Goal**: Releases of `plugins/murmuration` are cut only by CI after a merge to `main`. The commit checker, the release job, CONTRIBUTING and the repository settings follow writing-release v2.0.0, so 0.3.0 is the first release nobody cuts by hand.
**Pre-conditions**:
- [x] `retire_guard` done (A1)
- [x] Commit vocabulary decided by Eliott (sitting 1, 2026-10-30): `__reports__/release_lifecycle/commit_vocabulary_v0.md` D1–D7 as recommended, D4 as a CI check, `bump_message` keeps `[skip ci]`
- [x] Tag `v0.2.0` at 1f164ae pushed, and repository settings applied and read back (Eliott's yes, sitting 1): PR merges are merge commits only, titled by the PR title with the PR body, branch deleted on merge; no branch protection, so the Direct lane still pushes
**Success Gates**:
- ⬜ `cz check` accepts the subjects the report's draft regex accepts (302 of 850 on 3afb2da, 103 of the 105 since 2026-10-27) and rejects its reject samples; the report's unit checks pass under the pinned cz
- ⬜ The `commits` job fails a range in which a trace type (`claim`, `verdict`, `wave`, `synthesis`, `user_words`, `reports`, `rdm`) touches `plugins/murmuration/**` (D4)
- ⬜ The `bump_map` releases only on feat (minor), fix and perf (patch), and `BREAKING CHANGE` (minor while 0.x). `refactor`, `docs`, `merge`, `rdm`, `reports` and the research types never bump, checked by `cz bump --dry-run` in a scratch clone
- ⬜ The `release` job fails closed. It does not run after a red matrix (it tolerates `skipped` only when `changes` found no gated path). It exits 1 when no `v*` tag exists. It checks the manifest hashes against the new tip of origin/main, uses `git push --atomic`, and grants `contents: write` to itself alone
- ⬜ [run] PR-A's `pull_request` run green, including `commits`, `pr-title` and `preview`
- ⬜ [run] PR-A merged as a merge commit (Eliott's yes). Its push run's `release` job reports nothing to release, and no tag beyond `v0.2.0` exists
- ⬜ CONTRIBUTING.md has the sections Commit messages, Integration lanes, Versioning and Branches, and the root README names it
**References**: plan `~/.claude/plans/system-reminder-linked-sessions-now-groovy-waffle.md` § PR-A; writing-release v2.0.0 `references/setting-up.md`, `ci-release-job.md`, `lifecycle.md`, `recovery.md` (first run); `__reports__/windows_install/A2_lifecycle_and_live_split.md`

## Step 1: Commitizen config from the decided vocabulary
**Goal**: One config holds the vocabulary, the version file and what releases.
**Implementation Logic**:
- `.cz.toml` at the repository root, with `cz_customize`:
  - `schema_pattern`: the report's draft regex (§ schema_pattern), which also accepts Git's `Merge …` subjects; scope required on code types (D6), no length cap (D7);
  - `bump_pattern` and `bump_map` per the gates. Confirm on the pinned cz that `refactor` no longer bumps;
  - `tag_format = "v$version"`, `major_version_zero = true`, `version_files` pointing at the `"version"` line of `plugins/murmuration/.claude-plugin/plugin.json`, `bump_message = "chore(release): murmuration $new_version [skip ci]"` (D5), `update_changelog_on_bump = false`.
- Pin commitizen to 4.19.2 (released 2026-10-07) in the workflow and in every check.
- Never create or push a tag; `v0.2.0` comes from sitting 1 (`git fetch --tags`).
**Deliverables**: `.cz.toml`
**Consistency Checks**: `uvx --from commitizen==4.19.2 cz check --rev-range v0.2.0..HEAD` (expected: PASS)
**Commit**: `build(release): commitizen config for the commit check and the bump`

## Step 2: CI jobs that check commits and cut the release
**Goal**: The workflow gates PRs and releases after merges, without a hand step.
**Implementation Logic**:
Edit `.github/workflows/guard-binaries.yml` and keep its name.
- Edit `on`, `concurrency`, and the `needs`/`if` lines, and add jobs. Leave the bodies of `build`, `assemble` and `install_smoke`, which belong to `install`.
- `on`: `pull_request`, `push: branches: [main]`, `workflow_dispatch` (keep the `commit_back` input). No path filters.
- `concurrency`: `group: ${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`.
- Jobs:
  - `changes` outputs `gated`: true when `plugins/murmuration/{rust,scripts,hooks}/**` or the workflow changed. `build` needs it and runs only when it is true.
  - `commits` runs `cz check --rev-range` over the PR's base..head, or the push's before..after. A second step fails when a commit in that range whose type is a trace type touches `plugins/murmuration/**` (D4; cz sees no paths). Keep it a short inline script or one under `.github/`, not in the plugin tree.
  - `preview` (PR only) runs `cz bump --dry-run --yes` and prints the version a merge would cut, or "nothing to release".
  - `commit_back` keeps its body. Its `if` stays main-only.
  - `release` needs `[changes, commits, install_smoke, commit_back]` and runs on push to main only. Its order:
    1. Fail closed: no `v*` tag means exit 1.
    2. Fetch origin/main.
    3. Check that the manifest `scripts_sha256` and `rust_sources_sha256` equal that tip's sources (`build_manifest.py sources-hash`).
    4. Run `cz --no-raise <no-bump code> bump --yes`.
    5. Compare HEAD to the bump commit, per setting-up.md.
    6. Push with `git push --atomic origin HEAD:main "$TAG"`.
    7. Run `gh release create "$TAG" --notes` from `cz changelog --dry-run "$VERSION"`.
- `release` uses `GITHUB_TOKEN` and its own `permissions: contents: write`. Every other job keeps `contents: read`, except `commit_back`, which already writes.
- `.github/workflows/pr-title.yml` runs `cz check --message "$PR_TITLE"`, with the title passed through `env`, never interpolated into the script.
- Pin every action by SHA, with the tag in a comment.
**Deliverables**: `.github/workflows/guard-binaries.yml` (`on`, `concurrency`, jobs `changes`, `commits`, `preview`, `release`, `needs`/`if` of existing jobs); `.github/workflows/pr-title.yml`
**Consistency Checks**: `uv run --no-project --with pyyaml==6.0.2 python -c "import yaml,sys; j=yaml.safe_load(open('.github/workflows/guard-binaries.yml',encoding='utf-8'))['jobs']; sys.exit(0 if {'changes','commits','preview','release'} <= set(j) and j['release'].get('permissions',{}).get('contents')=='write' else 1)"` (expected: PASS)
**Commit**: `ci(release): cut releases from CI after a merge to main`

## Step 3: CONTRIBUTING and the README
**Goal**: Humans and agents find the lanes and the commit rules in one place.
**Implementation Logic**:
- `CONTRIBUTING.md` at the root (not shipped), with these sections:
  - **Commit messages**: the decided vocabulary and what releases.
  - **Integration lanes**:
    - Reviewed PR: CI and release machinery, campaign landings, persisted contracts (`hooks.json` rows, the data-dir program name, `bin/manifest.json`, the lab layout `lab_init.py` writes), and anything in doubt.
    - Self-merge PR: other changes under `plugins/murmuration/**`.
    - Direct: the `__*__/` stores, the root README, probes.
  - **Versioning**: CI cuts the release; `plugin.json`'s `version` is never edited by hand; `build(bin)` precedes the bump.
  - **Branches**.
- Root `README.md`: the repository-layout table names `pr-title.yml` and `CONTRIBUTING.md`, and the line about the workflow (≈151) says it also checks commits and cuts releases.
**Deliverables**: `CONTRIBUTING.md`, `README.md` (repository layout)
**Consistency Checks**: `python3 -I -c "import sys; t=open('CONTRIBUTING.md',encoding='utf-8').read(); sys.exit(0 if all('## '+s in t for s in ('Commit messages','Integration lanes','Versioning','Branches')) else 1)"` (expected: PASS)
**Commit**: `docs(contributing): lanes, commit messages, versioning and branches`

## Step 4: Land PR-A
**Goal**: The machinery is on `main`, and its first run on `main` released nothing.
**Implementation Logic**:
The coordinator does this step, behind Eliott's yeses.
1. Push `ci/release-lifecycle` and open PR-A, titled `merge(ci): adopt the writing-release lifecycle`, with the PR body as the merge body.
2. Once it is green and Eliott says yes, merge it as a merge commit.
3. Watch the push run in the background. Record that `release` reported nothing to release; a harmless `build(bin)` from the workflow change may appear. If the run is red, re-run it or dispatch. If anything was released, stop and ask Eliott.
4. Pull `main`.
**Deliverables**: results in this leaf's Progress row
**Consistency Checks**: `test "$(git ls-remote --tags origin 'v*' | wc -l | tr -d ' ')" = 1` (expected: PASS)
**Commit**: `merge(ci): adopt the writing-release lifecycle`
