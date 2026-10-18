# Murmuration architecture v5 — Independent review (Fable, v0)

Date: 2026-10-18 · Reviews [12-architecture_v5.md](../genesis/12-architecture_v5.md) against
[03-knowledge_transfer_v3.md](../genesis/03-knowledge_transfer_v3.md),
[00-wave1_note_v0.md](../pi_decisions/00-wave1_note_v0.md), the platform probes v1, the
instrument validation v0 and the benchmark survey. Written without reading the other reviewer.
Claims from memory of the field are marked [memory].

---
type: findings
topic: design_review
date: 2026-10-18
version: v0
prior-version: none
key-metric: verdict PROMISING BUT OVERBUILT; decisive test costs under 50 USD and needs no libripens
decision-required: confirm
---

## 1. Verdict

**PROMISING BUT OVERBUILT, with the promise in the half that is already proven and the build
aimed at the half that has no evidence yet.** The hardening contracts (label ladder, verifier
pairs, independence first, `changed_by`, PI claims checkable) worked in the genesis study and
are worth keeping in any form. The exploration half, which is the stated reason for the whole
project ("judgement-led exploration… with anomalies flowing back", v5 §Executive Summary), rests
on a diagnosis that wave 1 overturned and on a mechanism that was not re-derived afterwards.
The infrastructure (Rust binary, resident MCP server, 25 hook events, five stores, SQLite index,
cross-platform CI) is sized for a product with users, not for a hypothesis with n = 1.

The reasoning, in one paragraph. KT v2/v3 said the PI was *starved* of raw material by
word-capped summaries, so v0–v4 built carriage: raw artifacts to the PI, scrupuli in the brief,
`asyncRewake` on FileChanged. Wave 1 then found that 3 of the 4 mappable missed signals *did
reach* a PI note and were filed as curiosities (wave-1 note §1; validation A2, "MENTION"). The
failure is uptake. v5 responded by renaming the metric (retention → uptake) and adding
`mention`/`follow` events, but every mechanism that acts on the PI still acts on carriage. Nothing
in v5 makes an Opus PI *act* on a signal it has already seen, and the one data point on record (an
Opus PI that saw the signals and did not act, then cited a result 13 minutes before it existed,
wave-1 note §2) says the default behaviour is the failure mode. The design's own principle,
"identity where it is judgement", forbids the only cheap lever (a forcing function) and has not
tested the lever it chose (a 150-word prose identity). That is where the plan is weakest, and it
is exactly the part no amount of `libripens` will fix.

## 2. The strongest case FOR

**Genuinely new or valuable relative to the baselines:**

- **Versus a single Claude Code session with subagents:** the *claims registry with derived
  labels* (current label = weakest open verdict from distinct verifiers, `disputed` when they
  disagree; v5 §Stores) and the *pair protocol* (independent result first, then converse;
  `changed_by` required to revise a verdict). A plain session has neither, and in the genesis
  study these are what "caught every overstatement" (KT v3 §Executive Summary). The
  per-writer append-only JSONL layout (`__<store>__/<wave>/<agent_id>.jsonl`) is cheap, correct,
  and git-mergeable: good engineering with no downside.
- **Versus AI Scientist, Agent Laboratory, co-scientist-style systems [memory]:** those are
  pipelines (idea → experiment → paper) or tournaments (generate, debate, rank), with review as
  a final LLM pass. Murmuration's distinct ideas are (a) the two-mode budget with an explicit
  exploration reserve and a *portfolio of cheap probes* instead of one bet (KT v3 §What carries
  forward), (b) anomalies as a first-class channel (`__scrupuli__`) with a hand-labelled uptake
  metric, and (c) the PI's own factual claims verified like a worker's. (c) is, as far as I know
  [memory], not done anywhere else, and wave 1 showed it is needed.
- **Versus umbod:** umbod already has cycles, INTENT briefs, honesty tags, a verifier before
  `finish-cycle` and a senior reviewer. The real delta is in-session pairs, the claims/verdict
  derivation, scrupuli uptake and the user's words kept verbatim (`framing.md §0`). That delta is
  small enough to live inside umbod as a skill plus agent files plus two JSONL files.
- **The epistemic hygiene is good and should be said plainly:** instruments are never targets or
  gates, counts come with denominators, nothing is ranked, the KT report must say whether any
  measure changed a decision (v5 §Information instruments). Wave 1 dropped 7 of 11 instruments
  on evidence. Most multi-agent projects never do this.

**What survives even if the rest fails:** the hardening contracts as a skill; the per-writer
JSONL store layout; the 27-of-28 platform probe findings (`platform_probes/01-findings_v1.md`),
which are useful to anyone writing Claude Code plugins and are independent of Murmuration; the
finding that LLM-PI failure is uptake not carriage (a real result about the model, not about the
plumbing); and the benchmark survey with its gap table (`04-benchmarks_findings_v0.md` §Gaps).

## 3. The strongest case AGAINST

- **Unvalidated premise, n = 1, diagnosis revised twice.** One two-hour study, 10 Sonnet runs,
  2.6 M tokens (KT v3). The diagnosis went rules (v1) → starvation (v2/v3) → uptake (wave 1). Five
  architecture versions and about 4,400 lines of genesis reports were produced in one calendar
  day against that evidence. Design velocity exceeds evidence velocity by an order of magnitude.
- **The mechanism does not match the diagnosis.** See §1. The brief, FileChanged rewake, raw
  artifact registration and read-ratio all address carriage. Uptake is addressed only by a
  KT metric, which is measurement, not cause.
- **"Judgement" as identity prose is untested and, on the record, unlikely to be enough.** The
  design treats any rule on the PI as "the v1 mistake" (KT v2 §The correction; v5 Risks, "PI
  prose decays into rules"), which makes the principle unfalsifiable: no mechanical lever is
  admissible on the one failure that matters. What is known to move exploratory behaviour in
  agents [memory] is structural: more independent samples plus selection (best-of-k,
  tournaments), and forced enumeration before choice. The design has the first (probe
  portfolio) but makes it secondary to the prose; the second it rejects. Note that `park {id,
  reason}` already exists in `__scrupuli__`; requiring every open scrupulus to be followed or
  parked-with-reason before `wave seal` is a *mechanical* invariant on bookkeeping, not a
  decision rule, and the design's own principle allows it. It is not in v5.
- **Over-engineering.** The Rust justification (v5 §libripens, "Why Rust") does not survive the
  probes: the latency win comes from the *resident server* (3 ms `mcp_tool`), not the language;
  any `command` hook floors at about 140 ms regardless (probes v1 §Observations), and the Rust
  "1 ms" is "still a claim". A resident Python server gives the same 3 ms. Cross-platform CI, a
  SQLite index with byte watermarks, `map`, `rebuild`, Wh estimates, bits per message,
  PreModelSwitch, WorktreeCreate, InstructionsLoaded hashing, MessageDisplay: none of these
  touches the hypothesis. The validation code that already exists is Python and works.
- **Measurement theatre, partly admitted.** Of 11 instruments, 1 reached the brief, on 3 data
  points with about 2× sensitivity to the term list (validation §Instrument decisions). The
  energy ledger is tokens × a coefficient, labelled ESTIMATE: decoration. The sustainability
  section (v5) is longer than the section on how the PI decides.
- **Platform dependence.** Everything verified on Claude Code 2.1.296 only; the key mechanisms
  (`mcp_tool`, `asyncRewake`, `agent` prompt replacement, Pre/PostCompact) have "none stated" as
  documented floor (probes v1 §Minimum version). The `agent` setting drops nine default prompt
  blocks and cold-starts the cache (2.6× cost in probe 13). A point release can break the hook
  set; the design acknowledges this with a "degrade to v2" fallback that does not exist yet.
- **Cost.** A two-message pair ping-pong cost 0.42 USD (probes §Observations); SubagentStart
  context is paid per resume; Anthropic's own multi-agent research write-up [memory] reported
  roughly 15× the tokens of a single chat and gains only on parallelisable work; the scaling
  study the benchmark report cites gives −70 % to +81 % versus a single agent (2512.08296). No
  single-agent control is planned before `build/pilot/baseline`. It should come first.

**Where it is most likely fooling itself:** in believing that v5 "integrates wave 1". It
integrated wave 1's platform findings thoroughly and its central research finding nominally.

## 4. The decisive test

Replay the genesis PI's decision point with the material the PI actually had, and score uptake of
the five known missed signals. No `libripens`, no hooks, no stores: a hand-built brief in
Markdown and `claude -p`.

- **Material:** the genesis repo pinned at `17e97ae`; the user's original message; the 35 C&S
  bullets as "scrupuli" (`validation/labels/surprises.csv`); the open claims with labels; the
  wave-2 PI note. Ask for the next wave note and worker briefs.
- **Arms** (5 runs each, Opus, same material):
  A. default Claude Code prompt;
  B. `--agent research-pi` with the v5 prose identity;
  C. B plus one bookkeeping invariant: "each listed scrupulus ends this note as FOLLOW (named
  in a brief) or PARK (one reason)".
- **Score:** for each of the five signals (Bernoulli h = 1; trained ≈ random; Champernowne;
  m-sequence ≡ de Bruijn; the user's object-first wording), hand-label FOLLOW / MENTION / NONE,
  using the validation report's definitions. Also count fabricated citations. Genesis baseline:
  1 of 6 signals followed (the 2, 6, 20 count), one fabricated result.
- **Cost:** about 15 runs at 1–3 USD, under 50 USD, one day.

**Stop** if B does not beat A (median FOLLOW ≤ 1 of 5 in both) and C does not beat B. Then
prose identity does not move Opus's judgement, a mechanical invariant does not either, and the
lab's thesis fails at its root; build nothing, keep the hardening skill.

**Go** if B or C reaches FOLLOW ≥ 3 of 5 in at least 3 of 5 runs, with briefs that change (not
notes that mention), and A does not. If C beats B, the design's principle is wrong in a useful
way: bookkeeping invariants on the PI belong in the build. Replicate the planted-cascade
experiment B (3–5 runs per arm, already planned) in the same day: it is the only evidence on the
pair protocol and it is a CONJECTURE.

## 5. What to cut to reach the test fastest

Cut, for now: `libripens` as a Rust crate and everything downstream of it (MCP server, SQLite
index, `map`, `rebuild`, cross-platform CI, Nest distribution); the hook set beyond four
(SessionStart brief as `command`, UserPromptSubmit capture, PreToolUse guard, SubagentStop
ledger); bits, Wh, read ratio, PostToolBatch, model-switch, worktree, InstructionsLoaded,
MessageDisplay, Notification, Pre/PostCompact, FileChanged rewake, Agent Teams fallback. Keep the
Latin names; they cost nothing more.

Keep and ship as a skill plus agent files: the label ladder and weakest-open-verdict rule;
independence first and `changed_by`; PI claims as `pondus` claims; `framing.md §0`;
`__scrupuli__` with `raise`/`mention`/`follow`/`park`; the exploration reserve and the probe
portfolio. Stores as per-writer JSONL appended by a 50-line Python script. If the pilot later
shows hook latency or store contention as a measured problem, the Rust port has a reason; today
it has none.
