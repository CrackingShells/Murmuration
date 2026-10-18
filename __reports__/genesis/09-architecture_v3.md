# Research-lab package — Architecture Analysis (v3, consolidated)

Date: 2026-10-18 · Supersedes [07-architecture_v2.md](07-architecture_v2.md). It adds the full hook
surface ([08-hooks_leverage_v0.md](08-hooks_leverage_v0.md)) and information instruments, as
advised by the outside counsel ([08-information_counsel_v0.md](08-information_counsel_v0.md)) on
the draft ([08-information_measures_draft_v0.md](08-information_measures_draft_v0.md)). Unchanged
from v2: names, stores, agents, the umbod composition. This is the build reference.

## Executive Summary

- **Goal:** a multi-agent research team that reliably shows judgement-led exploration within a
  budget and mechanical hardening, with anomalies flowing back from hardening to exploration.
- **Principle:** procedure where the work is mechanical (stores, hooks, verifiers); identity where
  it is judgement (the PI). **Measurements are instruments for attention, never targets or
  gates.**
- **Package:**
  - `AGENTS.md`;
  - five agents (research-pi, explorer, author, reproducer, proof-adversary), plus an optional
    depth reviewer;
  - one skill (`research-loop`) and user commands `/lab` and `/lab-status`;
  - the Rust binary **`libripens`** (CLI, hook entry point, resident MCP server);
  - five append-only stores named after the Roman balance.
- **New in v3:**
  - **Hooks across 20+ of the 33 events.** Your words are captured automatically
    (`UserPromptSubmit`). The per-run contract is injected at `SubagentStart`. Pair messages are
    mirrored by `PostToolUse(SendMessage)`. `FileChanged` gives live notice of puzzles.
    `PreCompact`/`PostCompact` show what the PI's context dropped. Most hooks go through
    `mcp_tool` handlers, so no process starts per event.
  - **Information instruments,** kept or changed per the counsel and validated on this
    repository:
    - bits and conditional bits per message;
    - coverage of the user's own terms;
    - anomaly retention;
    - PI read ratio;
    - label reliability.
    The measures that failed the pilot (JSD maps, MI as a number) are dropped.
- **Composition:** umbod's contracts are reused, not its CLI; umbod stays the outer loop for
  multi-session campaigns.
- **Sustainability:** tokens, bits, cache reads, CPU seconds and estimated Wh in the ledger, per
  accepted claim and per mode.

## The balance: names

One Latin root system: weighing (*pendere*, *libra*). Paying and judging are the same act, so
every store is a role in one balance.

| Store / tool | Name | Gloss | Holds |
|:--|:--|:--|:--|
| ledger | **`__expensa__/`** | "things weighed out", the Roman payment entry | one event per agent run: what it spent |
| lab state | **`__statera__/`** | the balance in its current state | wave notes (open, then sealed), budget, inbox acknowledgements, questions to the human |
| claims | **`__pondus__/`** | the weight a claim can bear | claim and verdict events; the current label is derived |
| peer threads | **`__examen__/`** | the tongue of the balance; the verifier's independent weighing | per-claim conversation between author and verifier |
| puzzles | **`__scrupuli__/`** (sing. *scrupulus*) | the sharp pebble, and the smallest weight: a residue not rounded away | what did not add up, and whether anything followed it |
| tool | **`libripens`** | the neutral scale-holder in a Roman sale | the only writer path to the stores; hooks; queries |

Notes:
- `pondus` names a directory only, because a `pondus` package exists on several registries.
- `examen` reading as "exam" in Spanish and French is close enough to its sense to keep.
- The Latin forms have not been checked against a lexicon (flag carried from the naming report).

## Proposed State

```mermaid
graph TD
  U([User]) -- "/lab · prompts · answers" --> PI
  subgraph agents
    PI[research-pi<br/>main thread · Opus · identity in prose]
    EX[explorer<br/>probes, literature]
    subgraph pair["pair (one per claim)"]
      AU[author<br/>proof or experiment]
      VR[verifier<br/>reproducer · proof-adversary]
    end
    DR[depth reviewer<br/>optional, before synthesis]
  end
  L{{libripens<br/>CLI · hooks · MCP}}
  subgraph stores["stores (append-only, per-writer segments)"]
    FR[(framing.md §0<br/>user's words, human-only)]
    ST[(__statera__)]
    PO[(__pondus__)]
    EXM[(__examen__)]
    SC[(__scrupuli__)]
    XP[(__expensa__)]
  end
  IDX[(derived index<br/>SQLite, gitignored)]
  INS[[instruments<br/>bits · coverage · retention · read ratio · reliability]]
  PI & EX & AU & VR & DR --> L
  AU <-- "direct SendMessage, mirrored" --> VR
  L --> ST & PO & EXM & SC & XP
  ST & PO & EXM & SC & XP --> IDX
  IDX --> INS
  INS -- "counts in words, in the brief" --> PI
  INS -- "full tables (/lab-status --measures)" --> U
  U -. "every genuine prompt, captured by UserPromptSubmit" .-> FR
```

## Key Flows

```mermaid
sequenceDiagram
  participant U as User
  participant PI as research-pi
  participant X as explorer(s)
  participant A as author
  participant V as verifier
  participant L as libripens + stores
  U->>L: /lab "question" → framing.md §0
  PI->>L: ask --soft "is this your question?" (framing read-back)
  loop each wave, while budget remains and the question is open
    PI->>L: wave open: user's sentence + "this doesn't add up because…"
    par portfolio of cheap probes
      PI->>X: loose brief A (maxTurns)
    and
      PI->>X: loose brief B (maxTurns)
    end
    X->>L: scrupuli raised + raw artifact refs
    PI->>PI: opens raw artifacts itself
    opt a hunch is worth a claim
      PI->>A: claim brief · names V · claim id
      PI->>V: brief: independent result first
      A->>L: pondus claim event (label by what was run)
      V->>L: examen: independent result (seq 1)
      loop pair conversation, until verdict or ESCALATE
        V->>A: question (mirrored to examen)
        A->>V: answer or new artifact (mirrored)
      end
      V->>L: pondus verdict (changed_by if revised) + scrupuli
      alt ESCALATE or disputed
        L-->>PI: brief lists it; PI reads the examen thread itself
      end
    end
    L-->>PI: open scrupuli from every role reopen exploration
    PI->>L: wave seal (statera, immutable)
  end
  PI->>L: ask --soft "open scrupuli + reserve: spend on which?"
  opt budget exhausted
    L-->>U: ask --hard "budget gone; this is what I would still probe"
  end
  PI->>U: findings by label, with what still doesn't add up
```

## Package layout

```
research-lab/
├── .claude-plugin/plugin.json     min versions: managing-roadmaps ≥1.2.0, writing-reports, colgrep-mcp
├── AGENTS.md                      shared invariants (one screen); copied by lab-init; CLAUDE.md = "@AGENTS.md"
├── agents/
│   ├── research-pi.md   explorer.md   author.md   reproducer.md   proof-adversary.md
│   └── depth-reviewer.md          optional; umbod-style senior reviewer
├── skills/
│   ├── research-loop/SKILL.md     modes, briefs (worker mandate), labels, honesty tags, lab-init section
│   ├── lab/SKILL.md               user-invocable, model invocation off
│   └── lab-status/SKILL.md        user-invocable (`--measures` for full instrument tables)
├── hooks/hooks.json               every hook calls `libripens hook …`, with agent_type matchers
├── .mcp.json                      libripens (mcp), WolframToolkit, colgrep, arxiv, one web search
└── libripens/                     Rust crate; CI builds darwin and linux, arm64 and x64
```

## Contracts & Invariants

### Stores

Layout: `__<store>__/<wave>/<agent_id>.jsonl`, one segment per writer. No two writers share a file,
so parallel appends need no locks and git never conflicts. `framing.md §0` is the single human-only
file.

| Store | Events (one JSON line each) | Derived at read time |
|:--|:--|:--|
| `__expensa__` | `run {ts, run_id, wave, agent_id, agent_type, model, mode, claim_id?, tokens{in,out,cache_read,cache_write}, wall_s, cpu_s, energy_wh_est, tool_calls, deliverable, exit}` | spend by mode, wave, agent and claim; budget left; Wh per accepted claim |
| `__statera__` | `wave_open {wave, user_sentence, note, budget, exploration_share}` · `wave_append {note}` · `wave_seal {wave}` · `ack {inbox_ref}` · `ask {id, soft\|hard, text}` · `answer {id, text, by: human}` | the current wave; sealed history; unacknowledged steer notes; open questions |
| `__pondus__` | `claim {id, statement, label, scope, evidence[{path, commit}], author}` · `verdict {claim_id, by, vocab, verdict, examen_ref, changed_by?}` · `supersede {old, new}` | **current label = weakest open verdict from distinct verifiers; disputed if open verdicts disagree** |
| `__examen__` | `msg {claim_id, seq, from, to, kind: independent_result\|question\|answer\|artifact\|verdict\|escalate, body, refs[]}` | open threads; ESCALATE list |
| `__scrupuli__` | `raise {id, wave, agent, text, refs[]}` · `follow {id, by_brief\|by_claim}` · `park {id, reason}` | open / followed / parked; follow rate; latency in waves |

Invariants (each enforced by `libripens`):
- **Single writer path:** agents append only through `libripens append` or its MCP tools, which
  validate the schema. The guard denies direct edits to the stores and to `framing.md §0`.
- **Append-only:** nothing is updated in place; sealed waves are immutable.
- **Independence first:** the first `__examen__` message on a claim is the verifier's
  `independent_result`.
- **A verdict changes only with evidence:** a later verdict by the same verifier needs a
  `changed_by` path that exists.
- **Nothing reaches a deliverable above its current label.**
- **Honesty tags (from umbod):** every claim's evidence is a `[source: path@commit]`; ESTIMATE and
  CONJECTURE carry an `[assumption: …]`.

Index: a gitignored SQLite file holding per-segment byte watermarks. Queries ingest new bytes
only; `libripens rebuild` replays every segment. Gates that need strict freshness scan the segments
directly.

### libripens (one Rust binary, three front ends)

```
libripens append <store> --json '…'          # agents; validates, appends to own segment, fsync
libripens query  scrupuli --open | pondus --disputed | expensa --by mode | examen <claim>
libripens wave   open|append|seal  ·  ask --soft|--hard  ·  answer
libripens measure <text> --ctx <path>         # bits, new bits, coverage (also used by hooks)
libripens map --wave <n>                      # offline: retention, read ratio, anchors, novelty
libripens brief                               # SessionStart: startup / resume / compact / fork
libripens hook   subagent-stop | pre-tool-use # hook JSON on stdin; decision JSON on stdout
libripens rebuild                             # replay segments into the index
libripens mcp                                 # the same operations as typed MCP tools
```

- **Why Rust:** hooks fire on every tool call of every agent, more than 1,000 in the imbrication
  study.
  - A static binary starts in about 1 ms with about 2–4 MB of memory; Python takes about 30–60 ms
    and 15–25 MB, and depends on an interpreter and packages.
  - It matches `dirtree-rdm` and `umbod`.
  - Cross-platform CI builds from day one (`dirtree-rdm` still ships darwin-only).
- **Pilot scope:**
  - `append`, `query`, `wave`, `ask`, `brief`, `measure`;
  - the hook subcommands;
  - the MCP front end, which v3 needs from the start for the `mcp_tool` handlers.
  `map` and `rebuild` come second.

### Hooks (`hooks/hooks.json`, `agent_type` matchers; frontmatter hooks are ignored for plugin subagents)

The full map and its rationale are in [08-hooks_leverage_v0.md](08-hooks_leverage_v0.md). The
contract:

| Event (matcher) | Handler | Effect |
|:--|:--|:--|
| SessionStart (startup/resume/compact/fork/clear) | command `libripens brief` | Brief in this order: user words and unacknowledged steer notes · open scrupuli · disputed claims and ESCALATEs · open questions · instruments (words, with denominators) · spend and reserve · in-flight runs · roadmap frontier. `watchPaths` on stores; `sessionTitle` = wave; cache-cold notice on resume |
| UserPromptSubmit | mcp_tool | Append genuine user prompts verbatim to `framing.md §0` (hand-backs and cross-session messages become `comm` events instead) |
| UserPromptExpansion (`lab`, `lab-status`) | mcp_tool | lab-init when channels are missing |
| SubagentStart (workers) | mcp_tool | Open an `expensa` run; inject wave, claim id, partner, framing pointer and the honesty contract (`additionalContext`) |
| PreToolUse (`Agent`) | mcp_tool | Measure the brief (bits, redundancy against the injected context); record it; tell the PI in words only if the brief repeats injected material |
| PreToolUse (`Bash`, `Edit\|Write`) | command | Guard: deny kills by pattern; stores and `framing.md §0` are append-only through `libripens` (exit 2) |
| PostToolUse (`SendMessage`) | mcp_tool, async | Mirror pair messages into `__examen__`; `comm` event |
| PostToolUse (`Agent`) | mcp_tool, async | Ledger from run telemetry (foreground runs) |
| PostToolUse (`Write\|Edit` under `data/`, figures) | mcp_tool, async | Register raw artifacts for the brief |
| PostToolUse (`Read`, main thread) | mcp_tool, async | PI read events (for the read ratio) |
| PostToolBatch | mcp_tool | Record a parallel dispatch as one probe set |
| PostToolUseFailure · PermissionDenied · StopFailure | mcp_tool / command, async | Waste and friction events |
| SubagentStop (workers) | command | Close the run (tokens from `agent_transcript_path`); presence gate (`decision: block` once, `stop_hook_active`) |
| Stop (main) | command, async | Turn snapshot (comm totals, spend by mode) |
| PreCompact / PostCompact | mcp_tool | Record PI context size and `compact_summary`; derive which open scrupuli the summary dropped |
| FileChanged (store segments) | command | Live `systemMessage` for new scrupuli, disputes and ESCALATEs only |
| InstructionsLoaded | command, async | Hash instruction files (prompt-cache stability) |
| PreModelSwitch / PostModelSwitch | command | Log the switch with its cache-rewrite cost; energy coefficient follows the model |
| WorktreeCreate / WorktreeRemove | command | Register worktrees; list the ones to prune at wave seal |
| Notification (`agent_needs_input`) | command | Desktop notice for hard questions |
| MessageDisplay | command | Display-only: claim ids shown with their current label |
| SessionEnd | command | Flush the index; closing ledger summary (fits the 1.5 s budget) |
| TaskCreated / TaskCompleted / TeammateIdle | command | Agent Teams fallback only |

Invariants:
- `deny` and `block` are used only by the guard and the presence gate. Everything else informs.
- LLM-evaluated hook types (`prompt`, `agent`) are off by default.

### Agents

**research-pi**, the identity in prose. It is the whole system prompt in the main thread, so it
stays this short:

> You lead a small research team on a question someone cares about. Your job is to notice. You
> read the raw things your team produces (figures, odd rows, the examen threads where colleagues
> argued, the scrupuli they could not let go of), and you follow what does not add up, even when
> it is not on the roadmap. You keep the person's own words close; they are the question, and
> everything else is a reading of it. Exploration is yours: you decide which hunches deserve a
> claim, and you spread cheap probes when you cannot tell which is promising. Hardening is your
> team's: you trust their checks and spend your attention where judgement is needed. Framing,
> naming and the final synthesis you do yourself. When the budget runs out or you are about to
> close the story, you show the person what is still open. The procedures you and your team use
> are in the `research-loop` skill.

Workers (frontmatter fields `model`, `effort`, `maxTurns`, `tools` and `skills` are honoured for
plugin subagents):

| Agent | Model | Carries, in its own voice |
|:--|:--|:--|
| explorer | Sonnet | Return raw material and the worst-fitting case next to the best one. Give the id you fetched, or write UNVERIFIED. End with the three things you would look at next and why they bother you |
| author | Sonnet (Opus by brief for hard proofs) | Say what would differ if the claim were false, and show that case. Label by what you ran. When a result closes a direction, write the scope it closes and name one thing outside it. Wolfram first for exact work; state in one line why the tool fits |
| reproducer | Sonnet | Record your own result before reading the author: rerun at **sampled** scale (quick mode plus random cells, with a full rerun only on a mismatch), claim → row, re-derive without author code. You own termination: SUPPORTED / OVERSTATED / UNSUPPORTED / ESCALATE |
| proof-adversary | Sonnet or Opus | Record your own result first: per-step re-derivation, independent checks at larger and boundary cases. You own termination: SOUND / GAP / WRONG / LABEL TOO STRONG / LABEL TOO WEAK / ESCALATE |
| depth-reviewer (optional) | Opus | umbod's senior reviewer: judge by feel whether the work answers the person's words and goes as deep as it promised; one verdict paragraph before synthesis |

All workers use the framing doc's symbols and close with `[source:]`/`[assumption:]` tags and a
scrupuli entry. That is umbod's "what I am uncertain about", uncapped.

### Information instruments

Counsel verdicts are in [08-information_counsel_v0.md](08-information_counsel_v0.md). The pilot was
run on this repository's own reports (MEASURED), and only what carried signal is kept.

| Instrument | Definition | Where computed | Shown |
|:--|:--|:--|:--|
| Message bits | zstd size with a dictionary trained per study on framing, AGENTS.md, skills and sealed reports | hook (ms) | ledger; `/lab-status --measures` |
| New bits and redundancy | C(msg \| receiver's real context) = C(ctx+msg) − C(ctx); redundancy = 1 − new/total. **Within a thread or brief only**, where the receiver's context is on disk | hook | the brief, in words ("the brief repeats 70% of what the author already receives") |
| User-term coverage | share of the content terms of `framing.md §0` (and of the framing symbol table) used by a text | hook (µs) | the brief, in words with denominators. *Pilot: atlas 0.52, experiments 0.27–0.41, PI notes 0.23 → 0.09 → 0.12; "combinatorics", the user's first noun, appears nowhere* |
| Anomaly retention | share of the surprises raised in a wave (scrupuli) whose key terms reach the next wave note, brief or claim | at wave seal | the brief and the KT report |
| PI read ratio | bytes of raw artifacts and threads the PI opened ÷ bytes workers produced | at wave seal | the brief; the KT report (the empirical "starved vs drowning" rate) |
| Label reliability | label × final verdict table from `__pondus__` | offline | KT report only |
| Scrupulus novelty, distinct meanings | cosine to named anchors (`fastembed`, all-MiniLM, CPU); the count of distinct meanings across independent statements of one result | offline, on demand | on request |
| Sampled semantic entropy | 5–10 samples, clustered by entailment | on demand: disputed or synthesis-bound claims | the cluster list, not a number |

Dropped after the pilot:
- JSD vocabulary maps: they order nothing at these sample sizes.
- MI as a number: biased upward.
- Text-distance pair convergence: no separation. It is replaced by *whose words the verdict
  reuses* and *first use of framing terms in `__examen__`*, pending validation experiment B.
- Transfer entropy and topic models.

Rules that keep instruments from becoming targets:
- Agents never receive a measure.
- The brief states counts in words with their denominators: no scores, thresholds, colours or
  arrows.
- No measure enters any gate.
- Nothing is ranked.
- The closing KT report states which measures were looked at and whether any changed what the PI
  did, so the instruments themselves get reviewed each study.

### Human-side UX

| Element | What it does |
|:--|:--|
| `.claude/settings.json` written by lab-init | `agent: research-pi`, so a plain `claude` in the project *is* the PI |
| `/lab <question>` | Runs lab-init if needed; appends the words to `framing.md §0`; the PI opens with a soft read-back question |
| `/lab-status` | `libripens brief` on demand |
| Your prompts | Captured verbatim by `UserPromptSubmit` (umbod-style inbox): the PI acknowledges them in the next wave note, and unacknowledged ones head the brief. `/lab-steer` is no longer needed |
| Questions | Soft (read-back, "reserve: spend on which?") are recorded and non-blocking; hard (budget gone) waits for an answer. Shown by `/lab-status` |

### Composition with umbod

For single-session studies the lab stands alone. For multi-session campaigns:
- an umbod topic is the research question, and its INTENT.md mirrors `framing.md §0`;
- one umbod cycle holds one or more lab waves;
- sealed `statera` waves feed the cycle's HANDOFF;
- umbod's verifier runs before `finish-cycle` as usual.

Reused contracts are listed in [06-stores…](06-stores_umbod_sustainability_v0.md) §1. The CLI and
FSM are not imported. The former name collision (`__threads__/`) is gone (`__examen__/`).

### Sustainability (measured in `__expensa__`)

| Resource | Levers |
|:--|:--|
| Agent communication | measured in **bits** and **new bits** per message; context injected once by `SubagentStart` instead of pasted into briefs; briefs reference paths; colgrep retrieval; pairs talk directly; warm reuse; `query` returns pointers |
| Prompt cache | AGENTS.md, agent bodies and skills stay byte-stable within a study; variable content goes at the end of briefs; `cache_read` is tracked |
| Compute | model tiering; smallest instance first; Wolfram for exact work; sampled reproduction; content-addressed result cache |
| Electricity | `energy_wh_est` = tokens × per-model coefficient + `cpu_s` × machine coefficient (labelled ESTIMATE, sourced); budgets can be stated in Wh; hooks run as `mcp_tool` calls to a resident server, with no process start per event |
| Materials and storage | no re-downloads; derived data gitignored; vector or referenced figures, not embedded rasters; prune indexes and worktrees at close |
| Human attention | soft questions batched; hard ones only for budget-gone; scrupuli first in the brief |

The closing knowledge-transfer report of every study states tokens, CPU seconds and Wh per
accepted claim and per mode.

## Behavioral baseline

- **External** (survey ranking): ResearchGym (budgeted exploration), CORE-Bench v1.1 (the
  reproducer: cost and variance), Formal Conjectures with CombiBench (prove or disprove), MAST /
  TRAIL / ARFT (failure tags on our transcripts), TruthInsightBench (claim honesty). Inspect AI
  holds the logs; HAL logs give reference points.
- **Own metrics from the stores:**
  - spend share by mode;
  - exploration reserve;
  - delegation profile;
  - **scrupuli raised and followed**;
  - label calibration;
  - independent-verification coverage;
  - evidence traceability;
  - re-planning events by trigger;
  - hook interventions;
  - Wh per accepted claim;
  - redirects the PI did not anticipate.
- **Puzzle-following replay** (the gap no benchmark covers):
  - Replay the imbrication question. Score whether later waves pick up what the original run missed
    (Bernoulli h = 1, a trained map ≈ a random map, Champernowne completion, m-sequence ≡ de Bruijn,
    the user's object-first wording).
  - Then plant one synthetic anomaly per run and score detection latency.
- **Instrument validation** (counsel §4), before any instrument reaches the brief:
  - *A, retention replay:* 35 surprise bullets from this study's worker reports against the three
    PI notes. The instruments pass if the five known missed signals sit in the zero-retention,
    low-similarity cells and the one followed signal (2, 6, 20, 58, …) does not.
  - *B, planted cascade:* two verifier runs on one known claim, one independence-first and one
    shown the author's report first. Do "whose words the verdict reuses" and "term first use"
    separate them? If not, say so: independence-first is then the only guard.
- **Calibration:** hand-label about 20 transcripts before trusting an automatic MAST annotator.

## Alternatives Considered

| Option | Decision |
|:--|:--|
| Transmission-tradition names (pinkas, shilu, pratigya, sugya, kushya, sofer) | Not chosen. Three traditions mixed; the Latin set is one coherent balance and pairs with *imbrex* |
| SQLite or a server as source of truth | Rejected: binary, unmergeable in git, and out of proportion. Kept only as a derived index |
| One shared JSONL file per store | Rejected: relies on append atomicity that fails for large lines or on network filesystems |
| Python hooks | Rejected: per-call start-up and memory multiplied by agents × tool calls; dependency drift |
| umbod CLI as the backbone | Not for in-session studies; kept as the outer loop for multi-session campaigns |
| Four-agent minimal cut (one merged verifier) | Rejected for the verifier merge; both verification methods earned their cost |
| Agent Teams for pairs | Fallback only: teammates do not fire SubagentStop, so hooks would move to TaskCompleted |
| Command handlers for every hook | Rejected for hot events: one process start per event × thousands of events; `mcp_tool` to a resident server instead |
| JSD/MI maps of agent positions | Dropped after the pilot: no ordering at these sample sizes; coverage and retention carried the signal |
| LLM-evaluated hooks (`prompt`, `agent`) by default | Rejected: judgement and tokens on every event; on demand only |

## Risks & Mitigations

| Risk | Mitigation |
|:--|:--|
| Direct subagent-to-subagent messaging is only partly verified | Platform probe first; Agent Teams fallback |
| The PI file loses default-prompt behavior | Pilot check; fix by a skill pointer, never a longer PI file |
| PI prose decays into rules | The "when to decide what" test on every edit |
| A verifier is talked out of a finding | Independence first; `changed_by` enforced |
| Pair loops never converge | The verifier owns termination; `maxTurns`; ESCALATE |
| Energy coefficients are uncertain | Labelled ESTIMATE; used to compare runs, not as absolute figures |
| Index drift | The index is disposable; `rebuild` |
| Over-building `libripens` | Pilot scope as listed; `map` deferred |
| Instruments become targets | Agents never see them; no gates; counts in words; reviewed in each KT report |
| `UserPromptSubmit` captures non-user text | Filter on the hand-back and cross-session wrappers (platform probe 1) |
| Hook-set version drift | lab-init checks the Claude Code version and degrades to the v2 hook set |

## Roadmap Recommendation

To become `__roadmap__/research_lab/` on approval:
1. **Platform probes:**
   - direct subagent messaging;
   - SubagentStop fields for plugin agents;
   - `mcp_tool` handlers calling a plugin MCP server;
   - which `UserPromptSubmit` inputs mark hand-backs and cross-session messages;
   - what the main-thread `agent` setting drops from the default prompt;
   - the minimum Claude Code version for the v3 hook set.
2. **Instrument validation (offline, mostly no agent runs):** experiments A and B. Only the
   instruments that pass go into the brief.
3. **`libripens` core:**
   - stores, `append`, `query`, `wave`, `ask`, `brief`, `measure`, the hook subcommands, and the
     MCP server;
   - cross-platform CI;
   - replay on this repository's history.
4. **Agents and skills:** five agent files, `research-loop`, `/lab`, `/lab-status`; package with
   `spawning-agent-plugins`.
5. **Baseline:**
   - 20 hand-labelled transcripts;
   - the puzzle-following replay of the imbrication study;
   - one external benchmark for a reference point.

