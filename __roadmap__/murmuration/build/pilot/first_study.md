# First real study on the plugin

**Goal**: Run one genuine research question chosen by the user end to end with Murmuration.
**Pre-conditions**:
- [ ] The plugin installs locally
**Success Gates**:
- ✅ Every wave note is sealed with a disposition for each open puzzle [static]
- ✅ The study's claims carry labels and independent verdicts [static]
**References**: [R01 §File formats](../../../__reports__/genesis/13-architecture_v6.md)

## Step 1: Run the study
**Goal**: Real use, in a separate project
**Implementation Logic**:
The user picks the question and the project folder; `/lab` initializes it; the study runs in its own session.
**Deliverables**: the study's own project folder (outside this repository); a pointer in `__reports__/pilot/00-first_study_v0.md`
**Consistency Checks**: `test -f __reports__/pilot/00-first_study_v0.md` (expected: PASS)
**Commit**: `docs(pilot): record the first study run on the plugin`
