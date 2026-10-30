# windows_install: Knowledge Transfer (v1)

Date: 2026-10-30

## Executive Summary
- **What shipped:**
  - **0.3.0, the first release cut by CI.** It is commit 70879e3 `chore(release): murmuration 0.3.0 [skip ci]`, with tag `v0.3.0` and a GitHub Release.
  - **Windows support, tested in CI only.** The hooks exec `bin/murmuration.exe` on every OS, `TARGETS` includes Windows AMD64, and `install_smoke` has a windows-latest row.
  - **The writing-release v2.0.0 lifecycle**, which is in force from now on:
    - commitizen 4.19.2 (`.cz.toml`);
    - the `commits`, `preview` and `release` jobs in `guard-binaries.yml`, and `pr-title.yml`;
    - CONTRIBUTING.md with the lanes;
    - merge commits only.
- **The two PRs:**
  - [CrackingShells/Murmuration#1](https://github.com/CrackingShells/Murmuration/pull/1) (merge 396a4cc). It cut no release and created the v0.2.0 GitHub Release by its repair path.
  - [CrackingShells/Murmuration#2](https://github.com/CrackingShells/Murmuration/pull/2) (merge e0fc40c). It led to `build(bin)` 43b5815 with 5 targets, then the 0.3.0 bump.
- **Primary outcomes:**
  - From Nest on macOS, 0.3.0 installs `murmuration.exe`, byte-equal to CI's aarch64-apple-darwin binary, with its stamp. Its budget and hand-back hooks run in a lab.
  - The 0.2.0 files in the shared data folder are untouched.
  - The live Windows session is still open: `live_session`, reminder `murmuration-win-live`.

## Wins
- **The install self-test caught a real Windows bug.** When the binary and the Python script disagree, the installer refuses to install. That is how two Windows-only bugs surfaced before any user ran the binary:
  - Rust `lab_root` used POSIX path rules where Python uses `ntpath`;
  - Python's `os.open` without `O_BINARY` wrote CRLF.
- **A failure message that carries the diff paid for itself on the next run.** After the first round, `hook_selftest` returns a bounded, lab-masked diff instead of "step N". The CRLF difference was then legible from the CI log alone, with no Windows machine.
- **Splitting the job between two PRs worked.**
  - PR-A only added jobs and edited `on`, `needs`, `if` and `concurrency`.
  - PR-B only edited the job bodies.
  - The stacked rebase onto PR-A was clean, and GitHub retargeted PR-B to `main` when PR-A's branch was deleted.
- **The release job was right on its first run.** The `preview` notice ("nothing to release" / "a merge would release v0.3.0") matched what each push run did. The idempotent Release step repaired the missing v0.2.0 Release.
- **A distinct program name on every OS** (`murmuration.exe` with its own stamp) ended the 0.2.0 / 0.3.0 tug-of-war in the shared data folder.

## Pain Points
- **Three CI rounds on the Windows smoke row**, each finding one more difference:
  1. `shutil.SameFileError`, because the toolcache `python.exe` and `python3.exe` are the same file;
  2. the binary's path rules;
  3. the CRLF in hand-back and `harness.jsonl` writes.
- **The coordinator misdiagnosed round 3** as a text-mode `open()`. It was `os.open` without `O_BINARY`, and the implementer corrected it.
- **The implementer and the verifier disagreed about the Rust lock.** The implementer said Rust has none; the verifier said it locks. The source (`budget.rs:1027`) settled it.
- **Auto-fix was on for PR #1 only at first.** PR #2's red row sat unattended until Eliott asked.
- **My first macOS Nest check used `general-purpose` for the Agent call.** The budget hook records only `murmuration:<role>` agents, by design, so it had to be re-run with `murmuration:explorer`.

## Root Causes
- **Nothing ran the Python twin of the hooks on Windows before this cycle.** The comparison was only ever exercised on POSIX, where `os.path` is `posixpath`, a raw fd is binary, and `\n` is the line separator. Each assumption broke separately, so each round revealed exactly one.
- **The first doubt message said only "step 2".** One more round was needed just to see the difference.
- **Windows text and binary mode is per fd at the C-runtime level, not per Python API.** `os.write` looks binary-safe and is not.

## Next-cycle Changes
- **Instruction changes:**
  - A brief that touches cross-OS file I/O should say "every write in the hashed scripts sets `newline=`, or `O_BINARY` for `os.open`". `check_text_io` now enforces part of this (see Open Questions).
  - Smoke checks that exercise a hook should use a `murmuration:<role>` agent.
- **Workflow changes:**
  - When a comparison test fails, make the failure print the diff first, then fix.
  - Enable Auto-fix on every PR of a stack when the stack is opened.
- **Review process changes:**
  - When the implementer and the verifier disagree on a fact about the code, read the source line before relaying either claim.

## Artifacts to Preserve
- Gap note: `__reports__/windows_install/A2_lifecycle_and_live_split.md`.
- The commit vocabulary decision: `__reports__/release_lifecycle/commit_vocabulary_v0.md` (D1–D7).
- The commitizen config, `.cz.toml`, and the release machinery: `.github/workflows/guard-binaries.yml` (`changes`, `commits`, `preview` and `release`), `.github/scripts/manifest_matches.py` and `.github/scripts/check_trace_paths.py`.
- `plugins/murmuration/rust/src/hook.rs`: the `nt_*` helpers and the test `windows_paths_are_ntpaths`.
- The diff in `install_binary.py`'s `hook_selftest` doubt reason.

## Open Questions
- **Windows hardening for 0.3.1.** The verifier's round-4 report, the implementer's predictions and the fixes are all handed to the parent session; nothing here was a Windows measurement. In brief:
  - a CRLF hand-back under `core.autocrlf` parses as 0 sections (reproduced);
  - `python_for(Windows)` returns `"python"` rather than `python3`;
  - `budget.py` takes no lock on Windows;
  - `save_state` leaves its tmp file behind after a PermissionError;
  - the diagnostic masks only the lab's leaf;
  - `check_text_io`'s `newline` rule can be bypassed;
  - 4 clippy errors already on main, and no clippy in CI.
- **Deferred lifecycle items:**
  - pin commitizen's dependencies;
  - `persist-credentials` in the `release` job;
  - `preview` does not re-run on a body-only PR edit;
  - 0.2.0's orphaned `bin/murmuration` and `bin/.verified` have no cleanup.
- **Nest's marketplace entry still says "macOS and Linux"**, while plugin.json now says Windows is tested in CI only.
- **The live Windows session:** Defender scanning a fresh `.exe` against the 10 s hook timeout; the README's text for a Store-stub or python.org-only `python3`; a CRLF plugin checkout.
