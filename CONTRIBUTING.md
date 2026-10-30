# Contributing

How a change reaches `main` and becomes a release. The plugin is `plugins/murmuration/`; everything else in the repository is the research record that designed it. CI cuts every release; nobody tags or bumps by hand.

## Commit messages

`<type>(<scope>): <subject>`, then a body that says why. The convention is checked by commitizen (`.cz.toml`, pinned to 4.19.2) in the `commits` job of `.github/workflows/guard-binaries.yml`, over the commits of each pull request and of each push to `main`, and by `.github/workflows/pr-title.yml` over the PR title. Check a range or a message yourself:

```bash
uvx --from commitizen==4.19.2 cz check --rev-range origin/main..HEAD
uvx --from commitizen==4.19.2 cz check --message "fix(hooks): stop reading a closed pipe"
```

The scope is required. There is no length cap. A trailing `!` after the scope (`feat(hooks)!:`) or a `BREAKING CHANGE:` footer marks a breaking change.

| Type | Scope | Used for | Releases |
|:--|:--|:--|:--|
| `feat` | the component, kebab or snake case (`hooks`, `lab_init`) | a new capability of the plugin, under `plugins/murmuration/**` | minor |
| `fix`, `perf` | the component | a repair or a speed-up of the plugin | patch |
| `docs`, `test`, `build`, `ci`, `chore`, `refactor`, `revert` | the component | anything, but never the research stores below | nothing |
| `claim`, `verdict` | `wNN-cN` (`claim(w09-c8)`) | a claim filed in `__pondus__/`, with its scripts and puzzles; a verdict or a decision recorded on it | nothing |
| `wave` | `wNN` | `__statera__/wave-NN.md` | nothing |
| `synthesis`, `user_words` | optional `wNN` | those two files in `__statera__/` | nothing |
| `reports` | a topic folder or an agent id (`windows_install`, `w09-i`) | `__reports__/**` and explorer hand-offs | nothing |
| `rdm` | the campaign folder | `__roadmap__/**` | nothing |
| `merge` | the scope of the work | the subject of a pull request's merge commit | nothing |

- A commit takes the type of the act it performs on its main file, not of the folder. When one commit spans stores, `__pondus__` outranks `__statera__`, which outranks the rest; better, split it. Ids are written `wNN` everywhere (`wave(w09)`, never `wave(09)`).
- A research type never touches `plugins/murmuration/**`: CI fails the range if one does. Split the commit and give the plugin part a code type.
- `build(bin)` commits binaries that ship, and releases nothing: CI makes them (`build(bin): hook binaries for <sha>`), and so does the bump (`chore(release): murmuration <version> [skip ci]`). Do not write either by hand.
- Git's own `Merge …` subjects pass. `fixup!`, `squash!` and `Revert "…"` do not: write `revert(<scope>): …` and autosquash before pushing. GitHub's "Revert" button titles its PR `Revert "…"`, which `pr-title.yml` rejects: retitle it, as `merge(<scope>): revert …`, or `fix(<scope>): revert …` when the reverted change was released and the plugin should get a patch.
- Commitizen reads every line of a message, so a line of a body that starts with `feat(x):`, `fix(x):`, `perf(x):` or `BREAKING CHANGE:` counts toward the release. A PR body becomes the merge commit's body: do not start its lines that way unless you mean it, and never write `[skip ci]` in a commit or a PR body.
- The older subjects of the research waves (`w08-c1: …`, `wave-06: …`) are history; they are not rewritten, and only new ranges are checked.

## Integration lanes

Released paths: `plugins/murmuration/**`. The release tool does not scope by path, so a `feat`, `fix`, `perf` or `BREAKING CHANGE` releases wherever it lands; give changes outside the plugin a type that releases nothing.
Release-type commits: `feat` (minor), `fix` and `perf` (patch), a `BREAKING CHANGE` (minor while the version is 0.x).

| Lane | In this repository |
|:--|:--|
| Reviewed PR | Landing a roadmap campaign or a multi-leaf branch; a `BREAKING CHANGE`; CI and release machinery (`.github/**`, `.cz.toml`, repository settings); persisted contracts: the rows of `plugins/murmuration/hooks/hooks.json`, the program name in the data directory (`${CLAUDE_PLUGIN_DATA}/bin/murmuration`), `plugins/murmuration/bin/manifest.json` and the lab layout `scripts/lab_init.py` writes; and anything in doubt |
| Self-merge PR | Any other change under `plugins/murmuration/**` that is self-contained: one component, no machinery, no persisted contract, undone by one revert. `main` has no protection and no required review, and `guard-binaries.yml` gates the PR, so the author merges after CI is green and reports the link; if anything refuses the merge, hand the green PR to the maintainer |
| Direct | Releases nothing and touches no released path: the `__*__/` stores, the root `README.md`, `probes/`. `git pull --ff-only`, integrate (a branch comes in with `git merge --no-ff`), push to `main`. If `main` refuses the push, open a PR |

Doubt takes the heavier lane. A wrong lane is caught afterwards: the `commits` job runs on every push to `main`, and a Direct push that turns out to be release-type still releases.

## Versioning

CI cuts the release after a merge to `main`; never run `cz bump`, tag, or `gh release create` locally; a missing GitHub Release is repaired by re-running the workflow (see the last bullet).

- Tool: commitizen 4.19.2, configured in `.cz.toml`. One version for the whole plugin. Tag format `v<version>` (annotated). The last `v*` tag is the baseline, so a tag is never created, moved or deleted by hand.
- The `release` job of `guard-binaries.yml` runs on every push to `main`, after the checks: it fails closed (no tag, a red build matrix, or binaries built from other sources than the tip's all stop it), bumps the `"version"` line of `plugins/murmuration/.claude-plugin/plugin.json`, commits `chore(release): murmuration <version> [skip ci]`, pushes the commit and the tag together, and creates the GitHub Release with notes from the commits. When no commit warrants a release it bumps nothing, but it still checks that the latest `v*` tag has its GitHub Release and creates it when it is missing.
- `plugin.json`'s `version` is never edited by hand.
- `build(bin)` precedes the bump: when the build ran, the `commit_back` job commits the binaries first and the bump commit lands on top, so a release always carries binaries built from its sources.
- Published to: GitHub Releases and the repository itself; users install the plugin from the repository, for example through Nest. No registry, no changelog file. Channel: `main` only.
- A release missing after a merge: read the `release` job's log, then re-run the job or run the workflow on `main` with `commit_back` ticked ("Run workflow"). If the bump was pushed but the GitHub Release failed, the re-run or dispatch creates the missing Release for the latest tag; it does not bump twice. Do not tag by hand.

## Branches

- Topic branches are named `<type>/<topic>` (`fix/hook-timeout`, `ci/release-lifecycle`) and start from an up-to-date `main`.
- Before the merge, rebase onto `origin/main` and push with `--force-with-lease`, so that CI's verdict describes what `main` will hold.
- Merge commits only: squash and rebase merges are off in the repository settings. The PR title is the merge subject, so title it `merge(<scope>): <what the branch does>` (checked by `pr-title.yml`); the PR body is the merge body, so write why there. The branch is deleted on merge.
- Pull `main` after every merge (`git pull --ff-only`): CI may have added `build(bin)` and `chore(release)` commits.
