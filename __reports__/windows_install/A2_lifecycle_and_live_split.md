# Gap analysis: windows_install — adopt the release lifecycle, split the live Windows session (A2)

## Problem statement
The roadmap's last two leaves no longer describe the work.
- **`install.md` gates on a live Windows session.** Eliott has no Windows machine this week, so the leaf cannot close, and `release.md` (one level deeper) cannot start.
- **`release.md` describes a release that no longer exists.** It says 0.2.0, gates on "a01 denied" (the retired guard, A1), and cuts the release with a hand `chore(release)` bump.
- **The org release default changed.** `writing-release` v2.0.0 says releases are cut only by CI after a merge to `main`, through lanes, with no hand bumps or tags. Eliott asked, on 2026-10-30, to fold the adoption into this cycle.

## Evidence
- `next/next/next/install.md`:
  - its last gate is `[behavioral] On a real Windows machine …`;
  - Step 1 still says "implement the `if` decision", which A1 superseded.
- `next/next/next/next/release.md`:
  - its Goal says "0.2.0";
  - a gate reads "a01 denied, `ls` allowed";
  - its Commit is `chore(release): 0.2.0`;
  - Step 1 says "bump to 0.3.0". The leaf contradicts itself.
- Pre-conditions that BFS can never satisfy:
  - `next/README.md` waits on `if_probe`, which is blocked;
  - `next/next/README.md` waits on `shell_gaps`, which is blocked;
  - `next/next/next/README.md` waits on `if_decision` and `path_gaps`, both blocked.
- State of the repository on origin/main 3afb2da:
  - no tags, no CONTRIBUTING, no release tool, no commit checker;
  - `main` has no protection (`rules` [], protection 404);
  - squash and rebase merges are enabled, `merge_commit_title = MERGE_MESSAGE`, and branches are not deleted on merge;
  - 0.1.1, 0.1.2 and 0.2.0 were all hand `chore(release)` commits.
- The Windows launch: the 0.2.0 binary rows exec `${CLAUDE_PLUGIN_DATA}/bin/murmuration`. Claude Code's hooks reference says exec form on Windows needs "a real executable such as a `.exe`", and it documents no extension lookup.

## Root cause
- When the roadmap was written, a Windows machine was assumed, and the release process was the repository's own.
- A1 then removed the guard and left the gate prose that named it.

## Impact assessment
- **Scope.**
  - In: a new leaf `release_lifecycle` (PR-A), a sibling of `install` that runs in parallel.
  - In: a new leaf `live_session`, two levels below `install`. It takes over the live gate.
  - In: corrected prose in `install`, `release` and the four READMEs.
  - Out: any change to the guard leaves, which stay blocked.
- **Dependencies.**
  - `release` needs both `install` and `release_lifecycle`. The 0.3.0 release is cut by the release job PR-A adds, and the binary it releases comes from PR-B.
  - `live_session` needs `release`, because it installs 0.3.0 from Nest.
- **Risk.**
  - Without `release_lifecycle`, 0.3.0 would be the last hand-cut release, and the next repository adopting v2 would have nothing to copy.
  - Without the split, `install` cannot close this week.
  - With the split, 0.3.0 ships tested on Windows in CI only, and its banner says so.
- **Campaign close.** The knowledge-transfer note moves to `release`, so the campaign closes with 0.3.0. `live_session` stays open on reminder `murmuration-win-live`, and a `done` leaf is never reopened for it.

## Proposed solution
- **`release_lifecycle`** (PR-A, a Reviewed PR):
  - commitizen with a custom `bump_map`: feat is minor; fix and perf are patch; `BREAKING CHANGE` is minor while on 0.x;
  - `.cz.toml` at the root;
  - a `changes` job, a `commits` job, a PR preview step, and a `release` job in `guard-binaries.yml`, which keeps its name;
  - `pr-title.yml`;
  - CONTRIBUTING.md;
  - the `v0.2.0` baseline tag at 1f164ae;
  - the repository settings.

  The release job fails closed: it does not run on a red matrix, needs a `v*` tag, checks the manifest hashes, and pushes atomically.
- **`install`** (PR-B, stacked on PR-A):
  - the binary rows exec `…/bin/murmuration.exe` on every OS;
  - the stamp is keyed to that name;
  - `TARGETS` includes Windows;
  - on Windows, the doubt branch removes the binary instead of writing a POSIX launcher;
  - the smoke test runs on Windows;
  - the docs say "Windows tested in CI only".

  The Python rows are unchanged. A real `python3` on PATH is a documented Windows requirement: a launch shim measured about 70 ms more per start on macOS and was rejected.
- **`release`**: PR-B's merge makes CI commit `build(bin)` and then cut `v0.3.0`. The leaf then checks a macOS install from Nest and writes the knowledge-transfer note.
- **`live_session`**: the Windows install from Nest and a real session.

## Recommendations
1. Decide the commit vocabulary (`__reports__/release_lifecycle/commit_vocabulary_v0.md`) before `.cz.toml` is written, so the checker encodes a decision rather than a guess.
2. Push the baseline tag and change the settings before PR-A merges. Without a `v*` tag, cz counts the whole history as unreleased.
3. Keep the workflow file's name, and split its hunks between the two leaves: PR-A edits `on`, `needs`, `if` and `concurrency` and adds jobs; `install` edits the bodies of `build`, `assemble` and `install_smoke`.
