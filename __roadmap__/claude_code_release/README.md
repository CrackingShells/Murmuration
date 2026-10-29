# claude_code_release

## Context
First public release of Murmuration as a Claude Code plugin, a pure-dev cycle (no waves, no claims) following the user's decisions of 2026-10-26/27: one repository with the plugin in `plugins/murmuration/` and the research record kept beside it; Claude Code only, stated in a README banner; conditional compilation for macOS, Linux and Windows with binaries built and committed by GitHub Actions, Windows installs deferred; listed in Nest only (`murmuration@cracking-shells`). Two later dev cycles take other harnesses. It replaces the publishing part of `__roadmap__/murmuration` (amendment A2 there).

## Reference Documents
- [R01 settings record](../../__design__/settings_record/README.md) — why `.claude/settings.local.json` is no longer tracked (Phase 0, on `main`, commits 86fa0ca and b28572b)
- [R02 linux_live](../../__reports__/linux_live/00-findings_v0.md) — the first live Claude Code session with the plugin on Linux (banyan, 2026-10-29)

## Goal
`main` is on GitHub with CI-built binaries and `claude plugin install murmuration@cracking-shells` works on macOS and Linux.

## Pre-conditions
- [x] Remote `https://github.com/CrackingShells/Murmuration` exists, public and empty (`gh api`, 2026-10-26)
- [x] `.claude/settings.local.json` untracked on `main`, on-disk copy unchanged (`cmp` against the backup, 2026-10-27)
- [x] Integration branch `release/claude-code` in its own worktree; the coordinator's live session keeps reading the plugin from the `main` checkout's root until the switchover in `publish`

## Success Gates
- ✅ Each dispatched leaf passes its gates and an adversarial verifier's attacks
- ✅ The git-subdir probe install shows `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` resolved and the guard live
- ✅ `origin/main` holds a `build(bin)` commit by CI and `install_smoke` passed in that run
- ✅ `murmuration@cracking-shells` installs from Nest and the installed guard denies fixture attack `a01` (G1, a `claude` bypass flag) and allows `ls`
- ✅ Nothing is pushed to GitHub or Nest without the user's go-ahead (three: scratch CI repo, `main`, Nest)

## Gotchas
- `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` were verified only under `--plugin-dir` before this campaign; a missing `${CLAUDE_PLUGIN_DATA}/bin/murmuration` blocks every Bash call (guard rows use `onFailure: block`). `integrate` settles this with a git-subdir install from a bare clone.
- Once a hashed source changes (relocate step 3 already does, through `rust/Cargo.toml`), local `doubt()` reports "sources changed" and installs the Python launcher until CI's `build(bin)` lands. Correct, slower.
- The org's `check_plugin.py` is advisory here: its rules exist for cross-harness portability, which this cycle does not claim. On `plugins/murmuration` at db28904 it reports 47 problems: 43 "hook command should start with `uv run --no-project --quiet python`" (the hooks use exec form, `python3 -S -I` and the binary), 3 "the plugin root must be the only placeholder" (rows that also use `${CLAUDE_PLUGIN_DATA}`), 1 "`PostToolBatch` not every harness knows". `claude plugin validate plugins/murmuration` passes.
- Nest entry: committed on `../Nest` branch `feat/list-murmuration` (c00093d), not pushed; `claude plugin validate` passes on it.
- Version stays `0.1.0` under the new identity `murmuration@cracking-shells`. Bump `plugin.json` only after CI's `build(bin)` commit for the same sources is on `main`: a cached copy does not refresh under an unchanged version, and a bump ahead of the binaries ships the launcher.
- The guard is a permission-bypass guard (G1 to G4 in `permission_guard.py`'s docstring), not a process guard: an earlier draft of these gates said it "denies `pkill`", which it never did (the `pkill` rule is the user's own, enforced outside this plugin). Gates use fixture attack `a01` instead.
- Early probe, 2026-10-27, release tip 888b18b plus a throwaway SessionStart dump, installed from a bare clone through a `git-subdir` scratch marketplace (`murm-probe`, project scope in the scratchpad): exec-form `args` got `CLAUDE_PLUGIN_ROOT=~/.claude/plugins/cache/murm-probe/murmuration/0.1.0` (holds only the plugin subtree, no `__reports__`) and `CLAUDE_PLUGIN_DATA=~/.claude/plugins/data/murmuration-murm-probe`; `install_binary.py` ran and wrote the Python launcher (sources changed, as expected); that launcher denied `a01`/`a02` and allowed `ls`. Not yet seen: a live session routing a Bash call through the hook (the auto-mode classifier refused a nested `claude -p` with Bash allowed); `integrate` repeats the probe on the merged tree.
- **Windows guard binary: path semantics fixed, not yet run on Windows** (windows_paths merged a77b78b; the paragraph below records what was wrong before it). Residuals from verify-windows-paths, all low and Windows-only: a mixed reading of dots-and-spaces segments (one kept, another vanishing) is allowed, which matters only if Win32 reads such segments by kind or position; G4 does not apply the second reading; `claude.ps1.` with a trailing dot passes the G1 regex for one flag form. Real Win32 behaviour must be probed in the Windows-install cycle.
- **Before windows_paths, the Windows guard binary was not trustworthy** (rust_portability verifier, 2026-10-27): `rust/src/text.rs` path helpers (isabs, basename, normpath, join) follow posixpath, while `permission_guard.py` on Windows uses ntpath. A Windows build would ALLOW `Write C:\Users\u\.claude\settings.json` and `Edit .claude\settings.json`, which the Python guard denies (forward slashes are denied by both). Harmless in this release: `install_binary.TARGETS` has no Windows entry, so `murmuration.exe` is built and committed but never installed. The Windows-install cycle must make those helpers OS-aware and add backslash cases before Windows enters `TARGETS`.
- Integration probe, 2026-10-27, merged tip d8b3747 on throwaway `probe/install` with locally built darwin binaries and a manifest from `build_manifest.py --expect-targets aarch64-apple-darwin,x86_64-apple-darwin` (`doubt()` None), installed from a bare clone through scratch marketplace `murm-probe2`: `${CLAUDE_PLUGIN_ROOT}`/`${CLAUDE_PLUGIN_DATA}` resolved; the data dir got `.verified` and a Mach-O `murmuration` (binary path); the installed binary denied attacks a01, a02, a03 and a Write to `.claude/settings.json`, and allowed `ls`; a headless session listed the 5 agents and the 2 model-visible skills (`lab` is `disable-model-invocation`, present on disk), and the `research-loop` text arrived with the cache path substituted. Still not observed: a live session routing a Bash call through the hook (the auto-mode classifier refuses a nested `claude -p` with Bash allowed). Both probe installs and their cache and data dirs were removed.
- Text encoding on Windows: the plugin scripts open text and read stdin in the locale encoding (cp1252 on Windows); the hooks run `python3 -S -I`, and `-I` ignores `PYTHONUTF8`, so only explicit `encoding="utf-8"` and byte-level stdin/stdout fix it. Seen on the CI Windows row, 2026-10-27; in windows_paths' scope.
- Linux binaries are built on ubuntu-22.04 and link glibc dynamically (2.35): on an older glibc the self-test fails and the installer falls back to the Python launcher (safe, slower). A static musl target would remove that; not in this cycle.
- **Linux: observed live, 2026-10-29** ([R02 linux_live](../../__reports__/linux_live/00-findings_v0.md)). 0.1.2 was installed from Nest on banyan (x86_64, glibc 2.39, Claude Code 2.1.309, in a desktop-app session over ssh). It runs the compiled binary: `.verified` is written and its sha256 matches the manifest. `/lab`, the guard (a01 denied, `ls` allowed), a live subagent through the budget and handback hooks, and prompt recording all pass. Defect: `user_words.py` stores a `<system-reminder><session-mentions>` block that the app appends *after* an @-mention, because it cuts platform blocks only at the start of the prompt. Not covered: aarch64, glibc below 2.35, musl.
- Hook `if` filters on Windows (impl-windows-paths, docs reading only, 2026-10-27): permission rules are documented to normalise Windows paths to POSIX, and changelogs 2.1.162/2.1.176 fixed backslash and case-variant matching, but hook `if` normalisation of case, trailing dots, ADS and UNC forms is not documented, and `Write(...)` in `if` is undocumented. A guard that denies every Windows form is still bypassed if the `if` glob never starts it. The Windows-install cycle must settle this with a stub-hook probe on Windows, or drop `if` from the guard rows, before Windows enters `TARGETS`.
- Guard gaps found by verify-windows-paths, 2026-10-27, all present before this campaign (both guards agree on each):
  - **Posix, after posix_redirects (fd6088d):** closed or denied by default by `posix_gaps` (merge 2d554c1): nested `sh -c`/`bash -c $'..'` strings, scripts fed to a shell, `${..:-".."}` targets, variable, substitution and glob targets, NUL (both guards now deny it, in a command or a path), and the ~5M-character command (length caps and a work budget, the same in both guards). Claude Code 2.1.295 CHANGELOG: `onFailure: "block"` makes a hook that "times out" block the action; before that, and without it, a timed-out PreToolUse hook lets the call through (code.claude.com/docs/en/hooks, Timeouts). **Accepted residuals, all allowed before posix_gaps:** a name built from pieces, base64, a file's contents or a backslash-newline split; a directory reached by `cd -`, `$OLDPWD`, `popd`, `pushd +N`, `cd "$P"`, or assigned through `read`, `printf -v`, arrays or globs; `$XDG_CONFIG_HOME/claude/..` and `$PWD/settings.json`; a shell named only at run time (`| $(which sh)`, `| ksh93`, `| toybox sh`, `xargs -I{} sh -c {}`, `| ${SHELL:-sh}`); `sh -c "true; $(..)"` (the unknown-string test is anchored); `bash /dev/fd/3 3<<<`, `sh /dev/./stdin`; a doubly nested string with an escaped substitution after `cd ..`; `builtin command cd`, `builtin -- cd`; brace expansion and extglob/zsh globs; interpreter one-liners. **Accepted over-denies (fail closed):** `m*.log`, `managed-*`, `*settings*.log` globs; `| sh -n`; `eval "$(ssh-agent -s)"`, `bash --version` or `sh -c "$CMD"` in a command that also names a settings file; `S=.claude/settings.json; jq . $S > $OUT`; heredoc prose that quotes a pipe-fed shell beside a settings path; `(cd .claude); ..`; `pushd -n .claude`; about 5000 `$(..)` in one command, 12000 commands under a 400-character cwd, a `cd` target over 1024 characters. The pure-Python nt reading still takes up to 3.1 s on a few many-redirection forms at 190000 characters (385 s before); the Windows cycle owns it.
  - **Posix, fixed by posix_redirects (fd6088d):** the G3 redirect regex missed a quoted target containing a space (a home folder such as `First Last`) and the `>|` clobber operator, so such a Bash write to a settings file is allowed. Not fixed in `windows_paths`, whose gate requires posix unchanged.
  - **Windows cycle:**
    - G2 is not seen through `cmd /c`, `powershell -c` or a `set`/`$env:` assignment;
    - 8.3 short names (`SETTIN~1.JSO`) and Windows builtins (`copy`, `move`, `Set-Content`) are not read as writes;
    - G4 ignores `.ps1`/`.bat`/`.cmd` scripts.
  - **Performance, closed by posix_gaps (merge 2d554c1):** a command of about 5M characters made the Python guard time out at 20 s (Rust allowed). Both guards now deny it as too long (MAX_CHARS 200000 for Bash, WRITE_MAX_CHARS 10,000,000 for Write/Edit) or too complex (a shared work budget); worst measured time at the caps is 1.37 s (Python) and 0.47 s (Rust).
- Research records (`probes/`, `validation/`, `__instrumenta__/`) cite root-relative paths such as `scripts/permission_guard.py@<commit>`. They are read at their commit and are not rewritten.
- Subagents: Grep and `grep -r` are blocked by the colgrep hook; use colgrep `index_build` on the worktree path, then `search` with that path. No mamba or uv on this machine: system `python3` 3.12 (stdlib, `-I`), cargo 1.99.

## Status
```mermaid
graph TD
    relocate_plugin[Relocate the plugin into plugins/murmuration]:::done
    next[Portability, contracts, CI, docs]:::inprogress
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `relocate_plugin.md` | 📄 Leaf Task | ✅ Done |
| `next/` | 📁 Directory | 🔄 In Progress |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
