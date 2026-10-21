# The managed setting, checked (2026-10-22, 00:08–00:14 JST)

- 00:08: the user created `/Library/Application Support/ClaudeCode/managed-settings.json` with sudo.
  It is root-owned, mode 644, and reads `{"permissions": {"disableBypassPermissionsMode": "disable"}}`
  as valid JSON. MEASURED.
- The CLI on PATH is Claude Code 2.1.304, a native arm64 binary. Its strings name this folder for
  macOS, the file name `managed-settings.json`, and the check
  `permissions.disableBypassPermissionsMode === "disable"`. CHECKED by reading strings, not by tracing
  code.
- 00:12: the user ran `claude -p "say ok"` with the skip-permissions flag. It answered "ok" with
  empty stderr. Its transcript (`3c5c3eec…`, entrypoint `sdk-cli`) records `permissionMode:
  bypassPermissions`. **The setting did not stop a `-p` run from entering bypass mode.** MEASURED, n = 1.
- 00:13: a default-mode debug run (haiku, no bypass flag) shows that the file is read: "this machine
  has managed settings"; "Watching for changes in setting files … /Library/Application
  Support/ClaudeCode/managed-settings.json"; "Settings changed from policySettings". MEASURED.
- Not known: why a loaded setting did not refuse the flag. It may be enforced only in interactive
  sessions, or at another point, or not at all in this build. The docs fetched by claude-code-guide
  say the key "takes precedence over the flag" (CITED, `permission_mechanisms.md`).
- Consequence: the plugin's permission guard (w06-c13) stays. The `-p` path is the very one it
  stopped 21 of 21 times. Removing its Bash row waits until a bypass attempt is shown to be refused.
