## S-w02-reproducer-w02-10-1
The B3 author read a platform `budget_usd` attachment that shows the whole session's spend (used 1.0432 of 15) and reported it as its own ("about USD 1.0 against the USD 0.40"). Every worker in a budgeted session gets such records (6 of 7 subagent transcripts show 2 to 6 of them, rising with the shared total), yet only 1 of 7 hand-backs reported spend. What made that one worker report it, and would a brief that says "Budget: USD 0.40" without a reported-spend line make it rarer? The author could not say whether the worker knew the figure was session-wide.
refs: B3 `.../subagents/agent-a2b354341eefe6892.jsonl` (`budget_usd` attachments), `lab/__statera__/handbacks/wave-01-author-w01-1.md` line 29, `__reports__/reflective_run/w02/author-w02-4/b3_budget_attachments_out.txt`

## S-w02-reproducer-w02-10-2
The budget the worker is told in its brief (USD 0.40) and the counter it is shown (of 15) differ in scale and scope, and the harness's per-worker `used` is not shown to the worker at all. If the spend a worker sees cannot be compared with the budget it is given, the 80% note ("noted": false in all seven end lines) is the only per-worker signal. Is that intended?
refs: B3 `lab/__statera__/harness.jsonl` (`noted`), author-w01-1 transcript start-of-run budget hook text

## S-w02-reproducer-w02-10-3
The B3 PI's `synthesis.md` line 63 repeats "The author reported spending about USD 1.0" next to its own session figure "about USD 2.2 of USD 15" (cost-state says 2.347). Where did the PI's 2.2 come from (its own last `budget_usd` record read 2.2777), and is that figure a source by the rule the claim proposes?
refs: B3 `lab/__statera__/synthesis.md` lines 60-63; main transcript last `budget_usd` record 2.2777 at 07:16:52Z
