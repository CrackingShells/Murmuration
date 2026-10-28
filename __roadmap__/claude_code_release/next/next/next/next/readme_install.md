# README install on macOS

**Goal**: The plugin README tells a macOS user how to install from Nest at project scope, what `/lab` creates, and how to update.
**Pre-conditions**:
- [x] Decisions 1, 3 and 4 of the plan (project scope, no `agent` key, update path)
**Success Gates**:
- ⬜ [run] `claude plugin validate plugins/murmuration` passes with no README warning
- ⬜ [run] The README names `murmuration@cracking-shells`, `--scope project`, `claude plugin marketplace update cracking-shells` and `claude plugin update murmuration@cracking-shells`
**References**: `plugins/murmuration/README.md`; `plugins/murmuration/skills/lab/SKILL.md` (what `/lab` creates)

## Step 1: Install, lab and update sections
**Goal**: A stranger on macOS can go from nothing to a lab.
**Implementation Logic**:
Add "Install on macOS": `claude plugin marketplace add CrackingShells/Nest`, then `claude plugin install murmuration@cracking-shells --scope project` from the project folder; the one-line `/plugin install murmuration --marketplace CrackingShells/Nest` the validator asks for; and why not user scope (the guard would deny settings edits and some `claude` flags in every project). Rewrite "Use": `/lab` creates `__statera__/`, `__pondus__/`, `__scrupuli__/`, `__design__/`, `__instrumenta__/`, a `.ignore` block, the deny rules in `.claude/settings.local.json`, and no `agent` key; then open as the PI with `claude --agent murmuration:research-pi` or the settings line. Add "Update": marketplace update, then plugin update with `--scope project`, then restart. Requirements stay.
**Deliverables**: `plugins/murmuration/README.md`
**Consistency Checks**: `! claude plugin validate plugins/murmuration 2>&1 | grep -q 'has no line that installs'` (expected: PASS)
**Commit**: `docs(readme): install from Nest at project scope, what /lab creates, updates`
