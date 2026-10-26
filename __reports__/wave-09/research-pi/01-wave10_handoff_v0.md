# Hand-off to the PI of wave 10 (v0)

written 2026-10-26 (11:01 by `date`), by the PI of wave 9, after the close and the two report
probes the user asked for. Open wave 10 in a **fresh session**: this one carried more than 330k
tokens with no compaction. The fresh PI is also the first live measurement of the compaction window
(item 42), if the setting is in the main checkout's `.claude/settings.local.json` before it starts.

## Before the first dispatch

- **The settings file.** Check `/Users/hacker/Documents/src/CrackingShells/Murmuration/.claude/settings.local.json`
  holds `"autoCompactWindow": 250000` and whether it is tracked on main (`git ls-tree HEAD .claude/`).
  The wave-9 merge wrote it into main by mistake and left it tracked (S-w09-research-pi-3, -4); the
  user chose how to leave it. Do not merge a branch that deletes or rewrites that file.
- **The window, live.** Read request 0's `usage` and, once the context passes about 217k, look for a
  `compact_boundary` record in your own transcript. If none comes, the setting did not reach the
  session (wave 9 saw neither "file read" nor "live reload" separated).
- **The budget.** Not set. Ask.
- **Read:** `__statera__/synthesis.md` "Wave 9" and open items 50–53; the two dedicated reports
  below; the open puzzles (`/lab-status`): S-w09-research-pi-3 and -4, and the puzzles of
  explorer-w09-j and -k, filed after the close.

## The user's words for wave 10 (2026-10-26)

> We also need to visualize, and then measure, the communication graph of the agent system. We need
> to know who dispatched who, and when. The purpose is to replay the evolution of the structure of
> the small lab during a wave. and to see if there is any correlation between the structure of the
> communication graph (and usual graph properties using in social network studies) and how the agent
> that delegate work tend to check or not the work of their subagents, and can we find why?

> This is the kind of metric we can measure and compare across agent systems using different
> language models.

On the classifier: "the topic of such classifier is really open when it's in fact a critical
component for the integrity of the platforms on which autonomous LLM-based agent systems are
working. It is enough to lead to new research project if we have the resources (we have money and
hardware but at this point, mostly time is lacking to review everything)."

## What exists for the communication graph

- **Dispatch edges:** every subagent transcript has a `.meta.json` beside it (`agentType`, `name`,
  `description`, `toolUseId` of the parent's Agent call, `spawnDepth`, `requestShape`); the parent's
  transcript holds that `tool_use` with its timestamp. In this lab only the PI dispatches
  (`spawnDepth` 1); headless cells run by workers are a second layer, under `/private/tmp/` (cleared
  at a restart) and their own project folders.
- **Message edges:** `SendMessage` calls (worker to worker, worker to PI, PI to worker) with
  timestamps; hand-backs (`SubagentHandback`), task notices and queued attachments in the PI's
  transcript (three forms; the PI parser of wave 9 misses the queued ones, S-w09-explorer-w09-h-1).
- **Life spans and money:** `__statera__/harness.jsonl` per lab (`start`, `named`, `note`, `raise`,
  `end`, with `agent_id`, budgets and spend); the end line's `active_s`.
- **The checking side**, already defined and measured for the PI: raw opens per hand-back wake by
  sender (w09-c5 · MEASURED; `__reports__/wave-09/explorer-w09-k/` section 5 gives the portable
  definitions and the transcript fields). Verifiers check authors by protocol; whether they open the
  author's evidence beyond the head is not measured.
- Nine waves of lab transcripts (`~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-*`),
  one PI model (claude-opus-5-5) and one worker model; a cross-model comparison needs runs on another
  model, which none of the data has.

## Open, with what is known

| # | Direction | Known | First step |
|:--|:--|:--|:--|
| 1 | The communication graph and its replay | the edge sources above; a star (PI at the centre) with author–verifier pairs as the only lateral edges | build the temporal graph for one wave, draw its evolution, then compute per-wave properties (degree, fan-out, pair edges, message reciprocity, waiting time) |
| 2 | Structure against checking | the PI checks explorers 18–21 of 27, authors 10–11 of 57, verifiers 5–6 of 35 (w09-c5) | whether graph position (fan-out at the moment of the hand-back, concurrent in-flight workers, depth) predicts the check, controlling for sender role; "why" will be CONJECTURE |
| 3 | A local judge (items 50, 51) | qwen3.6 with auto mode's rules AUC 0.79 (w09-c8); seven refusals every judge allows (`/Users/hacker/Documents/tmp/murmuration-w09-private/seven_refusals.md`, private) | the user's review of the seven; then the shadow hook is the data source a research project needs |
| 4 | Rules the PI must remember (item 53) | clock times and an invented return, each caught late; two merge slips this wave | a mechanical check on quoted commits and times in a note |

## Reports from wave 9 to start from

- `__reports__/wave-09/explorer-w09-j/00-findings_v0.md`: tool-call classification, five figures,
  `python3 -I __instrumenta__/w09j_figures.py __reports__/wave-09 __reports__/wave-09/explorer-w09-j/figures`.
- `__reports__/wave-09/explorer-w09-k/00-findings_v0.md`: how the PI reads its team's work, five
  figures, `__instrumenta__/w09k_extract.py`, `w09k_figures.py`, `w09k_models.py`.
