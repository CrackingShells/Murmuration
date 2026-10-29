# What `disableBypassPermissionsMode` covers on this Mac

Measured 2026-10-29 with `__instrumenta__/retire_guard_scope_probe.py` (cases in `retire_guard_scope_cases.json`), Claude Code 2.1.304, 27 child runs, USD 0.09. Each child `claude -p` (haiku) is asked to run `touch marker` with no allow rule; a default-mode `-p` child is denied that, so a written marker means bypass was in force.

## The local managed file is ignored on org accounts
`/Library/Application Support/ClaudeCode/managed-settings.json` held the key, yet bypass ran. The account receives server-managed settings (`~/.claude/remote-settings.json`, one key: `channelsEnabled`), and the managed tier is first-wins by default: "Claude Code uses the highest-ranked source that delivers at least one policy key and ignores the rest" (code.claude.com/docs/en/managed-settings). Server-managed ranks above the file, so the file is silently inert.

## Results with no effective setting
| Escape form | default mode (control) | bypass, `--permission-mode` | bypass, skip flag |
|:--|:--|:--|:--|
| plain | denied | ran | ran |
| `--setting-sources project` | denied | ran | ran |
| `--settings` key null / false / "allow" | denied | ran | ran |
| `.claude/settings.local.json` key null | denied | ran | ran |
| `CLAUDE_CONFIG_DIR` empty | not logged in | not logged in | not logged in |
| `--bare` | not logged in | not logged in | not logged in |

On macOS the login lives in the Keychain, so a child with another config dir or `--bare` cannot reach the API at all.

## Writes into `.claude` in default mode, `Bash(cp *)` allowed
| Command | Result |
|:--|:--|
| `cp src.json out.json` (control) | written |
| `cp src.json .claude/settings.json` | denied |
| `cp src.json .claude/settings.json 2>&1` | denied |

Claude Code's protected-path check covers the `cp` destination with or without a trailing redirect, so the round-3 finding F1 needs no guard once bypass mode is off.

## Not measured
Eliott set the key in `~/.claude/settings.json` himself on 2026-10-30 and closed the measurement there: the user-scope column and any managed column were not run. The README states the setting at user scope and does not claim which escape forms it survives.
