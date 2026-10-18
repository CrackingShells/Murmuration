# Information measures for the lab — draft proposal (v0)

Date: 2026-10-18 · Draft by the design lead, for outside counsel before folding into architecture
v3. It extends [07-architecture_v2.md](07-architecture_v2.md). References here are quoted from
memory and are UNVERIFIED.

## Idea (from the PI)

Use information theory (entropy, mutual information, semantic entropy) as hook-level instruments
for two things: (1) the cost of communication between agents; (2) where each agent stands relative
to the others in the problem space, as revealed by the language it uses.

## Proposal

**1. Communication cost in bits, not tokens.**
- Description length of a message = its compressed size (zstd with a dictionary trained on the
  project corpus).
- New information to the receiver: C(msg | receiver context) = C(context + msg) − C(context), the
  compression-based conditional complexity behind normalized compression distance (Cilibrasi &
  Vitányi).
- Redundancy = 1 − C(msg | ctx) / C(msg).
- Intended uses: flag briefs that paste what the receiver already has, and handbacks that add
  almost nothing new.

**2. Position in the problem space.**
- Represent each agent per wave as a distribution over the framing doc's vocabulary (symbols and
  named objects), backed by a small local sentence-embedding model (all-MiniLM, CPU) for meaning
  beyond exact terms.
- Jensen–Shannon divergence between agents, laid out in 2D per wave: a map of the team and its
  movement.
- Mutual information between agent identity and terms: which concepts are distinctive of which
  agent.
- Divergence between wave notes and the user's own words (`framing.md §0`): drift from the
  question.
- Pair independence: the verifier's independent first `__examen__` entry vs the author's claim.
  Early convergence of the verifier's language onto the author's is a signature of an agreement
  cascade.
- Novelty of each scrupulus relative to existing claims: real anomaly or restatement.

**3. Semantic entropy** (Kuhn et al.; Farquhar et al., *Nature* 2024).
- Sampled N answers, clustered by mutual entailment, entropy over the clusters. This is too
  expensive per message.
- Free variant: when author and verifier, or parallel explorers, *independently* state a result,
  the semantic entropy across those independent statements measures how unsettled the claim is.
- The full sampled version is used only on disputed claims and on claims at synthesis.

**Guard.**
- Measurements are taken silently; agents are never told they are scored on them (Goodhart).
- Nothing gates on them. They surface as one or two lines in the session brief, for the PI and
  the human to judge.
- Words are not positions; the embedding complements the vocabulary.

**Placement.**
- `libripens hook subagent-stop` appends a `comm {from, to, kind, tokens, bits, new_bits,
  redundancy}` event to `__expensa__`.
- An offline `libripens map --wave` produces embeddings, divergences, a 2D map and an anomaly
  table.
- Semantic entropy is computed on demand.
- The brief gains a line of position signals after the scrupuli and before spend.

## Open questions for counsel

- Are these the right measures, and are they estimable on small samples (tens of messages per
  wave)? What are their biases?
- Are there better-founded alternatives, e.g. surprisal under a reference language model,
  information bottleneck views of delegation, rate–distortion of briefs, or channel capacity
  between PI and team?
- How should they be validated against ground truth (e.g. this study's known missed signals and
  the agreement-cascade cases)?
- What is the cheapest version that still carries signal?
