# First real project as a lab

**Goal**: One real project of Eliott's, chosen with him, runs as a Murmuration lab from `murmuration@cracking-shells` at project scope.
**Pre-conditions**:
- [ ] `ship_update` done (0.1.1 installed from Nest)
- [ ] The project chosen with Eliott, quoted here
**Success Gates**:
- ⬜ [run] In the project, `.claude/settings.json` enables `murmuration@cracking-shells`, and `claude plugin list` there shows it at project scope
- ⬜ [run] `claude plugin list` in a non-lab folder shows no `murmuration` entry
- ⬜ [behavioral] `/lab <question>` creates the lab files; a new session opened with `claude --agent murmuration:research-pi` is the PI; a plain new session is not
- ⬜ [behavioral] A Desktop worktree of the project loads the plugin without a new install (or what it asks is recorded)
- ⬜ [behavioral] A plain new session in the Murmuration repo, not a side session, is or is not the PI; the result is recorded against the plan's puzzle
**References**: plan "Decisions" 1 to 3; the `Murmuration` Reminders list

## Step 1: Install and open the lab
**Goal**: The scaffold in daily use.
**Implementation Logic**:
1. Choose the project with Eliott (his Reminders project lists). Install with `claude plugin install murmuration@cracking-shells --scope project` from its folder, and commit `.claude/settings.json` there only if Eliott says so.
2. Eliott runs `/lab <his question>`; check the files and the deny rules.
3. Open the PI as the README says; check that one guard deny fires there (fixture `a01` fed through Python to the installed binary).
4. Open a Desktop worktree of that repo and record whether the plugin loads.
5. Run the Consistency Check from the project folder.
6. Append log lines to the Reminders item through the scheduling-work writer.
**Deliverables**: this leaf's Results; the project's `.claude/settings.json` (in that project, on Eliott's word)
**Consistency Checks**: `claude plugin list 2>&1 | grep -q 'murmuration@cracking-shells'` (expected: PASS)
**Commit**: `docs(roadmap): record the first real project set up as a lab`
