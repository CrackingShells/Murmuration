# Wave 05

opened: 2026-10-21

## The user's sentence this wave serves

Quoted from the main checkout's `__statera__/user_words.md` (2026-10-21 14:29). The prompt hook
wrote it there, not to this worktree, for the reason found in wave 4 (open item 1):

> You can proceed with a wave 5 to self optimize your lab system. I'd really like that you work on
> optimizing the speed and leanness of operating your lab. Of course, just like the other puzzle,
> this is not a checklist item but part of the trajectory.

> note: make sure you are always running the latest version of the plugin on yourself

Later in the session (in the chat; not yet in any `user_words.md`, see the Notes below):

> i note that you never consider replan or reassessment as part of the plan for the purpose of
> pushing forward. It feels a bit strange or uncanny given the point of your agent system is to be
> a research lab and explore a topic. That's puzzling.

> Oh, and I forgot to give you the budget: you can spend 150USD for this wave. Take the time you
> need.

## What does not add up

- **The lab does not run the version it is improving.** Waves 3 and 4 changed hooks, agents and
  skills on their branches. Each PI session, though, loaded the plugin in place from the main
  checkout's working tree (`claude plugin list`: "Read from: …/src/CrackingShells/Murmuration";
  `claude plugin details`: 7 hooks, which only the source tree has, while the cache copy at 9eb759b
  has 2) [source: this session, 14:4x JST]. The "update installation" the user asked for at the
  close of wave 3 refreshed a cache copy that is never read. So whatever wave 4 learned about speed
  was learned on a plugin that its own PI was not running.
- **"Local scope" in a worktree means the main checkout.** `claude plugin marketplace add
  --scope local`, run from this worktree, wrote to the main checkout's `.claude/settings.local.json`
  (reverted by the PI within minutes; the main file is again byte-for-byte the pre-wave copy)
  [source: this session]. The same misrouting as the prompt hook in wave 4, through a different
  path.
- **Where a wave's time goes has never been measured.** Wave 4 took 88 minutes and cost at least
  USD 53 [source: `__statera__/wave-04.md`, Notes]. Every speed measurement so far was of hooks:
  about 0.1 s per call. The PI main thread is the largest single cost line in the study, USD 75.48
  of 204.11 [source: `lab_status.py` at 1b5ffa4, 14:4x JST]. Nobody has looked at what it spends
  that on, or at how long workers wait on each other (author, then verifier, then the exchange).
- **The PI's plans are written as checklists.** The user noticed that the plan never contains a
  re-plan. `waves.md` says "plan only the current wave", but nothing in it or in the wave template
  asks the PI to stop and revise mid-wave. The wave-4 note's "PI decisions" are all reactions to
  escalations, and none says "this result changes what we do next". A lab that does not re-plan
  pays for runs whose reason has expired. That is a leanness problem, not only a style problem.

## Reassessments

<!-- PI: one entry each time a result changes the plan: what came back, what changes, what is dropped. -->

- 14:5x, after finding the in-place load: the first step becomes "run this branch on myself"
  before any dispatch, and the plugin's delivery path becomes a probe in the portfolio rather than
  a setup chore.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- Budget: USD 150 for this wave (the user's), with no time limit. Baseline at opening:
  `lab_status.py` TOTAL USD 204.11 at least, this checkout USD 1.75 [source: lab_status.py at
  1b5ffa4]. Headless runs go under `/private/tmp/murmuration-w05/`, so their cost can be read
  separately.
- This branch was fast-forwarded to the wave-4 tip (1b5ffa4), so wave 5 builds on wave 4's
  unmerged work. Landing is still the user's decision.
- Running the latest plugin on myself (the user chose "worktree-local"): an untracked
  `.claude-plugin/marketplace.json` named `murmuration-w5` (gitignored), declared and enabled in
  this worktree's own `.claude/settings.local.json`, with `murmuration-local` disabled there. It
  takes effect at `/reload-plugins` or on reopening the session.
- The user's mid-turn chat messages (the re-plan remark, the budget) did not go through
  UserPromptSubmit as separate prompts. Whether the hook recorded them is to be checked.
