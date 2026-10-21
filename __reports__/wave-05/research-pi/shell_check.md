# PI check: tool resolution under CLAUDE_CODE_SHELL=/bin/bash (2026-10-21, claude 2.1.304, haiku, n = 1 per shell)

Command, run from /private/tmp/murmuration-w05/research-pi/ for each shell (bash with `CLAUDE_CODE_SHELL=/bin/bash` exported):
`claude -p 'Run the Bash command `sh ./probe.sh` once and reply with its raw output only.' --model haiku --allowedTools 'Bash(sh ./probe.sh)' --output-format json`
probe.sh = shell_probe.sh beside this file.

| shell | wall s | total_cost_usd | resolved |
|:--|--:|--:|:--|
| zsh | 16.49 | 0.0064 | python3=/Users/hacker/miniforge3/bin/python3; git=/usr/bin/git; uv=/Users/hacker/.local/bin/uv; colgrep=/Users/hacker/.cargo/bin/colgrep; claude=/Users/hacker/.local/bin/claude; /Users/hacker/miniforge3/bin/python3 |
| bash | 10.54 | 0.0059 | python3=/Users/hacker/miniforge3/bin/python3; git=/usr/bin/git; uv=/Users/hacker/.local/bin/uv; colgrep=/Users/hacker/.cargo/bin/colgrep; claude=/Users/hacker/.local/bin/claude; /Users/hacker/miniforge3/bin/python3 |

## Addendum (2026-10-21, after the user asked what the speed-up costs): environment under each shell

Command: as above, with `env_probe.sh` (beside this file; prints variable NAMES only, PATH entries
and the resolution of 15 tools). n = 1 per shell, headless, launched from the PI's Desktop session.

- Variable names: identical, except `CLAUDE_CODE_SHELL` itself under bash.
- PATH entries: identical.
- node, npm, npx, conda, mamba, brew, cargo, rustc, java, gh, docker: identical paths.
  nvm, go, R, julia: absent under both.

Reading: in this setting, PATH comes from the parent process, which already carries the login
environment. The zsh snapshot only adds what `.zshrc` defines as shell code: aliases, functions
(`conda activate`, `nvm`), options and zsh syntax.
- Not measured: aliases and functions, because a `sh` script cannot see them.
- What bash gives up: those functions, and the PATH that `.zshrc` would add for a run started
  from a bare environment (cron, launchd).
- What it gains: 5–10 s per run, and a deterministic shell under parallel launches. With zsh, 17 of
  35 snapshots timed out there (explorer-w05-f), so commands already ran without a complete
  `.zshrc`.
