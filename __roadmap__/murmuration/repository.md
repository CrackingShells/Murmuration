# Local repository scaffold

**Goal**: Create the Murmuration repository locally with Cracking Shells conventions and its genesis record.
**Pre-conditions**:
- [x] Architecture v4 approved
**Success Gates**:
- ✅ AGPL-3.0 licence, gitignore, README, design pointer, genesis reports and this roadmap are committed
- ✅ Nothing exists on GitHub yet
**References**: [R01 §Package layout](../../__reports__/genesis/11-architecture_v4.md) — repository conventions and layout

## Step 1: Licence and gitignore
**Goal**: Match sibling repositories
**Implementation Logic**:
Copy the AGPL-3.0 licence and gitignore from Pinion; ignore Rust build output and derived SQLite indexes.
**Deliverables**: `LICENSE`, `.gitignore` (entries `target/`, `*.sqlite`)
**Consistency Checks**: `test -f LICENSE` (expected: PASS)
**Commit**: `chore(repository): add the AGPL-3.0 license and gitignore`

## Step 2: Genesis record
**Goal**: Keep every design decision traceable
**Implementation Logic**:
Import the meta_process reports from the originating study, with their links intact, plus an index.
**Deliverables**: `__reports__/genesis/README.md` (reading order), `__reports__/genesis/11-architecture_v4.md`
**Consistency Checks**: `test -f __reports__/genesis/11-architecture_v4.md` (expected: PASS)
**Commit**: `docs(genesis): import the reports that produced the design`

## Step 3: README and design pointer
**Goal**: Point newcomers at the build reference first
**Implementation Logic**:
README with the murmuration image and status; `__design__/README.md` listing the PI-fixed decisions.
**Deliverables**: `README.md` (section Status), `__design__/README.md` (table Decisions fixed by the PI)
**Consistency Checks**: `test -f __design__/README.md` (expected: PASS)
**Commit**: `docs(readme): introduce Murmuration and point to its build reference`

## Step 4: Roadmap
**Goal**: Open the build roadmap one wave at a time
**Implementation Logic**:
Use dirtree-rdm 1.2.0 from the playbook; detail wave 1, keep build nodes coarse until wave 1 reports.
**Deliverables**: `__roadmap__/murmuration/README.md` (nodes repository, platform_probes, instrument_validation, build)
**Consistency Checks**: `bash $DIRTREE validate __roadmap__/murmuration/` (expected: PASS)
**Commit**: `chore(roadmap): open the Murmuration build roadmap`
