# Wave 6: pre-registered experiments, v1

Written by research-pi on 2026-10-21, after stage 1 of E1 returned (w06-c3, verdict ESCALATE by
reproducer-w06-3) and **after seeing its results**. v0 (`00-experiment_protocol_v0.md`, fc9eff9) is
not edited. Every decision on E1 is reported under both versions.

## What changes, and why

Stage 1's m4 was registered as "the server stopped by its own pid". In that scenario the platform
restarts the server within 71–87 ms and nothing fails, so m4 passed vacuously. The two variants the
author added are the real outages:
- (b) the restart fails: the deny and the 150% block are lost, and the only trace is a transcript
  `hook_non_blocking_error` record, which no lab script reads;
- (c) the restart hangs: 10 s at PostToolUse plus 10 s at PostToolBatch, so 20 s per tool boundary.

**Under v0** the meaningful m4 scenarios fail: (b) leaves no record the lab reads, and (c) exceeds
10 s if "the turn" means the tool boundary, which the author chose only after seeing the debug log.
So the rule says that **stage 2 does not run and the resident server stays out.**

**Under v1** stage 1's m4 failure modes become requirements that stage 2 must meet before anything
lands. The rule is **stricter on landing**, not looser on running:

| Metric | v0 | v1 |
|:--|:--|:--|
| s3 outage | m4 holds for the real build, and the 150% block either holds during an outage or the outage is announced to the worker and the PI | s3a: in scenario (b), a restart that fails, the worker **and** the PI each receive text that says the hooks are down, within the run, and the 150% block holds or is announced as lost. s3b: in scenario (c), a restart that hangs, no tool boundary waits more than 10 s in total, and no boundary waits more than 10 s in total over the whole outage. s3c: scenario (a) shows no lost effect |

s1, s2 and s4 are unchanged. The landing rule is unchanged except for s3, which is now s3a–c.

Stage 2 was dispatched at 19:2x under v0's reading that stage 1 had passed. It continues under v1.
If s3a–c are not all met, nothing lands. The report then says that under v0 stage 2 should not have
run at all.

## Correction (after reproducer-w06-3's verdict on w06-c5)

The paragraph "Under v0" above overstates v0. v0's m4 names "a transcript hook-error record, or text
the model sees". Scenario (b) leaves such a record, so it **meets v0's letter** and fails only its
intent: no lab script reads that record, and the model sees nothing. Scenario (c) fails v0 only if
"the turn" means the tool boundary, which was not registered. Read correctly, **under v0's letter
stage 1 passes and stage 2 runs**. Under its intent, the outage gate fails. v1's s3a–c stand as the
landing requirements either way. This correction changes the reason given, not the decision.
