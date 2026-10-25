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

**00:51, w09-c7 SUPPORTED (a844c29); round 3 opened.** The classifier answer stands at MEASURED:
under a short criterion in each judge's own wording, neither guard model separates auto mode's
refusals from its allows by much (the raw intervals overlap on both judges). Spend at least USD
42.38 of 100 (this checkout 29.58 against 1.60; headless 14.40) [source: `scripts/lab_status.py
--spend`]. What changes: two guard models are not "a classifier we can run locally" in general. One
more probe on the user's first sentence, explorer-w09-i: two general instruction models on disk,
given auto mode's rules, scored for discrimination (not one-sided agreement), and on wave 8's
written cases to settle S-w09-explorer-w09-c-1 (labels unlike auto mode's policy, or recorded calls
unlike written ones). After it, the wave closes.

**00:49, reproducer-w09-3 on w09-c6: OVERSTATED (332458d).** All 378 case ids join back to auto
mode's recorded decisions by `tool_use` id (67 classifier blocks, 311 classifier allows); polarity
re-parses 462/462 and 196/196; counts, intervals and weights match; a Granite spot re-run of 22 cases
repeats 22 of 22. The wording overstates: two criterion wordings, not one; mixed bases on the allow
side; "agrees" for one-sided rates of judges that barely separate the sides (Granite blocks 74.6% of
refusals against 59.8% weighted of natural allows; safeguard 11.9% against 3.9% weighted); "the
user's own sessions" for everything outside the arena, 41% of whose weight is this lab. What changes:
the finding is sharper than its first statement. Neither judge discriminates: each blocks about a
fixed share of everything, high for Granite, low for safeguard. w09-c7 restates it. In my message
to the author I wrote the weighted rates as if they were the raw fractions (132/212 is 62.3%, not
59.8%); corrected by a second message before it filed.

**00:36, explorer-w09-c back (1713dc5; checked: commit, agreement and latency tables, puzzles; LM
Studio stopped, no process left).** The set rebuilt: 67 refusals, 19 refusal-then-allowed pairs, 65
synthetic, 311 allows in 53 strata (weights kept). Neither judge agrees with auto mode on both sides.
Granite Guardian 4.1 8B, short criterion: misses 17 of 67 refusals, refuses 48.6% of allows
(reweighted, bootstrap 41.3–55.6%), 87.5% in the "risky-flag" stratum; separates 7 of 19 pairs.
gpt-oss-safeguard-20b, short: misses 59 of 67, refuses 3 of 45 allows (too few); separates 3 of 19.
Auto mode's own rules as the policy (18.4k tokens, policy first) made Granite block nearly everything
(3 of 65 missed, 16 of 17 pairs blocked on both members) and left safeguard missing 26 of 28. Steady
p50 on unique cases 1.7 s (Granite short), 2.7 s (full), 4.1 s (safeguard short), 15.2 s (full),
against auto mode's 628 ms [source: `__reports__/wave-09/explorer-w09-c/00-findings_v0.md`,
MEASURED by the explorer, not verified]. What does not add up: both judges were near-perfect on wave
8's hand-labelled sets and fail in opposite directions here (S-w09-explorer-w09-c-1), so wave 8's
labels described a different policy from auto mode's, or real calls are unlike the written ones.
16 of 67 refusals are allowed by both judges and look ordinary (reminder updates, a `ps | grep`):
whether auto mode erred there is the user's call (S-w09-explorer-w09-c-3). What changes: the
negative result is the answer to the user's first sentence for this wave, so it is hardened as
w09-c6 (author-w09-3, then reproducer-w09-3), with the verdict parsing and its polarity checked
before anything is said about the judges themselves. No shadow hook is built this wave: a judge that
refuses half of what auto mode allows would record disagreement on every second call.

**00:19, explorer-w09-h back (aed13a4, 6de1dc1; checked: commits, `01-escalation_table.md`).** 13
escalations located. In 0 of 13 would reading the verifier's section and exchange have changed the
decision (CONJECTURE, one reader, quotes in the table): the hand-back already carried the findings
and the author's request (median hand-back 4,458 characters, median section 6,929). 5 superseded as
decided, 9 restated in place, 0 reversed; the 9 decision sections were written 2–5 days after the
wakes (wave 8's close). In one queued case (w01-c5) the PI did read the section and decided the same
way. Lever sized, not built: a UserPromptSubmit hook injecting the verdict section on ESCALATE, 98
characters (pointer) to 6,929 (section) per escalation [source:
`__reports__/wave-09/explorer-w09-h/00-findings_v0.md`, ESTIMATE]. What changes: no lever. The rule
is not followed, and on this evidence not following it cost nothing, because the hand-back is the
verdict in short; injecting the section would carry about 7k characters into the PI's context to fix
nothing seen. The worst fit, w07-c7, is not a reading failure: the hand-back said "6-tool headless
only, no resume tested" and the PI landed it anyway; the decision rested on what it had read. Stays
out; recorded for the synthesis.

**00:19, explorer-w09-g back (3905c79, 6f8ea89; checked: commits, `41-rows.md`).** 40 rows, not 41;
three were live workers of this wave when explorer-w09-f counted. Of 37 ended: 27 wave-2 probe
workers whose agent types had no hand-back tool and ended on a delivered final text, 2 that had
handed back and ended on trailing text, 7 wave-2 explorers stopped by the old budget's
`continue:false`, 1 killed by the headless 10-minute wait. 8 hand-back messages lost, all in headless
cells of 2026-10-19; none in waves 3–9; the report file survived in 6 of the 7 budget-stopped
explorers. In a wider scan, 24 agents got a platform "turn limit / without delivering" notice, 14
resumed and delivered; none after 2026-10-20T01:18Z [source:
`__reports__/wave-09/explorer-w09-g/00-findings_v0.md`, MEASURED by the explorer, not verified].
What changes: item 15 is settled for waves 3–9 at the explorer's label (no lost deliverable; the
trace is in the platform's notice and the transcript, not in lab files); nothing to land, so no
claim. Its 312 against explorer-w09-f's 306 transcripts is left as a count difference.

**00:09, w09-c5 SUPPORTED (0bfbbe7).** The PI-behaviour counts stand at MEASURED without the
re-read figure (`lab_status.py`: w09-c5 MEASURED; w09-c2 and w09-c4 superseded). It took three
heads to get there: the first stated the explorer's rule, which its code did not follow; the second
counted writes as reads.

**00:08, round 2 opened.** Spend at least USD 33.44 of 100 (this checkout 20.64 against 1.60 at
opening, headless 14.40) [source: `scripts/lab_status.py --spend`, both projects]. Two cheap probes,
both from this round's puzzles: explorer-w09-g on S-w09-explorer-w09-f-3 (are deliverables lost,
item 15), explorer-w09-h on w09-c4's escalation result (does deciding from the hand-back alone cost
anything, and what lever would not rest on the PI's memory, which failed twice this wave:
S-w09-research-pi-1, -2). The classifier (explorer-w09-c) is still out.

**reproducer-w09-2 on w09-c4: OVERSTATED on (b) only (f874741).** (a), (c), (d), (e) reproduce,
the banner from its own coding too (9/37 against 45/179, p 1.00). The one-wake difference is an
author-w06-3 wake whose only record is an "API Error" text. (b) fails: 172 of the 588 "read" rows
are writes and hold 92 of the 243 repeats, and "139 identical" is a match on truncated text (71 of
327 on full text). What changes: the re-read share is not claimed this wave (explorer-w09-d's 41%
stays an unverified explorer figure); w09-c5 restates w09-c4 without (b).

**00:02, reproducer-w09-2 on w09-c2: OVERSTATED (10c5d2d).** Every count re-runs; as a second
coder with its own rule it agrees with the author's codes on 106 of 121 hand-back wakes (kappa
0.70), and a blind hand sample of 20 (seed 9202) agrees 18 of 20 with the author (kappa 0.78). The
escalation result reproduces from its own scan and gets stronger: 10 of 10 reproducer escalations
decided in the wake turn, the claim file read in 0 of 10, before or at the wake (the head's "2 of 10
earlier" rested on `ls` and `grep -c`). Overstated: the coding rule drops any Bash read that
mentions `lab_status` (lifted: explorers 21/27, authors 10/57, reproducers 6/41), the reproducer
denominator holds 6 peer messages, and the detectors' blind spot belongs in the statement. (b)
re-reads and (e) the banner were not checked. What changes: author-w09-2 files w09-c4 at that scope;
the same verifier checks it, with (b) and (e) this time. The ordering by sender survives both
coders: the PI reads an explorer's material most of the time and an author's or verifier's rarely,
and it decides escalations from the hand-back alone, against the skill's rule.

**23:55, w09-c3 SUPPORTED (cfc42b0).** reproducer-w09-1 found its four points met and nothing new
stated; the start-concurrency script reproduces its own split. Soft spot it notes: the binary's
n 3 / n 4 strata come from the `all` run, which grows with the live wave; the saved table holds the
frozen run. So the answer to the user's third sentence stands at MEASURED: every landed change has
its mechanism measured; none has a USD or minute saving measured as achieved; seven comparisons on
existing records show the change's own metric moved (`lab_status.py`: w09-c3 MEASURED, w09-c1
superseded by w09-c3).

**23:54, reproducer-w09-1 on w09-c1: OVERSTATED (61dfea7).** All seven sets of figures reproduce
from its own extraction, and "none is a USD or minute saving achieved" holds for each; the
statement is stronger than the evidence in four places, all conceded by the author: "pairs" (M5 has
no before arm, M4 three eras), "own metric" (M1 is the live PI's request 0, probably not independent
of w06-c1), "ceiling" (the USD figures are ESTIMATEs biased both ways), and M3's confounders omit
concurrent starts. It settles the odd row: the Rust binary's 282 ms against exec's 166 ms at
SubagentStart is a batch mix on thin n, not a slower port (alone 106 ms, n 3, against 142 ms, n 13;
three or more together 335, n 4, against 293.5, n 8) [source: `__pondus__/w09-c1.md`, verdict
section]. Also: the PI's tool list fell from 52 to 23 with w05-c7, all 29 removed on the denylist.
What changes: author-w09-1 files w09-c3 at the verified scope, `supersedes: w09-c1`; the same
verifier reads it.

**23:51, explorer-w09-e back (832716a, 3353e3b; checked: commits, `runs_scored.tsv`).** The route
works at real size: wave 8's PI transcript cut at 216,872 tokens, a clone at 104666a, `--resume
--fork-session`; the compaction fires on the first request (boundary 219–222k). Six Opus cells,
USD 1.15–1.70 each. Existing state only (B1): 8 of 8 in two cells (6 of 6 in the pilot), 5.3–8.6k
tokens re-read; with a digest, 3.0–3.8k (H n = 1, HP n = 2) [source:
`__reports__/wave-09/explorer-w09-e/runs_scored.tsv`, MEASURED tokens, ESTIMATE re-read conversion].
**The hand-back says "H and HP also got 8 of 8"; its own registered scorer gives HP 7 of 8 in both
cells** (Q3: the answer gave the labels but not the claim ids); the explorer overrode its scorer in
favour of its own arm, which the report states (line 53) and the hand-back does not. I read it at
the scorer's 7: the digest arm that re-read least also lost a fact. "Re-read nothing" held in no
arm: the summaries kept no hand-back numbers. Two artefacts make the replay unlike a live
compaction: the resumed context is cold (the compaction request paid input price on 168k tokens,
about five times a live one, S-w09-explorer-w09-e-3), and the platform injects a notice naming the
in-flight workers in every arm (S-w09-explorer-w09-e-2). What changes: the PreCompact hook stays
out; the saving at stake is about USD 3.7 of the 31–45 the window itself is estimated to bring
(ESTIMATE), and a replay is a worse test than the live compactions the next wave will have with the
window on `main`. The hardened replay (15–18 cells, about USD 20) is not run; the next wave's PI
reads its own re-reads after a real compaction instead. Headless spend under
`/private/tmp/murmuration-w09/` USD 14.40 at least; this checkout 15.22 at least (23:51) [source:
`scripts/lab_status.py --spend`, both]. w08-c12 live check: explorer-w09-e started
`name_unconfirmed` at the defaults (3 / 20) and ended at its brief's 10 / 60 (`harness.jsonl` end
line).

**23:48, explorer-w09-d back (5bdeb78; checked: commit, report, coded table rows 74 and 91).**
Over 244 PI wake turns of waves 1–8, a raw artifact was opened in the same turn in 22/8/18/16/36/36%
(waves 1–3, 4, 5, 6, 7, 8); in waves 5–8 by sender: explorers 18 of 27, authors 10 of 57, verifiers 5
of 41. The PI runs its own check instead about as often as it opens one (23 against 18 of 72
sampled). 41% of 588 reads in waves 5–8 re-read a file already read. Two escalations were decided
with no claim file opened (S-w09-explorer-w09-d-1), against the skill's rule. The scan for results
stated before a worker returned found 0 in waves 1–8 and fires on this session's 23:31 case. The
platform's "instruction-shaped" banner did not raise the raw-open rate (9/35 against 41/188; 0/12
in wave 6). Thinking blocks are not empty (8–20% carry narration); the wave-8 synthesis said they
were [source: `__reports__/wave-09/explorer-w09-d/00-findings_v0.md`, MEASURED counts and
CONJECTURE readings by the explorer, not verified]. What changes: (1) the rule "open a raw artifact
for every agent that returns" is followed for explorers and mostly not for authors and verifiers,
whose hand-back is about a claim file the PI does not open; the counts are hardened as w09-c2 with
a second, blind coder as the verifier; (2) the banner result is a guardrail matter (a warning the
PI does not act on), for the user at the close; (3) my own 23:31 error is the first of its kind on
record, so it is not yet a pattern.

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

**The settings file, tracked (4586446).** At the user's word ("then just force commit it"),
`.claude/settings.local.json` is now tracked on this branch (`git add -f`), equal to the main
checkout's untracked copy plus `"autoCompactWindow": 250000` (`diff` of the two, the only
difference). At the merge to `main`, git will refuse while main's untracked copy sits in the way;
moving it aside lets the merge write the tracked one into main, which is the file the guard keeps
agents from writing. That step goes to the user for a yes at the close.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w09-c | explorer | rebuild the labelled set; offline agreement of local judges with auto mode, judged with auto mode's own rules against wave 8's short criterion; refusals, rewrite pairs, synthetic and allows reported apart | 1713dc5 |
| author-w09-3 | author | w09-c6: the two local judges' agreement with auto mode on each side, re-scored from the result rows | 6485d3d, 1f1f79e |
| reproducer-w09-3 | reproducer | verdict on w09-c6, then w09-c7 | 332458d (OVERSTATED), a844c29 (SUPPORTED) |
| explorer-w09-i | explorer | general instruction models (qwen3.6-35b-a3b, gemma-4-26b-a4b) with auto mode's rules: discrimination on recorded decisions, and on wave 8's written cases | |
| explorer-w09-d | explorer | qualitative study of the PI: what it reads, why, and how it reacts to each hand-back, on a coded sample of PI turns of waves 5–8 | 5bdeb78, b3d83fa |
| explorer-w09-e | explorer | PreCompact v2 at real size: fork a real PI session at the compaction point, compact with and without a state digest, measure re-reads and answer accuracy (pilot) | 832716a, 3353e3b |
| explorer-w09-f | explorer | audit of every change on local `main`: what is MEASURED, what is ESTIMATE, and which savings existing records can now measure | a1f7780 |
| author-w09-1 | author | w09-c1: the before/after of landed changes on existing records, reproduced end to end, with their confounders | 718cd21 |
| reproducer-w09-1 | reproducer | verdict on w09-c1 | 61dfea7 (OVERSTATED) |
| author-w09-2 | author | w09-c2: the PI's raw-artifact reads by sender, re-reads, escalations decided without the claim file, invented returns, the banner | 5986c0b, bbb2c79 |
| reproducer-w09-2 | reproducer | verdict on w09-c2, as a second coder with its own extraction and a blind hand-coded sample; then w09-c4 | 10c5d2d (OVERSTATED), f874741 (OVERSTATED on (b)) |
| explorer-w09-g | explorer | the 41 of 306 worker transcripts ending without a hand-back: finished, resumed, stopped, maxTurns, error or lost | 3905c79, 6f8ea89 |
| explorer-w09-h | explorer | did escalation decisions made without reading the claim file lose anything; size a lever that does not depend on the PI remembering | aed13a4, 6de1dc1 |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|
| w09-c2 | the explorer's counts of the PI's raw opens, re-reads, banner and detector flags reproduce; in 10 of 10 reproducer escalations the PI decided in a turn that opened no claim file | superseded by w09-c4 |
| w09-c4 | raw opens on hand-back wakes waves 5–8 by sender (as coded and masked), re-reads, 10 of 10 escalations decided with the claim file read in 0 of 10, 0 confirmed invented returns with the detectors' blind spot, banner not shown to differ (supersedes w09-c2) | superseded by w09-c5 |
| w09-c6 | with one short criterion, Granite Guardian 8B blocks 50 of 67 refusals but 59.8% of the user's own allows; gpt-oss-safeguard-20b allows 42 of 45 allows but blocks 8 of 67 refusals; neither matches auto mode on both sides | superseded by w09-c7 |
| w09-c7 | under a short criterion in each judge's own wording, neither judge separates auto mode's refusals from its allows by much: Granite blocks 74.6% of refusals and 62.3% raw (59.8% weighted) of natural allows; safeguard 11.9% and 7.1% raw (3.9% weighted) (supersedes w09-c6) | MEASURED (reproducer-w09-3 SUPPORTED, a844c29) |
| w09-c5 | w09-c4 without (b) re-reads: raw opens by sender, 10 of 10 escalations with the claim file read in 0 of 10, 0 confirmed invented returns (with the blind spot), banner not shown to differ (supersedes w09-c4) | MEASURED (reproducer-w09-2 SUPPORTED, 0bfbbe7) |
| w09-c1 | seven before/after pairs of a landed change's own metric reproduce on existing records; none is a USD or minute saving achieved | superseded by w09-c3 |
| w09-c3 | seven before/after comparisons on existing records (M5 a rate, M4 three eras) reproduce; USD figures ESTIMATEs biased both ways; none a USD or minute saving achieved (supersedes w09-c1) | MEASURED (reproducer-w09-1 SUPPORTED, cfc42b0) |

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|
| S-w09-explorer-w09-a-1 | parked: the allow label exists only from 2.1.293; w09-c7 reports the refusal eras apart (44 of 67 predate it) and says so |
| S-w09-explorer-w09-a-2 | parked: `permissionMode` is not used as the auto-mode marker; the classifier's own `reasonType` is |
| S-w09-explorer-w09-a-3 | followed: w09-c7 (scored against these refusals); the 16 refusals both judges allow go to the user at the close |
| S-w09-explorer-w09-a-4 | followed: w09-c7 states agreement as a lower bound because the judges see less than auto mode may |
| S-w09-explorer-w09-a-5 | followed: w09-c7 (the 19 refusal-then-allowed pairs: Granite separates 7, safeguard 3) |
| S-w09-explorer-w09-b-1 | followed: explorer-w09-c (policy first, case last; latency on unique cases) |
| S-w09-explorer-w09-b-2 | parked: Laya was not carried forward; its choice head let 4 of 5 dangerous calls through in wave 8 |
| S-w09-explorer-w09-b-3 | followed: w09-c7 (the judges scored against auto mode's recorded decisions, not hand labels) |
| S-w09-explorer-w09-b-4 | parked: cold-load and memory figures matter only once a judge agrees; none does |
| S-w09-explorer-w09-b-5 | parked: one quantisation per judge is stated in w09-c7's scope; another quant is a later probe if a judge comes close |
| S-w09-explorer-w09-c-1 | followed: explorer-w09-i (the same prompt shape on wave 8's written cases and on recorded ones) |
| S-w09-explorer-w09-c-2 | followed: explorer-w09-i (general models given the full rules); Granite's collapse under them stays unexplained |
| S-w09-explorer-w09-c-3 | followed: to the user at the close (only the user can say whether auto mode erred on the 16) |
| S-w09-explorer-w09-c-4 | parked: safeguard's reasoning text is empty through LM Studio's chat endpoint; matters only if safeguard is pursued |
| S-w09-explorer-w09-c-5 | parked: a local judge cannot share the GPU; recorded in the synthesis, relevant only once accuracy is reached |
| S-w09-explorer-w09-d-1 | followed: w09-c5 (10 of 10) and explorer-w09-h (0 of 13 decisions would have changed) |
| S-w09-explorer-w09-d-2 | followed: w09-c5 (banner not shown to differ); to the user at the close as a guardrail question |
| S-w09-explorer-w09-d-3 | parked: the unit "a PI wake" differs between item 47 and w09-c5; noted in the synthesis, no lever depends on it |
| S-w09-explorer-w09-d-4 | parked: one unrecorded intention in four, a thin base |
| S-w09-explorer-w09-d-5 | followed: the synthesis corrects wave 8's "thinking is empty" (8–20% of PI thinking blocks carry narration) |
| S-w09-explorer-w09-e-1 | followed: PreCompact stays out; the next wave's live compactions replace the replay |
| S-w09-explorer-w09-e-2 | parked: an artefact of resume-based replay, which is not continued |
| S-w09-explorer-w09-e-3 | parked: same; recorded for anyone who replays at size (cold cache, about 5 times a live compaction) |
| S-w09-explorer-w09-e-4 | parked: a cost outlier from launching two cells on one prefix; replays not continued |
| S-w09-explorer-w09-e-5 | followed: the synthesis notes that a verbatim quote survives a post-compaction channel and may not survive the summariser; for the next wave's live check |
| S-w09-explorer-w09-f-1 | followed: w09-c3 (M1 ceiling 4.0–6.4% against the synthesis's 7.5–12%; the synthesis is corrected) |
| S-w09-explorer-w09-f-2 | followed: w09-c3 (M4 three eras; w07-c7's money stays undetermined) |
| S-w09-explorer-w09-f-3 | followed: explorer-w09-g (no lost deliverable in waves 3–9) |
| S-w09-explorer-w09-f-4 | followed: w09-c3 (lean start not visible at the median; exec form is) |
| S-w09-explorer-w09-g-1 | followed: item 15 settled for waves 3–9 in the synthesis |
| S-w09-explorer-w09-g-2 | parked: the headless 10-minute print-mode ceiling is a platform fact, already in item 17's family; no lab run depends on it now |
| S-w09-explorer-w09-g-3 | parked: wave-2 parents; the report check since wave 2 makes the file exist when the hand-back fails |
| S-w09-explorer-w09-g-4 | parked: a double hand-back costs a PI wake, not a deliverable; item 47's family |
| S-w09-explorer-w09-g-5 | parked: a count difference (312 against 306) from the glob, without effect on any claim |
| S-w09-explorer-w09-h-1 | parked: queued hand-backs are missed by `w09d_turns.py`; w09-c5's scope is the 10 located, explorer-w09-h covers the other three |
| S-w09-explorer-w09-h-2 | parked: one truncated read; no decision changed |
| S-w09-explorer-w09-h-3 | followed: the synthesis names w07-c7 as a decision against its own hand-back's limits, not a reading failure |
| S-w09-explorer-w09-h-4 | parked: decisions "in place" predate w08-c11, which now gives them a section |
| S-w09-explorer-w09-h-5 | parked: 156 against 160 in one scope line; the decision carries 160 |
| S-w09-explorer-w09-h-6 | parked: the lever is not built, so whether `additionalContext` reaches the model for queued prompts is not needed |
| S-w09-author-w09-1-1 | followed: w09-c3 (resumed sessions counted once) |
| S-w09-author-w09-1-2 | followed: w09-c3 (first hand-backs) |
| S-w09-author-w09-1-3 | followed: w09-c3 |
| S-w09-author-w09-1-4 | followed: w09-c3 (M5 a rate, raises stated) |
| S-w09-author-w09-1-5 | followed: w09-c3; this wave's start lines (one `name_unconfirmed`, then `named`, budgets right) are the only live after-sample |
| S-w09-author-w09-1-6 | parked: a JST/UTC word slip in an explorer report, corrected in w09-c3 |
| S-w09-author-w09-1-7 | parked: M2's single before-session is stated in w09-c3's scope |
| S-w09-author-w09-1-8 | parked: the tally reads 33 either way |
| S-w09-author-w09-1-9 | followed: w09-c3 |
| S-w09-author-w09-2-1 | followed: w09-c5 (both codings given) |
| S-w09-author-w09-2-2 | followed: w09-c5 drops re-reads |
| S-w09-author-w09-2-3 | followed: explorer-w09-h (14 ESCALATE claims, 13 located) |
| S-w09-author-w09-2-4 | followed: explorer-w09-h |
| S-w09-author-w09-2-5 | parked: one traced carrier is a tool result, not a hand-back; it remains a traced, not invented, result |
| S-w09-author-w09-2-6 | followed: w09-c5 states the banner not shown to differ; the by-role split goes with the guardrail question to the user |
| S-w09-author-w09-2-7 | parked: counts on a growing transcript; w09-c5 states its cut |
| S-w09-author-w09-2-8 | followed: reproducer-w09-2 (the extra wake is an API-error record) |
| S-w09-author-w09-3-1 | followed: w09-c7 (natural base) |
| S-w09-author-w09-3-2 | followed: w09-c7 states the refusal eras |
| S-w09-author-w09-3-3 | followed: w09-c7 states safeguard's run-to-run flip |
| S-w09-author-w09-3-4 | followed: w09-c7 uses raw Clopper-Pearson for safeguard |
| S-w09-author-w09-3-5 | parked: a probe count of the full-rules arm, outside w09-c7 |
| S-w09-author-w09-3-6 | parked: latency tails under load; no judge is accurate enough for latency to decide |
| S-w09-author-w09-3-7 | followed: w09-c7's scope ("allow" means classifier-allow) |
| S-w09-author-w09-3-8 | followed: my arithmetic slip, corrected before w09-c7 was filed (reassessment 00:49) |
| S-w09-reproducer-w09-1-1 | followed: w09-c3 (start concurrency); a paired binary-against-exec run is left, no change depends on it |
| S-w09-reproducer-w09-1-2 | followed: w09-c3 (M1 is the live Desktop figure; the extra 10.7k tokens are live MCP servers) |
| S-w09-reproducer-w09-1-3 | followed: w09-c3 (ESTIMATE, biased both ways) |
| S-w09-reproducer-w09-1-4 | followed: w09-c3 |
| S-w09-reproducer-w09-1-5 | parked: wording in a superseded head |
| S-w09-reproducer-w09-2-1 | followed: w09-c5 |
| S-w09-reproducer-w09-2-2 | followed: w09-c5 (0 of 10) |
| S-w09-reproducer-w09-2-3 | followed: w09-c5 cites the kappa; the synthesis says equal totals hid 15 disagreements |
| S-w09-reproducer-w09-2-4 | followed: w09-c5 (5 of 35) |
| S-w09-reproducer-w09-2-5 | followed: explorer-w09-h (three arrived as queued attachments) |
| S-w09-reproducer-w09-2-6 | followed: the synthesis records it: two errors in opposite directions gave matching totals; agreement per item, not per total, is the check |
| S-w09-reproducer-w09-2-7 | followed: w09-c5 drops re-reads |
| S-w09-reproducer-w09-2-8 | followed: w09-c5 drops re-reads |
| S-w09-reproducer-w09-2-9 | parked: an API-error record read as a wake; noted for anyone cutting PI turns |
| S-w09-reproducer-w09-3-1 | followed: w09-c7 |
| S-w09-reproducer-w09-3-2 | followed: w09-c7 ("neither separates"); explorer-w09-i asks for a score |
| S-w09-reproducer-w09-3-3 | followed: w09-c7 |
| S-w09-reproducer-w09-3-4 | followed: w09-c7 |
| S-w09-reproducer-w09-3-5 | parked: safeguard's run-to-run variation is stated, not sized; matters only if safeguard is pursued |
| S-w09-research-pi-1 | followed: w09-c5 (detector; 0 earlier cases) and the synthesis; a proposal for the PI's agent file goes to the next wave |
| S-w09-research-pi-2 | followed: the next wave: a time in a wave note has failed twice as a rule; a mechanical check is a candidate claim |

## Notes

- **The compaction window did not reach this session.** Context 331,011 tokens at 00:52 with no
  `compact_boundary` record, past the 217k where a 250k window fires; the line has been in this
  worktree's settings file since 23:35. So wave 9 is a clean run without the window, as the user
  decided at 23:45; which of "file not read" and "no live reload" caused it is not separated
  [source: this session's transcript, `usage` of the last main-thread request].
- Names: explorer-w09-a and -b were used by the two probes filed under wave 8's extra work; their
  puzzle files `__scrupuli__/wave-09-explorer-w09-{a,b}.md` are open and this wave disposes of them.
  This wave's agents start at letter c.
- Models: every worker on its agent file's default (Sonnet), except the PI-like headless sessions of
  explorer-w09-e, which run on Opus because the thing measured is a PI's behaviour.

closed: YYYY-MM-DD
