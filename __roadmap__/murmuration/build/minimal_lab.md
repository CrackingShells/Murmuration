# Minimal lab: scripts, hooks, lab commands, packaging

**Goal**: Ship the mechanical part of v6: two hook scripts, the status script, the /lab and /lab-status commands, and the plugin manifests.
**Pre-conditions**:
- [ ] Agent files and the research-loop skill written (agents_and_skills Steps 1–3)
**Success Gates**:
- ✅ Hook and status scripts pass `--selftest` on a temporary project [run]
- ✅ The plugin loads with `claude --plugin-dir .` and `/lab` initializes a temporary project [run]
- ✅ No shipped file mentions the design history (cold review) [static]
**References**: [R01 §Components, §File formats](../../__reports__/genesis/13-architecture_v6.md)

## Step 1: Hook and status scripts
**Goal**: The only code the lab needs
**Implementation Logic**:
`user_words.py` (UserPromptSubmit: append genuine prompts to `__statera__/user_words.md`; skip `<cross-session-message `, `<task-notification>`, `<agent-message from=`; no-op outside an initialized project); `resume_brief.py` (SessionStart resume|compact: print the current wave note and open puzzles); `lab_status.py` (open puzzles, current and disputed labels, spend per agent from transcripts). Standard library only.
**Deliverables**: `scripts/user_words.py` (fn `is_genuine`), `scripts/resume_brief.py`, `scripts/lab_status.py` (fn `open_puzzles`, fn `current_label`, fn `spend`)
**Consistency Checks**: `python3 scripts/lab_status.py --selftest` (expected: PASS)
**Commit**: `feat(scripts): add the hook scripts and the lab status script`

## Step 2: Commands and packaging
**Goal**: Installable plugin
**Implementation Logic**:
`/lab` (initialize: stores, framing stub, user words, project settings with `agent` and deny rules; or append a new question) and `/lab-status`; `hooks/hooks.json`; `.claude-plugin/plugin.json` via spawning-agent-plugins; local install test.
**Deliverables**: `skills/lab/SKILL.md`, `skills/lab-status/SKILL.md`, `hooks/hooks.json`, `.claude-plugin/plugin.json`
**Consistency Checks**: `test -f .claude-plugin/plugin.json` (expected: PASS)
**Commit**: `feat(plugin): package the minimal lab for local install`
