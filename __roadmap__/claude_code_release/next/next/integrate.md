# Integrate and probe the install path

**Goal**: The merged release branch installs through a git-subdir marketplace exactly as Nest will serve it, and the CI workflow runs green outside `main`.
**Pre-conditions**:
- [x] rust_portability, targets_contract, ci_workflow, readme_and_nest_prep merged into `release/claude-code`, each with its verifier's verdict recorded in the Progress table
- [x] The user's go-ahead #1 for a private scratch repository (CI dry run)
**Success Gates**:
- ✅ [static] Seam: the workflow's matrix equals `ALL_TARGETS`; the workflow calls `binary-name`, `sources-hash`, `--expect-targets` with the signatures build_manifest.py implements; `doubt()` looks up `binaries[<target>]` under the key the manifest writes
- ✅ [behavioral] Scratch install from a bare clone (`git clone --bare` of the branch, marketplace entry `source: git-subdir, url: file://<bare>, path: plugins/murmuration`): `claude plugin install` succeeds; a probe hook (on a throwaway commit only) prints `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA`; the root holds `.claude-plugin/plugin.json`, `rust/`, `bin/`, `LICENSE` and no `__reports__/`; `${CLAUDE_PLUGIN_DATA}/bin/murmuration` exists
- ✅ [behavioral] In that install, a `claude -p` session sees fixture attacks `a01`/`a02` of `scripts/fixtures/guard_lists/e3_attacks.json` denied (fed from the file: the coordinator's own live guard denies a command line that spells them) and `ls` allowed, lists 3 skills and 5 agents, and the `research-loop` skill text arrives with `${CLAUDE_PLUGIN_ROOT}` substituted — met in reduced form (2026-10-27): the installed binary, fed the fixture events, denied a01-a03 and allowed `ls`; the auto-mode classifier refused a nested `claude -p` with Bash allowed. The live route is observed instead in the coordinator's own session, whose Bash calls go through the same hook rows (its guard denied a G3 probe on 2026-10-27), and again after the switchover in `publish`, where the session reads `./plugins/murmuration`.
- ✅ [behavioral] Binary path: a throwaway commit with locally built macOS binaries and their manifest installs state `binary` (`.verified` present) through the same git-subdir route
- ✅ [run] CI dry run in the scratch repo, `workflow_dispatch` with `commit_back=false`: 4 Unix rows green, `bin-and-manifest` artefact keys equal the Unix targets (plus Windows if its row was green), `install_smoke` green; Windows outcome reported either way
- ✅ [run] Scratch marketplace, plugin install, scratch repo removed afterwards (`claude plugin list` shows no scratch entry)
**References**: `__roadmap__/claude_code_release/README.md` Gotchas (`${CLAUDE_PLUGIN_ROOT}` verified only under `--plugin-dir` before this leaf)

## Step 1: Seam review
**Goal**: The three dispatched leaves agree where none of them owned the joint.
**Implementation Logic**:
1. Read the merged workflow against `build_manifest.py`'s CLI and `install_binary.doubt()`.
2. Fix mismatches as small mechanical commits; anything larger goes back to the owning implementer.
**Deliverables**: fixes only where needed, in `.github/workflows/guard-binaries.yml` or `plugins/murmuration/scripts/`
**Consistency Checks**: `actionlint .github/workflows/guard-binaries.yml && cd plugins/murmuration && for s in permission_guard budget handback lab_init lab_status user_words resume_brief build_manifest install_binary; do python3 -I scripts/$s.py --selftest >/dev/null || exit 1; done` (expected: PASS)
**Commit**: `fix(release): align the workflow, manifest and installer contracts`

## Step 2: git-subdir probe install
**Goal**: Settle whether `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` resolve under a marketplace install, before anything is public.
**Implementation Logic**:
1. Throwaway branch `probe/install` (never merged): one extra SessionStart row that writes both variables to a file in the scratchpad.
2. Bare clone into the scratchpad; scratch marketplace with a throwaway name; `claude plugin marketplace add`, `claude plugin install murmuration@<scratch>`, then a scratch folder and `claude -p` with the probe questions; read the probe file and the data dir.
3. A second throwaway commit with locally built macOS binaries plus `build_manifest.py` output; reinstall; check `.verified`.
4. Record results in the Progress table; remove the scratch marketplace and plugin.
**Deliverables**: Progress table notes in `__roadmap__/claude_code_release/next/next/README.md`
**Consistency Checks**: `claude plugin list 2>&1 | grep -c scratch | grep -qx 0` (expected: PASS)
**Commit**: `docs(roadmap): record the git-subdir probe install`

## Step 3: CI dry run in a private scratch repository
**Goal**: The workflow runs on GitHub before it can touch the public `main`.
**Implementation Logic**:
1. With the user's yes: create a private repo, push `release/claude-code` there as its `main`, dispatch with `commit_back=false`.
2. Read each job's conclusion and the artefact listing with `gh run view`; download `bin-and-manifest` and compare its manifest keys to the targets.
3. Fix and re-run until green; delete the scratch repo after the user confirms.
**Deliverables**: Progress table notes with the run URL and job conclusions
**Consistency Checks**: `gh run list --repo <scratch> --workflow guard-binaries.yml --limit 1 --json conclusion -q '.[0].conclusion' | grep -qx success` (expected: PASS)
**Commit**: `docs(roadmap): record the CI dry run`
