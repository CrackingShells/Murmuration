# Architecture v5 — Independent design review (Opus, v0)

Date: 2026-10-18 · Reviewer: Opus, independent; the other reviewer's report was not read.
Under review: [12-architecture_v5](../genesis/12-architecture_v5.md), with its evidence ([03-KT v3](../genesis/03-knowledge_transfer_v3.md), [wave-1 note](../pi_decisions/00-wave1_note_v0.md), [probes v1](../platform_probes/01-findings_v1.md), [instrument validation](../instrument_validation/00-findings_v0.md), [benchmarks](../genesis/04-benchmarks_findings_v0.md)). Knowledge from memory is marked *[memory]*.

## 1. Verdict

**PROMISING BUT OVERBUILT: the research protocol has promise, but the infrastructure around it (libripens, about 25 hooks, the instruments, the ledger) aims at a failure that wave 1 showed is not the failure, and nothing yet shows the protocol beats a plain Claude Code session.**

The idea underneath is sound: exploration and hardening are different modes; claims carry labels; verifiers record an independent result before reading the author; puzzles are first-class objects. Hardening already worked in the genesis study (03 §Executive Summary: "no wrong theorem got through"). The trouble is that the design kept growing after its own premise moved. The genesis retrospective said signals were *filtered out* before reaching the PI; wave 1 found that 3 of 4 *did reach* the PI and were not acted on (wave-1 note §1; validation A1–A2). The failure is **uptake**, a judgement failure. Most of v5's machinery is **carriage**, built for the old diagnosis: FileChanged live notices through `asyncRewake`, raw-artifact registration, PI read events, PreCompact comparison with open scrupuli, `__examen__` mirroring (v5 §Hooks). Better carriage of signals the PI already received will not change what the PI does with them.

## 2. The strongest case FOR

- **Against a plain Claude Code session with subagents.** The genesis study *was* roughly that baseline: an Opus main thread, Sonnet workers, umbod-style contracts. Its hardening worked only because of contracts written by hand during the study: labels, reproducer, proof adversary. v5 makes them standing rules: "independence first", "a verdict changes only with evidence" (`changed_by`), "nothing reaches a deliverable above its current label" (v5 §Contracts). Plain prompting does not make these stick across waves; an append-only claim store does.
- **Against AI Scientist, Agent Laboratory and AI co-scientist** *[memory]*. Those systems aim at autonomous output (papers, ranked hypotheses). Independent assessments of AI Scientist reported hallucinated and failed experiments, and the user's own survey cites MLR-Bench (about 80% fabricated or invalid) and "Into the Unknown" (114 of 135 failed integrity) (04 §Observations). Murmuration's contribution is the reverse emphasis: **claim integrity and a human in the loop first**. Agent Laboratory itself found its human-guided co-pilot mode beat its autonomous mode *[memory]*, which supports keeping the user's words central (`framing.md §0`).
- **The PI is checkable** (v5 §New in v5). A genesis PI note cited a reproduction 13 minutes before it existed (wave-1 note §2). No system I know of verifies the orchestrator's own claims. This is cheap and real.
- **Its process can retract its own claims.** Wave 1 falsified its own diagnosis, dropped most instruments after its own pre-set criterion failed (validation §Headline), and resolved 27 of 28 platform mechanisms with runs, not docs (probes v1). That discipline is rarer than the architecture, and worth more.
- **What survives if the rest fails:** the label ladder with independence-first verification and `changed_by`; PI claims in the claim store; scrupuli with an explicit `follow`/`park` disposition; a reserved exploration budget; the probe findings as a reference on Claude Code's hook behaviour.

## 3. The strongest case AGAINST

- **Evidence base: n = 1, judged by hindsight.** One two-hour study. The "missed signals" were named after the fact by the people who designed the fix (02/03). Nobody has shown that following them would have paid off within the budget. "A quarter was too little exploration" (03 §Open Questions) is a guess. The labels in validation A were made by a Sonnet agent that knew which bullets were the targets (validation §Limits).
- **Measurement theatre, partly corrected.** The instruments failed (A: 0 of 4 at zero retention; B: no separation, n = 1 per arm). The one survivor in the brief, coverage of the PI's notes, rests on 3 data points and changes about 2× with the term list (v5 §Information instruments). The ledger still carries `energy_wh_est`, bits per message, and Wh per accepted claim, labelled ESTIMATE (v5 §Sustainability). None of this informs a decision the pilot needs.
- **Rust is justified by a number the probes made moot.** v5 rejects Python hooks for "30–60 ms" start-up (v5 §libripens). But the hot hooks now go to a resident `mcp_tool` server measured at a 3 ms median (probes row 5), where the server's language does not matter. Even the old worst case, 1,000 events × 60 ms, is one minute over a two-hour study. A Rust binary with CLI, hook and MCP front ends plus a four-target CI is the most expensive item, and its stated benefit is gone.
- **Platform dependence.** The design parses undocumented wrapper prefixes (`<task-notification>`, `<agent-message from=`), handles two hand-back shapes that depend on permission mode, filters an unnamed compaction agent (`agent_type: ""`), and relies on `asyncRewake` exit-2 semantics (probes rows 11, 24, 27, 15). Everything was verified on one version, 2.1.296, headless. Each of these can change without notice in any Claude Code release.
- **Cost.** A toy ping-pong pair cost 0.42 USD. `SubagentStart` context is paid on every resume. The `agent` setting made the first run 2.6× more expensive because of a cold cache (probes §Observations, row 13). Anthropic reported multi-agent research using about 15× the tokens of chat *[memory]*. The design budgets Wh but never asks whether the pair conversation (as opposed to the verdict) is worth its tokens.
- **Can judgement be packaged?** The PI's judgement is a 170-word persona (v5 §Agents). In genesis the best exploration came "at the user's prompting" (03 §two modes), so the judgement came from the human. A persona saying "your job is to notice" is the weakest available lever on uptake.

**Where it is most fooling itself.** The design *records* uptake (`follow` events, hand-labelled, KT only) but does nothing to *cause* it, and its own rules forbid the one cheap lever that might: "`deny` and `block` are used only by the guard and the presence gate"; "No measure enters a gate" (v5 §Hooks, §Information instruments). A wave that cannot seal until every open scrupulus is either `follow`ed or `park`ed *with a reason* forces attention without dictating judgement. The principle "never procedure where judgement belongs" is being stretched to protect the PI from the one procedure that addresses the diagnosed failure. The second self-deception is the **pilot design** (`__roadmap__/murmuration/build/pilot/baseline.md`). It runs only after the full build, has **no control arm** although the survey asked for one (04 §Observations "we need a single-agent control"; §Steering Questions), and scores a replay of the genesis question against five signals that the design documents name outright. That replay is contaminated: success there is leakage, not evidence.

## 4. The decisive test (before building `libripens`)

**Build the protocol, not the platform.** Use the agent files, the `research-loop` skill, and three plain JSONL files (claims, scrupuli, spend) that agents append to as the skill instructs, checked by a schema script of about 100 lines. Use one hook only, SubagentStop, for tokens. Add one rule: a wave note must dispose of every open scrupulus (`follow` or `park` with a reason).

- **Arms:** A = plain Claude Code (Opus main thread, generic subagents, a good research prompt); B = Murmuration-lite as above.
- **Tasks:** 3 small open questions *not* drawn from the genesis study, written by someone other than the designers. Each has 1–2 **planted anomalies that decide the correct answer** (for example, a data artefact that makes the obvious headline false), plus 2 **seeded errors** in intermediate results. Because the planted anomaly decides correctness, "uptake" is scored against outcomes, not hindsight.
- **Runs:** 3 per arm per task (18 runs). Variance is large (04 §Contradictions, ResearchGym).
- **Scoring, blind to arm:**
  1. planted-anomaly uptake: did it change a brief, plan or claim?
  2. correct final answer;
  3. seeded-error catch rate;
  4. cost in USD;
  5. the user's blind preference between paired final reports.

Estimated cost: a few hundred USD and about a week.

- **STOP** (or fall back to umbod plus the label contract) if B's anomaly uptake and correctness are within noise of A (for example, B does not win on at least 2 of 3 tasks), or B costs more than 2× for equal outcomes. Stop also if B's catch rate on seeded errors is no better than A's: then the pairs are not earning their cost either.
- **GO** if B takes up at least twice as many planted anomalies as A (say ≥ 50% against ≤ 25%), catches at least 80% of seeded errors, reaches the correct answer more often at ≤ 2× cost, and the user prefers B blind. Then build only the `libripens` pieces whose absence caused measured friction in B's runs.

## 5. What to cut to reach that test

Cut or defer:
- the Rust crate, the MCP server, CI;
- every hook except SubagentStop (and the guard, if agents edit the stores directly);
- `__examen__` mirroring, since transcripts suffice;
- every information instrument, including coverage in the brief;
- `energy_wh_est` and bits;
- the depth reviewer;
- the Agent Teams fallback;
- `PreCompact` comparisons;
- the ResearchGym, MAST and TruthInsightBench baseline;
- further naming work. Three naming reports exist (06 ×2, 10), and six architecture versions (v0–v5) were written before one line of the product.

Keep:
- the PI prompt;
- the four workers;
- labels, independence-first and `changed_by`;
- PI claims as claims;
- scrupuli with forced disposition;
- an explicit exploration reserve.

Replace the contaminated genesis replay with the held-out, planted-anomaly test above.
