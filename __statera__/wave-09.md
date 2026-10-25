# Wave 09

opened: 2026-10-25 (23:27 by `date`)

## The user's sentence this wave serves

> Before we care about time, however, we must check accuracy: can we find a classifier we can run
> locally that is aligned with the decisions Anthropic's classifier took? Does a classifier one our
> side refuse the same tool calls? Does it allow the same tool calls? (2026-10-24 13:48)

> I think we would probably need to study qualitatively whether the PI context acquisition patterns
> and its way to react to what's coming from its team. (2026-10-24 13:48)

> many were labelled ESTIMATED. If that's the case, there aren't a single thing that landed on `main`
> that has been properly measured? (2026-10-24 13:48)

> the PreCompact hook did not land. But it seems like an interesting location to be creative and
> automate the information we can pass to the PI after compaction so that it doesn't need to
> re-read anything and only trust the output of a semantic search, for example. (2026-10-24 13:48)

And today: "Proceed with wave 9. [...] as always this is not a checklist, you are responsible for
the research of your team." (2026-10-25 23:23). Budget USD 100 (the user's answer at opening).

## What does not add up

- **The wave-8 judges were scored against a criterion we invented, not the one auto mode uses.**
  `claude auto-mode defaults` (CLI 2.1.304) prints the classifier's own rules: 17 allow, 72
  soft_deny, 1 hard_deny, 21 environment entries, 83 KB; the effective config equals the defaults
  [source: `__reports__/wave-09/research-pi/auto_mode_defaults.json`, `auto_mode_config.json`].
  A local judge given the same rules is the fair test of "refuse the same, allow the same". The
  policy is long, which is also S-w09-explorer-w09-b-1's open idea: put the fixed policy first and
  the case last, and the prompt cache carries the policy.
- **The labelled set is gone.** The machine restarted (uptime 8 h at 23:24) and `/private/tmp` was
  cleared: wave 8's redacted set under `/private/tmp/murmuration-w09/` and all wave-8 headless
  folders no longer exist. The scripts are in `__instrumenta__/w09a_*.py`; the set must be rebuilt,
  and it now holds two more days of decisions.
- **The PI is 37% of the lab's money and nobody has watched how it works, only how much it costs.**
  Wave 8 split its USD by source (explorer-w08-d); no one has read what the PI fetches, why, and
  what it does with each hand-back.
- **The compaction window the next PI was to be tested under is not set.** The user remembers
  adding it; I found it in no settings file and in no commit (the 20 commits that name it are lab
  reports; `.claude/` is untracked) [source: `git log --all -S autoCompactWindow` in the main
  checkout; the six settings files read at 23:30]. So "the PI's cost given the context window
  decrease" has no live data yet, and PreCompact v2 can only be tested by replay.
- **"Not a single thing measured."** Every landed change has its mechanism measured; the money it
  saves is counterfactual, so ESTIMATE by definition (wave-8 hand-off, direction 2). Whether any
  landed change can have its money measured from records that now exist is unchecked.

Request 0 of this PI session: 51,098 tokens, all written to the 1-hour cache, Opus 5.5, Desktop
2.1.308 [source: this session's transcript, first assistant record's `usage`].

Spend at opening (23:27): TOTAL USD 546.17 at least; this checkout 1.60 [source:
`scripts/lab_status.py --spend`].

## Reassessments

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w09-c | explorer | rebuild the labelled set; offline agreement of local judges with auto mode, judged with auto mode's own rules against wave 8's short criterion; refusals, rewrite pairs, synthetic and allows reported apart | |
| explorer-w09-d | explorer | qualitative study of the PI: what it reads, why, and how it reacts to each hand-back, on a coded sample of PI turns of waves 5–8 | |
| explorer-w09-e | explorer | PreCompact v2 at real size: fork a real PI session at the compaction point, compact with and without a state digest, measure re-reads and answer accuracy (pilot) | |
| explorer-w09-f | explorer | audit of every change on local `main`: what is MEASURED, what is ESTIMATE, and which savings existing records can now measure | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- Names: explorer-w09-a and -b were used by the two probes filed under wave 8's extra work; their
  puzzle files `__scrupuli__/wave-09-explorer-w09-{a,b}.md` are open and this wave disposes of them.
  This wave's agents start at letter c.
- Models: every worker on its agent file's default (Sonnet), except the PI-like headless sessions of
  explorer-w09-e, which run on Opus because the thing measured is a PI's behaviour.

closed: YYYY-MM-DD
