# Gap analysis: windows_install — retire the permission guard (A1)

## Problem statement
The guard (G1–G4, `permission_guard.py` and `rust/src/guard.rs`) was built in wave 6 to stop an agent from loosening Claude Code's permission layer. The Windows leaf `shell_gaps` ran three implementer rounds and three adversarial verifier rounds. Each round closed shell spellings and found new ones, and the work cannot converge: the branch `task/win-shell-gaps` (tip 31096ce) adds 1,715 lines to a guard that is already about 1,640 lines of Python and 2,680 of Rust. Eliott decided on 2026-10-29 to retire the guard. In its place, the README documents `disableBypassPermissionsMode`.

## Evidence
- **What the guard has actually caught.** The recorded transcripts in `~/.claude/projects/*` hold 432 guard denials. Nearly all of them come from deliberate test runs: the wave-6 and wave-7 arenas and probe labs, and Murmuration's own development sessions. The organic ones come from one research project, youzuoqi: a subagent writing a harness for child `claude` runs used a bypass flag and `CLAUDE_CONFIG_DIR` in plain text. None was obfuscated, and none was specific to Windows.
- **What Claude Code already does** (docs read on 2026-10-29, code.claude.com/docs/en/permissions and /permission-modes):
  - `.claude` and `.git` are protected paths, "never auto-approved except in bypassPermissions mode".
  - The targets of Bash output redirects (`>`, `>>`, `2>`) and of `tee` are checked against protected paths, as if Claude wrote the file.
  - `permissions.disableBypassPermissionsMode: "disable"` refuses bypass mode. It "works from any scope", and it cannot be overridden in managed settings.
- **Cost of the current approach.**
  - Every Bash call starts a guard process, and its rows carry `onFailure: block`, so a guard that cannot run blocks every Bash call.
  - Every rule exists twice, in Python and in Rust, kept equal by `check_guard_equal.py`.
  - Round 3 alone cost about 290k subagent tokens and 1h45 of agent time.
  - The worst-case Rust time on long inputs rose from 0.05 s to 1.1 s on the branch.
- **Open on 0.1.2 today (F1, round-3 verifier).** `cp x.json .claude/settings.json 2>&1` passes the installed binary. Outside bypass mode, Claude Code's protected-path check still prompts for it. In bypass mode nothing stops it.

## Root cause
The guard tries to read every shell's spelling of a write as text. A reader of that kind has no end on Windows, where cmd, PowerShell, wsl and the built-in tools each spell writes differently. The settings that close the actual risk (bypass mode, protected paths) already exist in Claude Code.

## Impact assessment
- **Scope.** Removed: the guard, its fixtures, its equality machinery, its hook rows, and its part in the binary install self-test and in CI. Kept: the `murmuration` binary for `budget` and `handback`.
- **Supersedes** `if_probe`, `next/if_decision`, `next/shell_gaps` and `next/next/path_gaps`: all four change or probe the guard.
- **What is lost.**
  - Protection becomes opt-in, where the guard came with the install.
  - With the setting at user scope only, a child `claude` started with `--setting-sources project` or `CLAUDE_CONFIG_DIR=…` may not load it (G2); `retire_guard` Step 1 measures this.
  - A broad allow rule on an interpreter (`Bash(python3 *)`) still lets a script write a settings file without a prompt. The guard caught only some of those forms.

## Proposed solution
The leaf `retire_guard.md`:
1. Probe, on a machine with managed settings, which escape forms the setting survives at managed scope and at user scope.
2. Remove the guard from code, hooks, install and CI.
3. Document the setting, managed first and user scope as the fallback with the measured caveat.
4. Release.
