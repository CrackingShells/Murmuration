# What Claude Code documents for hardening the permission layer (CITED)

Source: claude-code-guide (guide-w06-perm), fetched 2026-10-21. Two pages were only partly readable
(the settings reference and env vars). Each line is CITED to the URL given; "inference" marks the
guide's own reading.

- A plugin cannot ship permission rules or `disableBypassPermissionsMode`. Plugin settings keep only
  `agent` and `subagentStatusLine` (https://code.claude.com/docs/en/plugins/manifest-reference).
  Plugin hooks run in every thread (https://code.claude.com/docs/en/hooks). Plugin subagents ignore
  `hooks`, `mcpServers` and `permissionMode` frontmatter (https://code.claude.com/docs/en/sub-agents).
- `tools:` and `disallowedTools:` take tool names. `Bash(git push *)` in `disallowedTools` removes all
  of Bash (sub-agents page). Argument rules exist only in `permissions.allow/ask/deny`. Deny rules
  match any subcommand and match past env assignments, but not `sh -c "..."` or `/usr/bin/claude`.
  The docs call them "fragile" and say a deny rule "isn't a security boundary around the program"
  (https://code.claude.com/docs/en/permissions).
- `permissions.disableBypassPermissionsMode: "disable"` works in any settings file, takes precedence
  over `--dangerously-skip-permissions`, and holds in a child that loads the same files. A child
  escapes user, project and local settings with `--setting-sources`, `CLAUDE_CONFIG_DIR` or another
  working directory. Nothing escapes managed settings: on macOS,
  `/Library/Application Support/ClaudeCode/managed-settings.json` or an MDM profile
  (https://code.claude.com/docs/en/settings-reference, /managed-settings, /cli-reference).
- Hooks: `matcher` filters by tool name. `if` holds one permission rule and the handler "only spawns
  when both filters match", checked per subcommand; it is "best-effort". The default is fail-open.
  `"onFailure": "block"` (2.1.295 or later) makes it fail closed (https://code.claude.com/docs/en/hooks).
- A child can skip hooks with `--bare`, `--safe-mode` or `--settings '{"disableAllHooks": true}'`
  (https://code.claude.com/docs/en/headless). The OS sandbox constrains Bash and its children,
  nested `claude` included (https://code.claude.com/docs/en/sandboxing).
- The guide's summary: only managed settings, plus the OS-level sandbox, hold against a child. A
  plugin cannot set them.
