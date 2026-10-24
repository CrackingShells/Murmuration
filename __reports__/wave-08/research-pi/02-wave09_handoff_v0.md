# Hand-off to the PI of wave 9 (v0)

written 2026-10-24 afternoon, by the PI of wave 8, from a brainstorm with the user after the close.
Open wave 9 in a **fresh session**: this one carried about 400k tokens and paid USD 27 to resume
[source: `scripts/lab_status.py --spend`, 14:21]. A fresh PI starts near 50k.

## Before the first dispatch

- **The user's setting.** The user said they will add the compaction window ("I still need to add
  the parameter to limit context window size"): `"autoCompactWindow": 250000` in the main
  checkout's `.claude/settings.local.json` (w08-c3; synthesis item 42). Check it is there before
  relying on it; the guard keeps agents from writing that file.
- **The budget.** Not set yet for wave 9. Ask.
- **Read:** `__statera__/synthesis.md` "Wave 8" and open items 42–48; this file; the addendum
  `01-addendum_classifier_probes_v0.md` beside it; the 10 open puzzles
  `__scrupuli__/wave-09-explorer-w09-*.md` (they are yours to dispose of at your close).
- The user's message of 2026-10-24 ends mid-sentence ("Additionally, I am curious,"): ask what
  they meant.

## The user's words for wave 9 (2026-10-24, after the close)

> I think we would probably need to study qualitatively whether the PI context acquisition
> patterns and its way to react to what's coming from its team.

> many were labelled ESTIMATED. If that's the case, there aren't a single thing that landed on
> `main` that has been properly measured? [...] probably a whole section of the next few waves
> will be dedicated to reporting the PI's cost and behavior given the context window decrease.

> the PreCompact hook did not land. But it seems like an interesting location to be creative and
> automate the information we can pass to the PI after compaction so that it doesn't need to
> re-read anything and only trust the output of a semantic search, for example.

> Before we care about time, however, we must check accuracy: can we find a classifier we can run
> locally that is aligned with the decisions Anthropic's classifier took? [...] You can also add a
> Pre-tool call and Post tool call dev hooks that dispatches the classification to the
> self-hosted models and then record agreement/disagreement. But you are correct that
> statistical treatment of the results will need to be serious because samples will be skewed
> toward comparing allowed tool calls

## Five directions, with what is already known

| # | Direction | Known | First step | Rough cost |
|:--|:--|:--|:--|:--|
| 1 | **The PI under a compaction window: cost and behaviour.** A standing per-wave report (spend split read / write / output, what entered the context and why, wakes, re-reads after each compaction), plus a qualitative coding of a sample of PI turns: what it reads and why, how it reacts to each hand-back, which wakes end with no action | `__instrumenta__/w08d_pi_context.py` splits a PI session by source; wave 8's own PI: USD 15.18 over 167 requests at 03:30, context 406k, no compaction; worker hand-backs 7.1% of what it re-read | Run the script on waves 5–8 and on wave 9 as it runs; an explorer codes 100 PI turns by hand against a scheme it writes first | USD 5 |
| 2 | **Measured, not estimated, savings.** Every landed change has its mechanism MEASURED; none has its money measured in a real wave (the ladder's USD figures are counterfactual ESTIMATEs by definition) | The live harness log holds `budget` hook times since w08-c4; PI sessions of waves 5–8 are a baseline for direction 1 | Before/after per landed change, on the same kind of work: the PI's USD per request and per wave with the window against waves 5–8; the hook's live ms from the harness log against wave 7 | USD 3 |
| 3 | **PreCompact, second version.** The hook writes the lab's state into the summary so the PI need not re-read: a compact digest, plus pointers it can trust (exact line ranges; semantic hits once colgrep shows where a markdown hit matched) | w08-c3: in a small lab the hook added nothing, but the test could not see it: re-reads were 1.6–14k tokens and the questions were answerable from 300–700-character files (S-w08-reproducer-w08-3-4); a real PI's floor is about 91k | A replay at real size (the real wave notes, a 91k floor, a harness log with workers in flight), measuring re-read tokens after compaction and answer accuracy, hook against no hook, on Opus | USD 10 |
| 4 | **A local classifier's agreement with auto mode.** Shadow-mode dev hooks: PreToolUse asks a local model (async, never deciding) and records its verdict by `tool_use_id`; the platform's own verdict is joined from the transcript record (`permissionDecision.reasonType: "classifier"`) after the fact | 30,525 recorded allows, 67 refusals (0.075%), allows recorded only since 2.1.293; the classifier's input is not in transcripts (agreement is a lower bound); refusals are mostly agents working around a hook; 15 refusal-then-rewrite pairs; 65 synthetic cases drafted; Granite Guardian 8B and gpt-oss-safeguard-20b judged a small easy set well at 1.2 s and 2.3 s, slower than auto mode's 450–628 ms; Laya fast and weak; Jev has no weights | The offline agreement run first (the redacted set in `/private/tmp/murmuration-w09/explorer-w09-a/`, stratified weights, refusals and synthetic reported apart, the 15 pairs as the hardest test), then the shadow hook. Replacing or bypassing auto mode's classifier stays the user's decision | USD 8 |
| 5 | **colgrep shows where a markdown hit matched.** Upstream, in the user's colgrep-mcp repository | Report written there (`__reports__/match_lines/00-observation_markdown_match_lines_v0.md`, not committed); a mission reminder in Side Jobs (`sj-colgrep-match-lines`) | The user's side job; direction 3 benefits when it lands | — |

## Statistics for direction 4 (to settle before the run)

- Report agreement on allowed calls and on refusals separately, never one pooled rate: the pooled
  rate is about the allow rate.
- Allowed calls: the stratified sample (1,608 of 30,525, weights N_h/n_h by tool, project and
  command family) gives a reweighted false-refusal rate with an interval.
- Refusals: all 67 observed, plus the live shadow hook's new ones as they come, plus the
  synthetic set, each reported apart. Zero misses in 67 bounds the miss rate at 4.4% (95%
  one-sided); a ±0.05 interval at a 20% miss rate needs about 246 refusals, about 117 days at the
  observed rate (ESTIMATE, explorer-w09-a). So the refusal side will stay thin for months; the
  synthetic set and the 15 rewrite pairs carry it meanwhile.
- The classifier judges intent with context the transcripts do not keep: give the local model the
  visible context (the preceding user prompt or task) and say that its agreement is a lower bound.
- A false allow is the metric that matters; a false refusal costs a detour.

## Not to forget

- The guard's leftovers (synthesis item 26): `+c` clusters, zsh `-O` and ksh `-o` misread, a
  variable as the program, unlisted wrappers; the Python fall-back's slow case on very long words.
- 17.4 GB of model weights now sit in LM Studio's folder (Laya, Granite Guardian 4.1 8B,
  gpt-oss-safeguard-20b); nothing is loaded.
- Branches of wave 8 not merged: `w08-c2-shorthandback`, `w08-c3-compaction` (the hook);
  worktrees under `/private/tmp/murmuration-w08/*/wt` can be removed.
