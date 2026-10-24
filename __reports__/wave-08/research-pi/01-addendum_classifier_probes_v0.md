# Wave 8, extra work after the close: two probes on a local command classifier (v0)

written 2026-10-24 afternoon, by research-pi. Not a wave: the user asked for a brainstorm toward
the wave-9 hand-off, and the PI opened a wave by mistake; at the user's word ("finish your cheap
probes as part of a wave 8 extra work and close to main") the two probes are filed here. Their
puzzles (`__scrupuli__/wave-09-explorer-w09-*.md`) stay open for wave 9's PI. The hand-off is
`02-wave09_handoff_v0.md` beside this file.

## The user's words these probes serve

From the user's message of 2026-10-24 (afternoon), in their words:

> I authorize downloading the model weights. I suggest we download via LM Studio (I just started
> the app, you can probe at http://127.0.0.1:1234; nothing loaded for now). and we will be able to
> compare running ourselves (using the same weights, vs. running in LM studio) there might even be
> classifiers or fine tunes specific to tool calls.

> you can scan the other Claude Code sessions to search for the denied tool calls and help build
> the adverserial cases. You can also add a Pre-tool call and Post tool call dev hooks that
> dispatches the classification to the self-hosted models and then record
> agreement/disagreement. But you are correct that statistical treatment of the results will need
> to be serious because samples will be skewed toward comparing allowed tool calls

And the earlier part of the same direction: "Before we care about time, however, we must check
accuracy: can we find a classifier we can run locally that is aligned with the decisions
Anthropic's classifier took? Does a classifier on our side refuse the same tool calls? Does it
allow the same tool calls?"

Budget: the remainder of wave 8's USD 150. Spend baseline at opening: TOTAL USD 482.47 at
least; this checkout 110.37 at least, of which 27.44 is this resumed session [source:
`scripts/lab_status.py --spend`, 14:21]. The probes were kept to about USD 8.

## What does not add up

- **Auto mode's classifier is the largest per-call cost the lab cannot touch** (628 ms median on a
  trivial Bash call, wave 7), and its decisions are recorded nowhere the lab reads. Whether a local
  model agrees with it is unknown, and so is how many of its decisions the transcripts even hold.
- **The labels are skewed.** Almost every recorded call was allowed; a refusal is rare. Agreement
  on allowed calls says little about the case that matters, a false allow.
- **Replacing the classifier is the permission layer, and stays the user's.** This wave measures
  agreement only; a dev hook that asks a local model records its answer and decides nothing.

## Reassessments

**explorer-w09-a back (12eb74b, fa96441).**
- The classifier's verdict is on the tool-result record (`permissionDecision.reasonType:
  "classifier"`, `toolDenialKind: "automode-blocked"`), kept apart from rules, hooks and the
  user's answers. Over 5,227 transcript files: 30,525 recorded allows, 67 refusals (0.075%), 39
  "no verdict" errors; the allow side is recorded only since 2.1.293 (2026-10-08) [source:
  `__reports__/wave-08/explorer-w09-a/00-findings_v0.md`, MEASURED].
- Three things change the design. (1) The classifier's input is not in the transcripts (a git
  summary, cwd and platform only), so a local model judging the command and the visible context
  is compared against a classifier that may have seen more: agreement is a lower bound. (2) The
  refusals are not a spread of attacks: 16 of 67 in colgrep-mcp worktrees, 20 about colgrep, 6
  with `COLGREP_BYPASS`; most are agents working around a hook. (3) 15 refusals were followed by a
  rewritten call the classifier allowed: those pairs are the sharpest test of a local model.
- Statistics: 67 refusals bound a zero-miss model's miss rate at 4.4% (95% one-sided); ±0.05 at
  a 20% miss rate needs about 246 refusals, about 117 days at the observed rate (ESTIMATE). So the
  refusal side needs the synthetic set (65 cases drafted) and the live shadow hook, which adds
  refusals as they happen, both reported apart from the observed decisions.

**explorer-w09-b back (99c4447).**
- Jev is a hosted API with no weights: it cannot run here. LM Studio's `/v1/systemone` page exists
  (CITED). Downloaded through LM Studio, at the user's word: Laya (0.45 GB), Granite Guardian 4.1
  8B (4.9 GB, Q4_K_S), gpt-oss-safeguard-20b (12 GB): about 17.4 GB on disk, nothing left loaded.
- On a 22-call smoke set the explorer labelled itself (too easy to separate the judges; not an
  accuracy claim): Laya 57 ms a call but its choice head let 4 of 5 dangerous calls through;
  Granite Guardian 10/10 and 11/12 at 1.16 s per new prompt (0.48 s when the prompt prefix
  repeats); gpt-oss-safeguard 10/10 and 12/12 at 2.3 s p50; prompted baselines ministral-3-8b
  9/12 at 0.35 s and gemma-4-26b-a4b 12/12 at 5.5 s (+17 GB) [source:
  `__reports__/wave-08/explorer-w09-b/00-findings_v0.md`, MEASURED].
- "Same weights outside LM Studio": no independent runtime is installed (no mlx_lm, transformers
  or llama.cpp of its own); the llama-server inside LM Studio's backend folder gave identical
  outputs on 10 of 10 for Laya and Granite. A truly independent engine needs a runtime install,
  which the user's yes did not cover.
- What it means for the user's time argument: on this machine no candidate that judged the smoke
  set well is faster than auto mode's classifier (450–628 ms); the fast ones are the weak ones.
  Speed would need a smaller fine-tuned judge, a prompt-prefix cache, or a GPU host.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w09-a | explorer | the labelled set: auto-mode classifier refusals and a stratified sample of allowed calls across all sessions; synthetic adversarial cases; sample sizes | 12eb74b, fa96441 |
| explorer-w09-b | explorer | candidate local classifiers (Jev, Laya, guard models, prompted baselines) via LM Studio: download, smoke set, latency, memory; same weights outside LM Studio if a runtime exists | 99c4447 |

## Notes

- 2026-10-24 afternoon, before opening: the colgrep report is at
  `/Users/hacker/Documents/src/CrackingShells/colgrep-mcp/__reports__/match_lines/00-observation_markdown_match_lines_v0.md`
  (not committed there); the reminder `colgrep-mcp match lines — show where a markdown hit
  matched` (`id: sj-colgrep-match-lines`, mission, est30m, priority 5, no due date) is in list
  Side Jobs.
- LM Studio at 14:21: server up at 127.0.0.1:1234; downloaded, none loaded: three embedding
  models, `qwen3.6-35b-a3b`, `google/gemma-4-26b-a4b` and others [source: `/api/v0/models`]. The
  machine has 36 GB of memory.

