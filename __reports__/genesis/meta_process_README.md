# meta_process

Retrospectives on how the study was run, as opposed to what it found.

## Round 00
- [00-knowledge_transfer_v0.md](00-knowledge_transfer_v0.md). Process retrospective of the imbrication campaign: division of work, verification archetypes, re-planning choke points, proposed agent-configuration patterns.

## Round 01
- [01-knowledge_transfer_v1.md](01-knowledge_transfer_v1.md) — After PI review: validator was fixed upstream (stale 1.0.0 cache); PI agent vs skill; why Python displaced Wolfram; reassessment triggers; asymmetric doubt; perseverance and re-angling.

## Round 02
- [02-knowledge_transfer_v2.md](02-knowledge_transfer_v2.md) — Withdraws v1's decision rules: the PI role is judgement; lists the weak signals that were present and not acted on, and traces the cause to summaries that starved the PI of raw material.

## Round 03
- [03-knowledge_transfer_v3.md](03-knowledge_transfer_v3.md) — **latest KT**. Consolidated retrospective organized around exploration (attention) vs hardening (mechanics), with the spend split by mode.
- [03-architecture_v0.md](03-architecture_v0.md) — The `research-lab` plugin design: AGENTS.md, 8 agents, 3 skills, 4 mechanical hooks, MCP routing, file channels for claims, spend and puzzles.

## Round 04
- [04-design_review_v0.md](04-design_review_v0.md) — Outside review of the `research-lab` design: verdict table, lifecycle holes (resume, disputed verdicts, budget gone, non-converging pairs), a minimal-lab cut with costs, the author ↔ verifier pair protocol with Claude Code mechanisms labelled VERIFIED/ASSUMED, failure modes as positive instructions, and where the design drifts back toward v1.
- [04-benchmarks_findings_v0.md](04-benchmarks_findings_v0.md) — Survey of 68 benchmarks, datasets and instruments (research agents, math with tools, multi-agent traces, scientific-process behaviors) for a behavioral baseline of the research-lab system: tables by family, a ranked 5-item baseline, 18 log metrics to extract from our own runs, and a list of behaviors no benchmark measures.

## Round 05
- [05-architecture_v1.md](05-architecture_v1.md) — Integrates the PI notes (pairs, loops, positive failure-mode instructions, `/lab` UX), the outside review and the benchmark survey; five-agent pilot cut; puzzle-following replay as the new instrument.

## Round 06
- [06-stores_umbod_sustainability_v0.md](06-stores_umbod_sustainability_v0.md) — umbod reuse (contracts, not CLI), store entry schemas, per-writer segments + derived index, Rust utility, sustainability levers.
- [06-naming_classical_v0.md](06-naming_classical_v0.md) — Latin weighing family: expensa, statera, pondus, examen, scrupuli, libripens.
- [06-naming_transmission_v0.md](06-naming_transmission_v0.md) — transmission traditions: pinkas, shilu, pratigya, sugya, kushya, sofer.

## Round 07
- [07-architecture_v2.md](07-architecture_v2.md) — Consolidated design with the Latin weighing names (expensa, statera, pondus, examen, scrupuli, libripens), per-writer stores, the Rust `libripens` tool, umbod composition, sustainability and the baseline.

## Round 08
- [08-information_measures_draft_v0.md](08-information_measures_draft_v0.md) — Draft proposal: information theory as hook-level instruments for the cost of communication between agents (compression-based bits, conditional complexity) and for each agent's position in the problem space (divergence maps, drift from the user's words, pair convergence, semantic entropy).
- [08-information_counsel_v0.md](08-information_counsel_v0.md) — Outside counsel on the draft: verdict table (compression measures kept and narrowed; JSD and MI-as-number dropped at this sample size; drift measured as coverage of the user's terms), three additions (anomaly retention, PI read ratio, label reliability), a pilot on this repository's own reports, the cheapest Rust version, and display rules that keep the measures from becoming targets.

## Round 08 (lead)
- [08-hooks_leverage_v0.md](08-hooks_leverage_v0.md) — the 33 hook events mapped onto lab functions; mcp_tool handlers.

## Round 09
- [09-architecture_v3.md](09-architecture_v3.md) — v2 plus the full hook surface and the information instruments that passed the counsel's pilot (bits, coverage of the user's words, anomaly retention, PI read ratio, label reliability).

## Round 10
- [10-naming_repo_v0.md](10-naming_repo_v0.md) — repository name for the lab in Cracking Shells: recommends **Murmuration** (alternatives Rookery, Skein).

## Round 11
- [11-architecture_v4.md](11-architecture_v4.md) — **latest, build reference**. v3 as the repository `CrackingShells/Murmuration`, with the model policy: the PI is the only Opus agent, every other agent is Sonnet by default.

## Status
Complete for this cycle.
