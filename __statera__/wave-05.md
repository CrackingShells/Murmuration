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
<!-- Correction (16:03): the entry times were first written as estimates (14:5x to 17:4x) and drifted by up to 1 h 40 min. reproducer-w05-8 caught it. They are now the commit times of the entries, with the commit named. -->

- 14:36 (4a6a533), after finding the in-place load: the first step becomes "run this branch on myself"
  before any dispatch, and the plugin's delivery path becomes a probe in the portfolio rather than
  a setup chore.
- 14:43 (27d1f7a), after `/reload-plugins` re-read `murmuration-local` from the main checkout: a Desktop
  worktree session reads the **main** checkout's `.claude/settings.local.json`, so a worktree-only
  switch cannot be made with settings files. The user chose to merge wave 4 first. Merged into
  local main as 4c675ec (not pushed), and the worktree-local marketplace was removed. The main
  settings file was left byte-identical. Consequence for this wave: my own changes reach me only
  when they land on main. Until then, experiments run headless with `--plugin-dir` pointed at this
  branch.
- 14:52 (c928bd1), after explorer-w05-e and explorer-w05-a returned:
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
- 15:08 (5a05785), after b, c and d returned:
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
- 15:26 (46935e8), after w05-c3: E6's rule proposes the allowlist (baba44f). But an allowlist silently drops
  every MCP server the plugin cannot name (user connectors, project servers), and E6 measured
  nothing of that. A metric that misses a cost makes a rule pass for the wrong reason. Protocol v1
  (0bd9570) adds E6b, a denylist, with that metric; author-w05-2 is resumed for it (w05-c6). w05-c3
  goes to its verifier as filed.
- 15:36 (db18700), after explorer-w05-f and w05-c3's verdict (SUPPORTED) and w05-c6:
  - Auto mode puts a classifier round trip on every Bash call: `permissionDecisionMs` has a median
    of 448–747 ms, against 2 ms in bypass. Claude Code's cost records do not show its cost. **Every
    spend figure this lab quotes in auto mode, mine included, is a lower bound** by an unknown
    amount (explorer-w05-f). Narrow allow rules remove the wait for read-only commands but not for
    `python3 -I scripts/...`. A hook that answers "allow" for lab scripts would. That is a
    security trade-off, so it goes to the user and is not built.
  - The first Bash call of a headless run sources `~/.zshrc` for a shell snapshot: 5.7 s idle, and
    10 s timeouts on 17 of 35 snapshots under three parallel launches. `CLAUDE_CODE_SHELL=/bin/bash`
    brings it to 0.5 s (14 of 14). My own check resolved the same python3, git, uv, colgrep and
    claude under both shells, with wall 16.5 s against 10.5 s (n = 1;
    `__reports__/wave-05/research-pi/shell_check.md`). It is not applied to runs already in
    progress. For future drivers it is a free 5–10 s per cell, roughly 11–23 cell-minutes for a
    wave of wave 4's 137 runs (ESTIMATE: 137 × 5–10 s).
  - The PreToolUse hooks may overlap the classifier (with hooks off, the decision was slower). If
    so, PreToolUse savings show less in auto mode. This does not change E7's metric (serial
    seconds); it changes how its saving is read.
- 16:00 (3486d68), after authors 1 and 3 returned:
  - The waiting paragraph is the wave's largest measured gain: cost 0.57 of A at 227k context, in
    3 of 3 runs per arm (w05-c1, before verification). One finding changes how I read the
    probes: a headless main thread writes 1-hour cache entries and a subagent writes 5-minute
    ones (author-w05-1). The PI's own idle waits are therefore probably not cache losses. b's
    expiries after over an hour fit that.
  - E7 failed on my own m1, which no build that removes a start can meet, and on a 500 KB payload
    the platform never sends (31 KB seen). I do not rewrite the rule after the fact. The build goes
    to the user with that reading (S-w05-research-pi-4).
  - A plain commit in this shared checkout swept a staged revert into another author's commit
    (baba44f). I filed w05-c8 (commit by naming paths) and w05-c9 (reassessments in the procedure,
    CONJECTURE). Both are with reproducer-w05-8.
- 16:16 (the closing commit), at close:
  - **PI decision on w05-c1's ESCALATE:**
    - The switch to a subagent worker is accepted on substance and recorded post hoc in protocol
      v1, as its "v2 note".
    - The head is restated in place to the runs (7c09d58).
    - The paragraph gets two untested text fixes: pid and log named per agent, and "4½ minutes"
      (5906331).
    - Not seen by anyone until now: E5's arms were both exported from baba44f, the commit that
      carried the swept-in w04-c5 lean hooks. The two arms are equal in hooks, so the comparison
      stands, but neither ran main's hooks.
  - **w05-c4:** the verifier's true-batch replay shows the second lean build is not only faster.
    It sends an extra message on 11 of 197 transcripts. My puzzle 4 ("blocked for reasons that are
    not about leanness or correctness") was premature. The rule's "not proposed" stands on a real
    behaviour difference as well.
  - **Verifiers changed something in 6 of 7 claims they closed:**
    - two real cache defects (w05-c5);
    - an unrecorded protocol switch and a shared pid file (w05-c1);
    - a replay that could not see parallel batches (w05-c4);
    - "intact" that was only "present" (w05-c6);
    - my own estimated clock times (w05-c9);
    - the missing `git add` for new files (w05-c8).
  - Untracked puzzle: `S-w05-reproducer-w05-1-2b` has an id `/lab-status` does not parse (the
    letter suffix). Its content, the shared pid file seen in the raw logs, is the same as
    S-w05-reproducer-w05-1-1. Parked with it as followed by w05-c1.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w05-a | explorer | wall-clock anatomy of wave 4: timeline, waits, critical path; USD 4, 30 min | yes; Gantt, 6 puzzles |
| explorer-w05-b | explorer | PI main-thread token anatomy (wave 4 and waves 1–3); USD 4, 30 min | yes; structural cost, tools-schema lever, 5 puzzles |
| explorer-w05-c | explorer | worker orientation, waste and resume costs (wave 4, vs 2–3); USD 4, 30 min | yes; cache lapses in long waits, 6 puzzles |
| explorer-w05-d | explorer | non-model overhead: hook starts, lab_status, lab_init, Python start; USD 4, 30 min | yes; auto-mode 0.85 s/call found, 5 puzzles |
| explorer-w05-e | explorer | leanest way for a worktree session to run its own branch of the plugin; USD 4, 30 min | yes; cause found (--project-config-root), 4 puzzles |
| author-w05-1 | author | w05-c1 (E5, how a worker waits), then w05-c2 (colgrep path); USD 12, 75 min, runs ≤ USD 15 | yes; E5 proposes B (cost 0.57 of A at 227k context); c2 CHECKED; runs about USD 10.5 |
| reproducer-w05-1 | reproducer | verify w05-c1, then w05-c2; USD 3, 35 min, runs ≤ USD 3.5 | w05-c1 ESCALATE (unrecorded switch to subagent; title); w05-c2 SUPPORTED |
| author-w05-2 | author | w05-c3 (E6, `tools:` for the PI); USD 5, 40 min, runs ≤ USD 5; resumed for w05-c6 (E6b denylist), USD 3, 25 min | w05-c3 filed: E6 proposes B; connectors dropped (unmetered); w05-c6: E6b proposes D (tip b554266); w05-c7 restates w05-c6 |
| reproducer-w05-3 | reproducer | verify w05-c3 at baba44f/36e1b47; USD 2.5, 20 min | SUPPORTED; title arithmetic loose (medians vs mean) |
| reproducer-w05-6 | reproducer | verify w05-c6; USD 2, 20 min; resumed for w05-c7, USD 0.6, 6 min | w05-c6 OVERSTATED (presence not use; four entries unrun; Artifact a judgement); w05-c7 SUPPORTED |
| author-w05-3 | author | w05-c4 (E7, lean hooks v2), then w05-c5 (E8, lab_status); USD 10, 75 min | yes; E7 not proposed (m1 ill-posed, m3 at 500 KB), set aside 0d3c879; E8 proposed |
| reproducer-w05-4 | reproducer | verify w05-c4; USD 2.5, 25 min | SUPPORTED; true-batch replay found 11 transcripts with an extra message |
| reproducer-w05-5 | reproducer | verify w05-c5; USD 1.5, 15 min | SUPPORTED after two real cache defects were fixed (9da5a47) |
| reproducer-w05-8 | reproducer | verify w05-c8 and w05-c9 (PI-authored); resumed for w05-c10 | w05-c8 SUPPORTED; w05-c9 OVERSTATED (my clock labels were estimates); w05-c10 SUPPORTED |
| explorer-w05-f | explorer | auto mode's per-call cost and the first-Bash shell start; USD 3, 25 min, runs ≤ USD 2 | yes; hidden classifier per call; bash shell 0.5 s first call; 4 puzzles |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|
| w05-c1 | the waiting paragraph: 0 cold requests against 1, cost 0.57 of A at 227k context (author subagent, one task) | MEASURED, restated in place by PI decision on ESCALATE |
| w05-c2 | colgrep path in the agent files is absolute; the relative one searched the plugin source | CHECKED |
| w05-c3 | `tools:` allowlist for the PI: 30.5k to 15.0k tokens at request 0, headless | superseded by w05-c7 (via w05-c6) |
| w05-c4 | lean hooks, second build: hook serial time −52.5 to −56%; behaviour differs on 11 of 197 transcripts in true batches | MEASURED; not proposed by E7, set aside at 0d3c879 |
| w05-c5 | `lab_status.py`: one git call and a parse cache, 835 to 261 ms warm, output identical | MEASURED (on the tip, 9da5a47) |
| w05-c6 | denylist for the PI, first statement | superseded by w05-c7 |
| w05-c7 | `disallowedTools:` for the PI: about 15,690 tokens off request 0 in 4 of 4 pairs, connectors present | MEASURED (on the tip, b554266) |
| w05-c8 | commit by naming paths; a plain commit takes another agent's staging | CHECKED |
| w05-c9 | reassessment entries, first statement | superseded by w05-c10 |
| w05-c10 | six reassessment entries record changes of plan; procedure asks for them | CONJECTURE |

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|
| S-w05-author-w05-1-1 | followed: w05-c1 (worker run as a subagent; protocol v2 note) |
| S-w05-author-w05-1-2 | followed: w05-c1 (the paragraph polls; Monitor not added) |
| S-w05-author-w05-1-3 | parked: open item 19 (the stop-your-jobs clause is unexercised) in __statera__/synthesis.md |
| S-w05-author-w05-1-4 | followed: w05-c1 (the paragraph names `timeout: 270000`) |
| S-w05-author-w05-1-5 | followed: w05-c1 (PI decision: "4½ minutes", 5906331) |
| S-w05-author-w05-1-6 | followed: w05-c2 |
| S-w05-author-w05-1-7 | parked: disclosed in w05-c1 (the dispatcher's cost is inside each run's total) |
| S-w05-author-w05-2-1 | parked: open item 17 (platform facts: the headless Agent tool has no `name`) |
| S-w05-author-w05-2-2 | followed: w05-c7 (denylist chosen; the allowlist's silent drops stated) |
| S-w05-author-w05-2-3 | parked: open item 17 (`tools:` can add a tool) |
| S-w05-author-w05-2-4 | parked: open item 20 (the Desktop check of w05-c7) in __statera__/synthesis.md |
| S-w05-author-w05-2-5 | parked: method note (a token threshold is a cliff; see S-w05-research-pi-4) |
| S-w05-author-w05-2-6 | followed: w05-c6 and w05-c7 |
| S-w05-author-w05-2-7 | parked: disclosed in w05-c3 (cold pilot costs) |
| S-w05-author-w05-2-8 | parked: open item 8 (the report check makes a "write no file" explorer write one) |
| S-w05-author-w05-2-9 | followed: w05-c6 (the verifier traced the wall time to the explorer side) |
| S-w05-author-w05-2-10 | parked: method note (both rules met by under 700 tokens; Artifact is 74% of either) |
| S-w05-author-w05-3-1 | followed: w05-c8 |
| S-w05-author-w05-3-2 | followed: w05-c4 (withdrawn in the exchange; the build differs on 11 of 197 transcripts in true batches) |
| S-w05-author-w05-3-3 | parked: open item 9 in __statera__/synthesis.md |
| S-w05-author-w05-3-4 | parked: open item 9 (block reads cost a process start here) |
| S-w05-author-w05-3-5 | parked: method note (machine load moves wall figures more than the change; interleave) |
| S-w05-author-w05-3-6 | parked: disclosed in w05-c4 (three headless runs, two pilots) |
| S-w05-author-w05-3-7 | parked: open item 9 (failed and denied calls under a PostToolUse-only build) |
| S-w05-author-w05-3-8 | followed: wave 5 reassessment of 15:08 (the weight moved from hooks to waits) |
| S-w05-author-w05-3-9 | parked: open item 9 (two starts per hand-back event) |
| S-w05-explorer-w05-a-1 | parked: open item 4 (whether time boxes set the chain length) |
| S-w05-explorer-w05-a-2 | parked: open item 21 (the experiment pipeline: batch width, pilot cell) in __statera__/synthesis.md |
| S-w05-explorer-w05-a-3 | parked: open item 21 (keep timing records without account identifiers) |
| S-w05-explorer-w05-a-4 | followed: w05-c1 |
| S-w05-explorer-w05-a-5 | parked: open item 6 (a stray background job made the harness log's last end wrong) |
| S-w05-explorer-w05-a-6 | parked: method note (this wave dispatched its probes before the PI's own checks finished) |
| S-w05-explorer-w05-b-1 | parked: open item 22 (platform costs outside the plugin) in __statera__/synthesis.md |
| S-w05-explorer-w05-b-2 | parked: open item 22 |
| S-w05-explorer-w05-b-3 | parked: method note (shares from the long session are not trusted; direct measures used) |
| S-w05-explorer-w05-b-4 | parked: open item 22 (the PI cannot batch its wake-ups) |
| S-w05-explorer-w05-b-5 | parked: open item 22 (a main thread writes 1-hour cache entries, S-w05-author-w05-1-1) |
| S-w05-explorer-w05-c-1 | followed: w05-c1 (the stop-your-jobs clause) |
| S-w05-explorer-w05-c-2 | followed: w05-c2 |
| S-w05-explorer-w05-c-3 | parked: open item 5 (output tokens are estimated, so spend is soft) |
| S-w05-explorer-w05-c-4 | parked: open item 21 |
| S-w05-explorer-w05-c-5 | parked: open item 6 (harness start lines swap names on same-second dispatches) |
| S-w05-explorer-w05-c-6 | followed: w05-c1 |
| S-w05-explorer-w05-d-1 | followed: explorer-w05-f |
| S-w05-explorer-w05-d-2 | parked: open item 9 (platform-recorded hook durations under concurrency) |
| S-w05-explorer-w05-d-3 | followed: explorer-w05-f and the PI's shell check (__reports__/wave-05/research-pi/shell_check.md) |
| S-w05-explorer-w05-d-4 | parked: open item 22 (another plugin's hook timed out once at 10 s) |
| S-w05-explorer-w05-d-5 | followed: w05-c1 |
| S-w05-explorer-w05-e-1 | parked: open item 1 (the Desktop pins the config root to main) |
| S-w05-explorer-w05-e-2 | parked: open item 16 (one lab rule for every script) |
| S-w05-explorer-w05-e-3 | parked: explained (the PI removed the setup before explorer-w05-e read the files; wave note 14:43) |
| S-w05-explorer-w05-e-4 | parked: open item 9 (fixed platform cost per hook start) |
| S-w05-explorer-w05-f-1 | parked: open item 23 (auto mode's classifier) in __statera__/synthesis.md |
| S-w05-explorer-w05-f-2 | parked: open item 23 (its cost is in no record) |
| S-w05-explorer-w05-f-3 | parked: open item 21 (bash for headless drivers) |
| S-w05-explorer-w05-f-4 | parked: open item 23 (allow rules cannot match lab scripts) |
| S-w05-reproducer-w05-1-1 | followed: w05-c1 (PI decision: pid and log named per agent, 5906331) |
| S-w05-reproducer-w05-1-2 | followed: w05-c1 (PI decision: "4½ minutes") |
| S-w05-reproducer-w05-1-3 | parked: method note (A's cost varies with the worker's own requests; n = 3) |
| S-w05-reproducer-w05-1-4 | parked: open item 1 (agent text reaches sessions only once it lands on main) |
| S-w05-reproducer-w05-3-1 | parked: open item 17 |
| S-w05-reproducer-w05-3-2 | parked: method note (a hand-back reaches the PI as a message, not in the Agent result) |
| S-w05-reproducer-w05-3-3 | followed: w05-c7 (scope) and S-w05-research-pi-3 |
| S-w05-reproducer-w05-3-4 | parked: method note (threshold margin) |
| S-w05-reproducer-w05-4-1 | followed: w05-c4 (197 distinct transcripts) |
| S-w05-reproducer-w05-4-2 | followed: w05-c4 (true-batch replay) |
| S-w05-reproducer-w05-4-3 | parked: open item 9 (wall at 500 KB depends on load; CPU does not) |
| S-w05-reproducer-w05-4-4 | followed: w05-c4 |
| S-w05-reproducer-w05-4-5 | parked: open item 9 (m4 tested at 164%, once) |
| S-w05-reproducer-w05-4-6 | parked: corrected by its writer (puzzle 7) |
| S-w05-reproducer-w05-4-7 | parked: correction recorded by its writer |
| S-w05-reproducer-w05-5-1 | followed: w05-c5 (fixed at 9da5a47) |
| S-w05-reproducer-w05-5-2 | followed: w05-c5 |
| S-w05-reproducer-w05-5-3 | followed: w05-c5 |
| S-w05-reproducer-w05-5-4 | followed: w05-c5 (fixed at 9da5a47) |
| S-w05-reproducer-w05-5-5 | parked: open item 24 (whether the cache is worth its code) in __statera__/synthesis.md |
| S-w05-reproducer-w05-5-6 | parked: open item 24 (headline numbers from 4eb2272) |
| S-w05-reproducer-w05-6-1 | followed: w05-c7 |
| S-w05-reproducer-w05-6-2 | followed: w05-c7 |
| S-w05-reproducer-w05-6-3 | parked: open item 20 |
| S-w05-reproducer-w05-6-4 | parked: open item 8 |
| S-w05-reproducer-w05-6-5 | parked: open item 20 (request-0 composition) |
| S-w05-reproducer-w05-8-1 | followed: w05-c8 (7ea877d) |
| S-w05-reproducer-w05-8-2 | followed: w05-c8 (scope as answered in the exchange) |
| S-w05-reproducer-w05-8-3 | followed: wave-05 note corrected at 7ea877d |
| S-w05-reproducer-w05-8-4 | followed: w05-c10 |
| S-w05-reproducer-w05-8-5 | followed: w05-c10 |
| S-w05-reproducer-w05-8-6 | parked: method note (git has one identity; attribution rests on messages) |
| S-w05-research-pi-1 | followed: w05-c10 |
| S-w05-research-pi-2 | parked: open item 1 |
| S-w05-research-pi-3 | followed: w05-c8 |
| S-w05-research-pi-4 | followed: w05-c4 (partly withdrawn: the build does change behaviour on 11 of 197 transcripts) |

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
  (about 14:40, before 27d1f7a) "You can do worktree local this session but for the future should we add a
  project-scope or local-scope hook to always run plugin reinstall/update on SessionStart or
  Resume?"; (about 14:41) chose "Merge wave 4 first".
- **Spend at close (16:15):** this checkout USD 26.29 at list price (a lower bound: the session is
  open), and headless runs under `/private/tmp/murmuration-w05/` USD 18.18 (exact, cost-state, all
  ended). That is **at least USD 44.47 against the user's 150**. Both figures are lower bounds in
  auto mode, because the permission classifier's cost is in no record (explorer-w05-f)
  [source: lab_status.py at this commit, run in this checkout and in /private/tmp/murmuration-w05/].
- The probes were dispatched after the merge but before a second `/reload-plugins`. Wave 4 changed
  `agents/explorer.md` by one line, so these explorers may carry the pre-merge definition.

closed: 2026-10-21
