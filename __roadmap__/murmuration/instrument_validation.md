# Instrument validation on the genesis study

**Goal**: Decide which information instruments may enter the PI's brief, by testing them on the genesis study, where the missed signals are known.
**Pre-conditions**:
- [ ] Read access to `/Users/hacker/Documents/explore/combinatorics_on_binary` (the genesis study)
**Success Gates**:
- ✅ Experiment A scored: whether the five known missed signals fall in the zero-retention, low-similarity cells and the followed signal does not [run]
- ✅ Experiment B scored: whether "whose words the verdict reuses" and "term first use" separate an independence-first verifier from a primed one [run]
- ✅ A decision table lists each instrument as IN BRIEF, KT ONLY, or DROPPED, with its evidence
**References**: [R01 §Information instruments](../../__reports__/genesis/11-architecture_v4.md); [R02](../../__reports__/genesis/08-information_counsel_v0.md) §4–5 — experiments A and B, pilot recipe

## Step 1: Experiment A: retention replay
**Goal**: Test anomaly retention and user-term coverage on known ground truth
**Implementation Logic**:
Extract the surprise bullets (Contradictions & Surprises, Observations) from the eight worker reports of the genesis study; mark by hand whether each reached a later PI note, amendment or brief, and whether 02-knowledge_transfer_v2 lists it as missed; compute retention, coverage and embedding similarity to the PI notes. Offline only, no agent runs.
**Deliverables**: `validation/retention_replay.py` (functions `extract_surprises`, `retention`, `coverage`); `validation/labels/surprises.csv` (hand labels)
**Consistency Checks**: `python3 validation/retention_replay.py --selftest` (expected: PASS)
**Commit**: `test(validation): replay anomaly retention on the genesis study`

## Step 2: Experiment B: planted cascade
**Goal**: Test whether pair-independence signals separate a primed verifier
**Implementation Logic**:
Two Sonnet verifier runs on one claim with a known verdict (genesis trellis row 10): one records its result before reading the author, one is shown the author's report first. Compute byte reuse from the author's text vs its own first message, and the first use of framing terms.
**Deliverables**: `validation/planted_cascade.py` (functions `byte_reuse`, `term_first_use`); `validation/runs/` (the two transcripts)
**Consistency Checks**: `python3 validation/planted_cascade.py --selftest` (expected: PASS)
**Commit**: `test(validation): plant an agreement cascade and measure it`

## Step 3: Decision
**Goal**: Fix which instruments the brief may carry
**Implementation Logic**:
Findings report with both experiments and the decision table; amend v4 if an instrument is dropped.
**Deliverables**: `__reports__/instrument_validation/00-findings_v0.md` (table Instrument decisions)
**Consistency Checks**: `test -f __reports__/instrument_validation/00-findings_v0.md` (expected: PASS)
**Commit**: `docs(validation): decide which instruments enter the brief`
