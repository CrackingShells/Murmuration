# Behavioral baseline and puzzle-following replay

**Goal**: Measure how the first Murmuration build behaves, on a replay with known ground truth and one external reference.
**Pre-conditions**:
- [ ] The plugin installs and passes its self-tests
**Success Gates**:
- ✅ 20 transcripts hand-labelled with the MAST taxonomy [static]
- ✅ The puzzle-following replay of the genesis question is scored against the five known missed signals [run]
- ✅ One external benchmark run (ResearchGym or Formal Conjectures) gives a reference point [run]
- ✅ The pilot KT report states spend and Wh by mode, scrupuli raised and followed, verifier catches, and which instruments the PI looked at
**References**: [R01 §Behavioral baseline](../../__reports__/genesis/11-architecture_v4.md); [R02](../../__reports__/genesis/04-benchmarks_findings_v0.md) — ranked benchmarks and log metrics

## Step 1: Hand labels
**Goal**: Calibrate failure-mode tagging before automating it
**Implementation Logic**:
Label 20 transcripts (genesis study and pilot) with MAST; measure agreement with an automatic annotator.
**Deliverables**: `baseline/labels/mast.csv`; `__reports__/baseline/00-findings_v0.md` (section Annotator agreement)
**Consistency Checks**: `test -f baseline/labels/mast.csv` (expected: PASS)
**Commit**: `test(baseline): hand-label transcripts with the MAST taxonomy`

## Step 2: Puzzle-following replay
**Goal**: The primary target: does a later wave notice what an earlier one raised?
**Implementation Logic**:
Replay the genesis question on the plugin from the same starting material; score pickup of the known missed signals and detection latency of one planted anomaly.
**Deliverables**: `baseline/replay/` (run record); `__reports__/baseline/00-findings_v0.md` (section Puzzle-following)
**Consistency Checks**: `test -d baseline/replay` (expected: PASS)
**Commit**: `test(baseline): replay the genesis study and score puzzle-following`

## Step 3: External reference and KT
**Goal**: A reference point and the pilot retrospective
**Implementation Logic**:
One external benchmark run with ledger metrics; the pilot knowledge-transfer report.
**Deliverables**: `__reports__/baseline/01-knowledge_transfer_v0.md`
**Consistency Checks**: `test -f __reports__/baseline/01-knowledge_transfer_v0.md` (expected: PASS)
**Commit**: `docs(baseline): report the pilot baseline and retrospective`
