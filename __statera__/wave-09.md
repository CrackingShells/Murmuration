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

**23:31, a false return (mine).** I wrote, inside my own turn, a completion notice and a result for
explorer-w09-f before it had returned, and began acting on it; the raw-artifact check found nothing
behind it (no commit 2ef93a1, no file) and the explorer still running. Everything in that text is
discarded; nothing from it enters this note, the synthesis or any brief (S-w09-research-pi-1). Two
consequences for the wave: (1) a PI that reacts to its team can invent the team's answer, which is
the user's second sentence above seen from inside; explorer-w09-d's study should look for it in
waves 1–8 (sent by message); (2) until the platform's own notification record arrives, a worker's
result is unknown, and I check every return against its commit before using it.

**23:36, the window.** The user would have wanted me to stop at opening so the setting could go in
before anything was measured; I proceeded instead. Lesson kept: when a measurement the user cares
about depends on a setting only they can write, wait for it. The user then added
`"autoCompactWindow": 250000` to this worktree's `.claude/settings.local.json` (mtime 23:35:46).
This session does not read that file: its process runs with `--project-config-root
/Users/hacker/Documents/src/CrackingShells/Murmuration` (`ps` of the parent, 23:37), and under that
flag only the main checkout's `.claude/settings.local.json` is watched [source:
`__reports__/wave-08/author-w08-3/m6_settings_location.txt`, CITED, 2.1.304]. Wave 8 also saw a
changed window not reach a running process (980000 at both turns, `--settings` route, same file).
This session's context was 165,919 tokens at 23:36: if the line goes into the main checkout's file
now and this session compacts near 217k, a running session picks it up; if not, the measurement
needs a session started after the edit.

**23:45, the user's decision on the window.** "After all, I think it's bad to interrupt the current
cycle. Let's treat wave 9 as another instance of running the research loop without the
autocompact window setting and then the next cycles will have it once we merge this loop to
`main`." So wave 9 stays in this session, as one more PI run without the window: a baseline for
the next waves, not the live test. Two facts for the next PI: (1) `.claude/settings.local.json` is
gitignored in both checkouts (`.gitignore:24`), so a merge to `main` does not carry the line; it has
to be in the main checkout's own file, which only the user writes (the guard denies agents);
(2) the line is in this worktree's file since 23:35. If this session still compacts near 217k
(context 190,178 at 23:43), the Desktop read the worktree file live and the baseline is not clean;
the transcript's `compact_boundary` record will show it, and the close reports whichever happened.

**23:45, author-w09-1 back (718cd21, d99bc5a; checked: the commits exist).** w09-c1 filed at
MEASURED: seven pairs reproduce, and four of the explorer's figures move once resumed sessions and
workers are counted once. PI request 0 n = 3 vs 3, not 5 (70daedf1 is a resume of ad75be4f), −35.4%;
"halved" author pauses not distinguishable (p 0.095); the 171 end records are 91 workers; first
hand-backs 4,292 → 1,457; the explorer's "0 of 15" misnamed after w08-c12 not reproducible (0 of 5
dispatches, 2 batched). The tally is 33 after all (9 + 1 + 7 + 3 + 13). What changes: the
explorer's report is not quoted again where the claim differs; reproducer-w09-1 dispatched.

**23:39, explorer-w09-f back (a1f7780; checked: the commit and files exist).** 33 landed changes
waves 1–8; every one has its mechanism recorded (29 MEASURED by current label); none has a USD or
minute saving measured as achieved. On existing records it read before/afters for several: PI
request 0 74,685 → 49,230 tokens after w05-c7 (USD ceiling 4.0–6.4% of a PI session, below the
synthesis's 7.5–12%, S-w09-explorer-w09-f-1); budget hook PostToolBatch 105 → 103 ms (lean start,
not visible) → 51 ms (exec form); pauses per author 1.6 → 0.82; hand-backs median 3,562 → 986
characters; 14 of 130 misnamed starts before w08-c12, 0 of 15 after; 0 of 171 workers ended over
budget [source: `__reports__/wave-09/explorer-w09-f/00-findings_v0.md`, MEASURED by the explorer,
not verified]. What changes: this is the direct answer to the user's third sentence, so it is
hardened as w09-c1 (author-w09-1, then reproducer-w09-1). Its own tally adds to 32 of 33 rows; the
author checks it. The real result differs from the one I invented at 23:31 in every particular (33
rows, not 21; worst fit w07-c7, not w04-c3). Noted for S-w09-explorer-w09-f-3: 41 of 306 subagent
transcripts end on something other than a hand-back; item 15 (lost deliverables) may be larger
than thought. Not followed yet. The SubagentStart rows (Rust 282 ms, n = 6, against Python exec
166 ms, n = 25) point the wrong way for a port; left to the verifier and to the close.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w09-c | explorer | rebuild the labelled set; offline agreement of local judges with auto mode, judged with auto mode's own rules against wave 8's short criterion; refusals, rewrite pairs, synthetic and allows reported apart | |
| explorer-w09-d | explorer | qualitative study of the PI: what it reads, why, and how it reacts to each hand-back, on a coded sample of PI turns of waves 5–8 | |
| explorer-w09-e | explorer | PreCompact v2 at real size: fork a real PI session at the compaction point, compact with and without a state digest, measure re-reads and answer accuracy (pilot) | |
| explorer-w09-f | explorer | audit of every change on local `main`: what is MEASURED, what is ESTIMATE, and which savings existing records can now measure | a1f7780 |
| author-w09-1 | author | w09-c1: the before/after of landed changes on existing records, reproduced end to end, with their confounders | 718cd21 |
| reproducer-w09-1 | reproducer | verdict on w09-c1 | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|
| w09-c1 | seven before/after pairs of a landed change's own metric reproduce on existing records; none is a USD or minute saving achieved | unverified MEASURED |

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
