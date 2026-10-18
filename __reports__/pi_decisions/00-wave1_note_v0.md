# Wave 1 — PI note (v0)

---
type: open-question
topic: pi_decisions
date: 2026-10-18
version: v0
prior-version: none
decision-required: confirm
---

The user's question this wave serves: make the multi-agent system "reliably emerge the behavior
we want", which is judgement-led exploration plus hardening, with weak signals flowing back.

## What doesn't add up

1. **Our own diagnosis was half wrong.**
   - The genesis retrospective (02/03) said the missed signals were *filtered out* by
     word-capped summaries before they reached the PI.
   - The retention replay shows that three of the four mappable missed signals **did reach** a
     PI note or the outline. Only m-sequence ≡ de Bruijn never did.
   - The PI saw them and filed them as curiosities. The failure is **uptake**, not carriage.
   - Two consequences:
     - anomaly retention measures the wrong thing, so the KT metric becomes uptake (did a signal
       change a brief or a plan?);
     - "summary starvation" is not the whole story, which weakens the PI read-ratio premise.
   [source: __reports__/instrument_validation/00-findings_v0.md, puzzles 2 and 4]
2. **The PI is the least-verified node.**
   - My genesis note PI02 (committed 13:38:40) cited the reproduction as having re-derived
     pointer-entropy invariance. The reproduction was committed at 13:51:58: I recorded an
     expected result as a finding.
   - PI02 also dropped a qualifier ("best ρ ≥ 0.976 on images and weights": 0.976 is one RGB
     palette effect).
   - PI note 00 stated as fact an absence that the literature report had flagged as weak
     evidence.
   - The design verifies every worker claim and no PI claim.
   [source: git log of the genesis repo; instrument_validation puzzles 5–7]
3. **Priming helped the verifier.**
   - In the planted cascade, the run shown the author's report first found the better diagnosis
     (the 1e-3 tolerance behind "46 of 51").
   - The independent run did not, but it also did not anchor on the author's number.
   - This supports the pair protocol as designed: independent result first, *then* read and
     converse. It does not support pure isolation. One run per arm, so this is a CONJECTURE.
   [source: instrument_validation puzzles 12–15]
4. **The instruments are fragile.**
   - The counsel's coverage numbers do not replicate (0.23/0.09/0.12 vs 0.50/0.17/0.08). The
     term list is underspecified, and 7 of the 12 terms are generic.
   - The counsel's "combinatorics appears in no report" is false by substring; it holds for the
     PI notes only.
   - Only coverage of the PI's notes survives into the brief, and on weak evidence.
5. **The platform mostly holds, with specific holes.**
   - `mcp_tool` handlers run in a median of 3 ms (vs 188 ms for bash+jq). They ignore `async`,
     are skipped at SessionStart(startup/resume), and fail at process-exit SessionEnd.
   - FileChanged cannot reach the PI's context. Only an `asyncRewake` exit-2 wakes an idle PI.
   - UserPromptExpansion needs the scoped matcher `murmuration:lab`.
   - The `agent` setting replaces the 6,259-character default prompt with the agent body, and
     nine default blocks are dropped.
   - Direct messaging between subagents works, by agent id.
   [source: __reports__/platform_probes/00-findings_v0.md]

## Blocker

The `claude` CLI is logged out on this machine, so ten model-backed probes did not run (named
plugin pairs, SubagentStart/Stop fields, PostToolUse on SendMessage/Agent, hand-back shape,
PostCompact, the behavior diff under `agent`). Logging in is the user's step. Then
`probes/run_model_probes.sh` runs 7 sessions capped at 0.60 USD each.

## Amendments planned for architecture v5 (after the model probes)

| Change | From |
|:--|:--|
| PI decision notes carry their factual claims as `pondus` claims with labels and sources, checkable like any worker claim; the depth reviewer reads PI notes too | point 2 |
| KT metric "anomaly retention" → **uptake** (signal → changed brief/plan), hand-labelled per study; retention dropped | point 1 |
| Brief instruments: only coverage of the PI's notes, with the term list written down per study; everything else KT-only or dropped (validation decision table) | point 4 |
| Live back-flow via an `asyncRewake` command hook (exit 2) instead of a FileChanged `systemMessage` | point 5 |
| `mcp_tool` only on hot synchronous events; `command` at SessionStart(startup/resume), SessionEnd and anything async; scoped matchers (`murmuration:*`) | point 5 |
| Pair protocol unchanged (independent first, then converse); note the priming evidence; replicate B with 3–5 runs per arm in the pilot | point 3 |
| Check the nine default-prompt blocks the `agent` setting drops; restore the needed ones through a skill pointer | point 5 |
