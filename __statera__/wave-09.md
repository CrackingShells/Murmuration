# Wave 09

opened: 2026-10-24

## The user's sentence this wave serves

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

Budget: not yet set by the user for this wave. Spend baseline at opening: TOTAL USD 482.47 at
least; this checkout 110.37 at least, of which 27.44 is this resumed session [source:
`scripts/lab_status.py --spend`, 14:21]. Round 1 is kept to about USD 10 until the user sets one.

## What does not add up

- **Auto mode's classifier is the largest per-call cost the lab cannot touch** (628 ms median on a
  trivial Bash call, wave 7), and its decisions are recorded nowhere the lab reads. Whether a local
  model agrees with it is unknown, and so is how many of its decisions the transcripts even hold.
- **The labels are skewed.** Almost every recorded call was allowed; a refusal is rare. Agreement
  on allowed calls says little about the case that matters, a false allow.
- **Replacing the classifier is the permission layer, and stays the user's.** This wave measures
  agreement only; a dev hook that asks a local model records its answer and decides nothing.

## Reassessments

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w09-a | explorer | the labelled set: auto-mode classifier refusals and a stratified sample of allowed calls across all sessions; synthetic adversarial cases; sample sizes | |
| explorer-w09-b | explorer | candidate local classifiers (Jev, Laya, guard models, prompted baselines) via LM Studio: download, smoke set, latency, memory; same weights outside LM Studio if a runtime exists | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- 2026-10-24 afternoon, before opening: the colgrep report is at
  `/Users/hacker/Documents/src/CrackingShells/colgrep-mcp/__reports__/match_lines/00-observation_markdown_match_lines_v0.md`
  (not committed there); the reminder `colgrep-mcp match lines — show where a markdown hit
  matched` (`id: sj-colgrep-match-lines`, mission, est30m, priority 5, no due date) is in list
  Side Jobs.
- LM Studio at 14:21: server up at 127.0.0.1:1234; downloaded, none loaded: three embedding
  models, `qwen3.6-35b-a3b`, `google/gemma-4-26b-a4b` and others [source: `/api/v0/models`]. The
  machine has 36 GB of memory.

closed: YYYY-MM-DD
