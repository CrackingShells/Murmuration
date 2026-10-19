## symbols

| Symbol | Meaning |
|:--|:--|
| B, T | a worker's limits in force: USD and active minutes. B and T start as the brief's `Budget:` and `Time:` lines (else the role defaults) and change only by a raise |
| frac, t_frac, deciding fraction | `used / B`, `active minutes / T`, and the larger of the two (the log's `frac`, `t_frac`, `which`) |
| check | one PostToolBatch event of a worker: at most one note per check |
| note | the `additionalContext` of a check: `Spent X of USD Y (Z%); t of T min (W%)`, plus one sentence from frac 1.0 |
| ceiling | frac 1.5: a PostToolUse `decision: block` (the log's `stop`); `halt` is `continue: false` after 3 blocks |
| raise | a PI message with `Budget: USD x` or `Time: min t`: B becomes max(B, spend at the message) + x, T likewise with active minutes |
| active time | minutes between SubagentStart and SubagentStop of each run, summed (the idle gap between runs is out) |
| floor | no brief under USD 0.30 or 3 minutes; a lower figure is logged as `warn`, not raised |

## S-w03-author-w03-1-1
`decision: block` on PostToolBatch is not feedback to the model; it ends the worker. The worker made no further call, there was no hand-back and no SubagentStop event followed (4 of 4 cells, 1 foreground and 3 background; the transcript has a `hook_stopped_continuation` attachment with the reason as its message). The same `decision: block` on PostToolUse gives the reason to the worker as a `hook_blocking_error` and the worker hands back (2 of 2). The two events share the schema's field name and differ in what it does. So the ceiling block has to stay on PostToolUse even though the notes moved to PostToolBatch.
refs: __reports__/reflective_run/w03/author-w03-1/derived/probe_analysis.txt (rows p5 p6 p12 p13 against p16 p17); raw /tmp/author-w03-1/runs/p12/events.jsonl and the worker transcript under ~/.claude/projects/*-runs-p12-lab/

## S-w03-author-w03-1-2
Surprise about when PostToolBatch does and does not fire. I found no case where it did not: 109 of 109 batches, with the batch of a failed call (12 cells), of a call refused by a PreToolUse hook (p14), of a Bash call started with `run_in_background` (p18, the batch ends at the launch, not at the end of the job), of a parallel batch with one 6 s call (the event comes after the slowest call), and of the final `SubagentHandback` (before SubagentStop). PostToolUse is the one that misses: it does not fire for failed or denied calls (13 of 172 calls) and fires once per call in a parallel batch (5 duplicates in 3 batches of p7). The first budget hook (w02-c5) was on PostToolUse, so it never checked after a failed call and could send one note per call of a parallel batch (it was guarded by a once-per-agent flag, so the second did not show). I could not reproduce the user's warning ("not triggered exactly when one wanted"). Candidates for what the other project saw, none tested here: it fires only after all calls of a batch return (late when one call is long); a turn that ends with no tool call has no batch, so a hook there never runs; and `decision: block` stops the run, which looks like "triggered at the wrong moment" if one expected feedback.
refs: __reports__/reflective_run/w03/author-w03-1/derived/probe_summary.tsv; /tmp/author-w03-1/runs/p18/events.jsonl, p14/events.jsonl, p7/events.jsonl

## S-w03-author-w03-1-3
SubagentStart cannot carry the budgets the brief sets: the event has no prompt, and the new worker's transcript does not exist yet (3 of 3). The first hook said "unless your brief has a line" instead of the figures. I added a PreToolUse hook on `Agent` that stores the brief's lines for the next SubagentStart of the same type; with two parallel dispatches of one type and different figures it cannot know which is which and says so. A resume's SubagentStart fires and its `additionalContext` is not delivered (1 of 1 run that still sent one; the final hook sends none). Both are platform facts I measured only on 2.1.302.
refs: /tmp/author-w03-1/runs/p16/events.jsonl (`tx.exists: false`), /tmp/author-w03-1/runs/q1 (the first q1: SubagentStart `hook_success` twice, `hook_additional_context` once), scripts/budget.py (`dispatch`, `claim_pending`)

## S-w03-author-w03-1-4
The haiku parent does not do what the brief says about foreground and background: asked for foreground it backgrounded the worker in 3 of 13 cells (p5, p13, p16), and in p8 it did the worker's seven rounds itself before dispatching. The worker's own behaviour was the same in both modes, but "foreground" in this report is what the platform did (the Agent call returned after SubagentStart), not what I asked for. In headless runs the foreground and background rows are therefore not controlled.
refs: __reports__/reflective_run/w03/author-w03-1/probe_analyze.py (`actual_fg`), /tmp/author-w03-1/runs/p8/events.jsonl (main thread events with the worker's tool calls)

## S-w03-author-w03-1-5
The report check pushes every explorer past 100% after it has decided to hand back. In e2, e3, e5, e6 and the quick-run q1 the worker called SubagentHandback at 85 to 100%, the report check (handback.py, once) refused it, and the report write and the second hand-back cost 1 to 2 more requests: the notes with the sentence (103 to 138%) arrived while the worker was writing a report it had been told it must write. The spend between the first hand-back call and the end of the run is USD 0.085 in e2 and 0.080 in e3 (B = 0.30, about 27% of B), 0.081 in e6 (B = 0.24); part of it is the report the explorer has to write anyway. In e1 the worker wrote the report right after the 88% note, before its hand-back, and got no refusal. So whether a run passes 100% depends on whether the explorer writes its report before the hand-back. A line in the explorer's contract ("write the report before you hand back") is the cheap fix; I did not test one.
refs: derived/harness_e2.jsonl, harness_e3.jsonl, harness_e6.jsonl (a `deny` line between the 89 to 95% note and the first note above 100%), derived/e2e_timeline_e1.jsonl (no deny)

## S-w03-author-w03-1-6
At small budgets one request is more than a threshold step. e1: 0.878 at request 85 and 0.996 at request 86 (one request cost USD 0.035, about ten normal ones; probably a cache write once the 5-minute cache lifetime had passed, not checked); e6: 0.95 then 1.114 at the hand-back. The schedule 50, 75, 87.5, 93.75 can send one note for several thresholds, as designed, but cannot warn before a single request that crosses 100% from 0.88. The floor of USD 0.30 holds about 8 requests of that size, not 10: the 0.03 to 0.04 of w02-c8 was the first request, and later requests cost about 0.0035 each except those with a long output or a cache write. I did not measure the distribution of request costs over a run.
refs: derived/harness_e1.jsonl (`requests` 85 and 86), derived/harness_e6.jsonl

## S-w03-author-w03-1-7
A plain resume restores nothing: spend and active time are cumulative, which replaces the first hook's baseline restart. In the research-loop protocol a verifier's message resumes an author, and only a message from the PI raises a budget (a peer's message has `origin.kind` "peer" and is ignored by the raise). An author that finished at 1.0 or more and is then questioned by a verifier gets a note at every check from 1.0, and a ceiling block from 1.5; after 3 blocks the backstop `continue: false` ends it. A Q&A answer is 1 to 3 calls, so I expect it to be fine, but I did not run the author-verifier exchange with the hook on. Related, n = 1 (x1): a peer's SendMessage to a worker that had already stopped did not resume it (no SubagentStart, no record); the same peer message to a running worker arrived as `queued_command` (x2). So in a headless run a verifier may not be able to wake a stopped author at all; I do not know whether that is the platform or my prompt.
refs: /tmp/author-w03-1/runs/x1 and x2 (events.jsonl; transcripts under ~/.claude/projects/*-runs-x1-lab/ and *-runs-x2-lab/), scripts/budget.py (`scan`, the `origin` check)

## S-w03-author-w03-1-8
What the workers did at the notes was not what the start note's contract says. The note says "from 100% you choose"; 4 of 7 runs (e1 in both runs, e2, e6, e7) handed back on their own after a note of 75 to 99%, and e7's worker reported "about 3 min" used at 2.3 of 3 by the hook's clock (the worker's own clock was off). The worker in e2, told by its brief not to hand back before f200, handed back at 89% and wrote "no message authorised going over the budget". I cannot tell compliance from anxiety, and no run without notes at these budgets exists to compare (w02-c5's no-note runs were at USD 0.06). Whether handing back at 89% is the wanted behaviour or an early stop is the PI's call.
refs: derived/e2e_timeline_e1.jsonl, e2e_timeline_e2.jsonl, e2e_timeline_e6.jsonl, e2e_timeline_e7.jsonl

## S-w03-author-w03-1-9
Workers made parallel calls although the brief said "one call at a time": f077 and f078 in e1, f011 and f012 in e3, f009 and f010 in e5 (all admitted in their hand-backs). That is a free test of the one-note-per-check rule, which held (one `note` line per check in every log), and it is another reason a per-call hook (PostToolUse) would have sent twice. It also means a worker told to do one call at a time cannot be relied on to produce single-call batches.
refs: derived/e2e_timeline_e1.jsonl (hand-back text), derived/harness_e1.jsonl

## S-w03-author-w03-1-10
Minor, pre-existing: `claude plugin validate .` passes but prints a warning that the README has no marketplace install line. Not touched. Also: `git revert --no-commit` left the index staged; I unstaged it (`git reset -q`), so the working tree holds everything uncommitted for the PI.
refs: `claude plugin validate .`
