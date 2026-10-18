# Labels and verdicts

## Claim labels (what the author ran, not what the author believes)

| Label | Means | Requires |
|:--|:--|:--|
| THEOREM | Proved | The proof, every step checkable |
| CHECKED | Verified exhaustively or numerically, not proved | The instance sizes |
| MEASURED | A number produced by code that ran end to end on data | The reproduction command and its commit |
| ESTIMATE | A formula evaluated on data; not an achieved result | The formula and its inputs |
| CONJECTURE | A pattern seen, not proved | What was observed and at which sizes |
| CITED | A statement of prior work | The identifier actually fetched, or `UNVERIFIED` |

Every factual statement in a report or a note carries a source (`[source: path@commit]`) or a
declared assumption (`[assumption: why]`). Reports end with what remains uncertain.

## Verdict vocabularies

| Verifier | Verdicts |
|:--|:--|
| reproducer | SUPPORTED · OVERSTATED (true but stated more strongly than the evidence) · UNSUPPORTED · ESCALATE |
| proof-adversary | SOUND · SOUND WITH GAP · WRONG · LABEL TOO STRONG · LABEL TOO WEAK · ESCALATE |

## The current label of a claim

- With no verdict yet, the claim stands at its author's label, marked *unverified*.
- Each verifier's latest verdict is its standing verdict.
- The current label is the weakest of the standing verdicts:
  - SUPPORTED or SOUND keep the author's label;
  - SOUND WITH GAP keeps it, marked *gap*;
  - OVERSTATED and LABEL TOO STRONG require the claim to be restated at a lower label;
  - LABEL TOO WEAK allows a higher label once the author restates it;
  - UNSUPPORTED and WRONG withdraw the claim.
- Two standing verdicts that disagree make the claim *disputed* until the PI resolves it, by a
  further check or a stated decision.

No synthesis, report or note states a claim above its current label.
