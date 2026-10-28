# lab stops setting agent

**Goal**: `/lab` never writes or restores `"agent"` in `.claude/settings.local.json`; it prints how to open as the PI instead.
**Pre-conditions**:
- [x] Eliott's decision, 2026-10-28, answering the plan questions: "Never set it"
**Success Gates**:
- ⬜ [run] `python3 -I plugins/murmuration/scripts/lab_init.py --selftest` passes, with asserts that no init, append or restore writes `agent`, that an existing `agent` (any value) is left byte-for-byte, and that the deny rules are still written and restored
- ⬜ [run] On a fresh scratch folder, `lab_init.py` writes `settings.local.json` holding only `permissions.deny` (plus any keys already there), and its "Next:" text names `"agent": "murmuration:research-pi"` and `claude --agent murmuration:research-pi`
- ⬜ [behavioral] The adversarial verifier `verify-lab-pi-choice` closes with no open finding
**References**: `plugins/murmuration/scripts/lab_init.py` (`merge_settings`, `restore_settings`, `next_steps`, `initialize`, `run`, `selftest`); `plugins/murmuration/skills/lab/SKILL.md` sections 2 and 3

## Step 1: Drop the agent key from lab_init and the lab skill
**Goal**: The lab stops choosing the main-thread agent for the user.
**Implementation Logic**:
`merge_settings` keeps merging the deny rules and stops touching `agent`: no set, no restore. If an `agent` is already present in either settings file, it stays as it is, and the notes may say what it names. `next_steps` prints both ways to open as the PI: the settings line for `.claude/settings.local.json`, and `claude --agent murmuration:research-pi`, prefixed with `--plugin-dir <root>` when the plugin is loaded from a folder rather than installed (`plugin_is_installed`). Check that `plugin_is_installed` recognises a project-scope install from `cracking-shells`, and report it if not. Update the module docstring and `SKILL.md` sections 2 and 3 so no text promises the key: after an init the skill tells the user how to open as the PI. Selftests: rewrite the asserts that expect `agent`, and keep every assert on the deny rules, the shared settings and invalid JSON. Report a spec defect rather than building on it.
**Deliverables**: `plugins/murmuration/scripts/lab_init.py` (`merge_settings`, `restore_settings`, `next_steps`, docstring, `selftest`); `plugins/murmuration/skills/lab/SKILL.md`
**Consistency Checks**: `python3 -I plugins/murmuration/scripts/lab_init.py --selftest` (expected: PASS)
**Commit**: `feat(lab): stop setting the main-thread agent; print how to open as the PI`
