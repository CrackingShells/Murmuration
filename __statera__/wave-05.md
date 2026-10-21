# Wave 05

opened: 2026-10-21

## The user's sentence this wave serves

Quoted from the main checkout's `__statera__/user_words.md` (2026-10-21 14:29). The prompt hook
wrote it there, not to this worktree, for the reason found in wave 4 (open item 1):

> You can proceed with a wave 5 to self optimize your lab system. I'd really like that you work on
> optimizing the speed and leanness of operating your lab. Of course, just like the other puzzle,
> this is not a checklist item but part of the trajectory.

> note: make sure you are always running the latest version of the plugin on yourself

Later in the session (sent mid-turn; the hook recorded both in the main checkout's file at 14:3x):

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
- 14:5x, after `/reload-plugins` re-read `murmuration-local` from the main checkout: a Desktop
  worktree session reads the **main** checkout's `.claude/settings.local.json`, so a worktree-only
  switch cannot be made with settings files. The user chose to merge wave 4 first. Merged into
  local main as 4c675ec (not pushed), and the worktree-local marketplace was removed. The main
  settings file was left byte-identical. Consequence for this wave: my own changes reach me only
  when they land on main. Until then, experiments run headless with `--plugin-dir` pointed at this
  branch.
- 15:1x, after explorer-w05-e and explorer-w05-a returned:
  - The Desktop pins every session's config root to the main checkout (`--project-config-root`,
    seen in the process's command line, reproduced headless; explorer-w05-e). That one flag
    explains wave 4's misrouted prompt, my misrouted `--scope local`, and the ignored worktree
    settings. The user's reinstall-on-start idea cannot work: a directory plugin has nothing to
    update, and SessionStart fires after loading. So "latest on myself" means keeping main current,
    or a symlinked marketplace path. Both are the user's call. Plugin delivery is dropped as a
    research direction; what is left goes to the user.
  - Wave 4's 88 minutes were not spent by the PI (75% idle, about 11 min on the critical path) or
    by hooks. They went into serial stages of headless experiment cells inside one author's chain
    (53 of 79 min), 15 min of it rerunning cells after a confound was found late (explorer-w05-a,
    MEASURED). In the Gantt, the authors' lanes are mostly ≥45 s waits. **The speed of the lab is
    the speed of its experiments.** This moves the weight of the wave from hooks and the PI toward
    how workers run and check experiments: pilot one cell before a batch, batch width, waits that
    can still read messages. I hold that until b, c and d return.
- 15:5x, after b, c and d returned:
  - **Four probes point at one mechanism: how a worker waits.**
    - 80% of worker Bash time is 48 calls of 60 s or more (d).
    - Every mid-run cache lapse is a single wait longer than 5 minutes, about 17% of worker list
      price (c).
    - A message sent to a worker in such a wait goes unread for 1.5–2.5 minutes (a).
    - The harness points workers to Monitor, which none of them has (c).
    - This becomes w05-c1 (E5).
  - Orientation is small (about 3%, c), and re-reads are negligible (b, c). **Trimming the skill or
    framing is dropped:** it would save 1–3%.
  - The PI's cost is structural: about 53k tokens of tool schemas re-read on every request (b).
    This becomes w05-c3 (E6), tested because the lever is a CONJECTURE.
  - Hooks and `lab_status.py` are real but small (156 s and 0.8 s per wave, d). They become
    w05-c4 and w05-c5, with a per-wave metric instead of E4's two separate thresholds.
  - An unexplained 0.85 s per Bash call in auto mode is larger than all the plugin's hooks (d).
    That is explorer-w05-f.
  - Parked for now, with reasons in the dispositions at close:
    - the listing re-injection of waves 1–3 (2.5% in wave 4);
    - cache expiry while the human is away after `wrap_up` (an app behaviour);
    - the PI's wake-ups per hand-back (the PI cannot batch notifications);
    - "pilot one cell first" and side-by-side cells. These are written into the E5–E8 protocol as
      practice, not tested as claims.
  - Pre-registration committed at e0fc3ab before any run.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w05-a | explorer | wall-clock anatomy of wave 4: timeline, waits, critical path; USD 4, 30 min | yes; Gantt, 6 puzzles |
| explorer-w05-b | explorer | PI main-thread token anatomy (wave 4 and waves 1–3); USD 4, 30 min | yes; structural cost, tools-schema lever, 5 puzzles |
| explorer-w05-c | explorer | worker orientation, waste and resume costs (wave 4, vs 2–3); USD 4, 30 min | yes; cache lapses in long waits, 6 puzzles |
| explorer-w05-d | explorer | non-model overhead: hook starts, lab_status, lab_init, Python start; USD 4, 30 min | yes; auto-mode 0.85 s/call found, 5 puzzles |
| explorer-w05-e | explorer | leanest way for a worktree session to run its own branch of the plugin; USD 4, 30 min | yes; cause found (--project-config-root), 4 puzzles |
| author-w05-1 | author | w05-c1 (E5, how a worker waits), then w05-c2 (colgrep path); USD 12, 75 min, runs ≤ USD 15 | |
| author-w05-2 | author | w05-c3 (E6, `tools:` for the PI); USD 5, 40 min, runs ≤ USD 5 | |
| author-w05-3 | author | w05-c4 (E7, lean hooks v2), then w05-c5 (E8, lab_status); USD 10, 75 min | |
| explorer-w05-f | explorer | auto mode's per-call cost and the first-Bash shell start; USD 3, 25 min, runs ≤ USD 2 | |

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
- The user's mid-turn messages did reach UserPromptSubmit and were recorded, in the main checkout's
  file. Their dialog answers were not, as in waves 2–4. Quoted here so the lab keeps them:
  (14:4x) "You can do worktree local this session but for the future should we add a
  project-scope or local-scope hook to always run plugin reinstall/update on SessionStart or
  Resume?"; (14:5x) chose "Merge wave 4 first".
- The probes were dispatched after the merge but before a second `/reload-plugins`. Wave 4 changed
  `agents/explorer.md` by one line, so these explorers may carry the pre-merge definition.
