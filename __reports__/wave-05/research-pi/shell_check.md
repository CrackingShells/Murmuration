# PI check: tool resolution under CLAUDE_CODE_SHELL=/bin/bash (2026-10-21, claude 2.1.304, haiku, n = 1 per shell)

Command, run from /private/tmp/murmuration-w05/research-pi/ for each shell (bash with `CLAUDE_CODE_SHELL=/bin/bash` exported):
`claude -p 'Run the Bash command `sh ./probe.sh` once and reply with its raw output only.' --model haiku --allowedTools 'Bash(sh ./probe.sh)' --output-format json`
probe.sh = shell_probe.sh beside this file.

| shell | wall s | total_cost_usd | resolved |
|:--|--:|--:|:--|
| zsh | 16.49 | 0.0064 | python3=/Users/hacker/miniforge3/bin/python3; git=/usr/bin/git; uv=/Users/hacker/.local/bin/uv; colgrep=/Users/hacker/.cargo/bin/colgrep; claude=/Users/hacker/.local/bin/claude; /Users/hacker/miniforge3/bin/python3 |
| bash | 10.54 | 0.0059 | python3=/Users/hacker/miniforge3/bin/python3; git=/usr/bin/git; uv=/Users/hacker/.local/bin/uv; colgrep=/Users/hacker/.cargo/bin/colgrep; claude=/Users/hacker/.local/bin/claude; /Users/hacker/miniforge3/bin/python3 |
