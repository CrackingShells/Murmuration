# Probe hook if filters on Windows

**Goal**: Know which Windows path forms start the guard's Write/Edit/NotebookEdit rows, whose `if` globs (e.g. `Write(**/.claude/settings*.json)`) gate them.
**Pre-conditions**:
- [ ] A real Windows machine with Claude Code, chosen by Eliott (a GitHub runner would need an API key secret)
**Success Gates**:
- ⬜ [behavioral] A findings report under `__reports__/` with a table of path forms × fired / not fired: backslash, forward slash, mixed case, trailing dot or space, ADS (`settings.json::$DATA`), UNC (`\\?\C:\…`, `\\localhost\c$\…`), 8.3 short name (`SETTIN~1.JSO`)
- ⬜ The report lays out the options for `if_decision`: keep `if`, widen it, or drop it
**References**: reminder `murmuration-win-if-probe`; `plugins/murmuration/hooks/hooks.json`; `../claude_code_release/README.md` Gotchas, "Hook if filters on Windows"

## Step 1: Stub plugin and the path forms
**Goal**: Observe, not infer, what the undocumented `if` normalisation does on Windows.
**Implementation Logic**:
Install a stub plugin whose hook only logs its stdin, with the same `if` rows as the guard; drive Write and Edit at each path form; record which forms start the hook.
**Deliverables**: `__reports__/windows_install/` findings report
**Consistency Checks**: every form in the gate list has a row in the report (expected: PASS)
**Commit**: `docs(reports): record which Windows path forms start the hook if filters`
