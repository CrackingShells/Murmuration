## S-w04-reproducer-w04-3-1
Every request of every worker, in all arms and cap states, carries a `total_tokens_reminder` attachment ("<total_tokens>14989858 tokens left</total_tokens>"). The "spend-blind" arm C (uncapped) therefore sees a token counter that falls as the context grows; its end value after 150 requests was never compared with a spend. No claim reads this channel, and w02 called it "about 15,000,000 minus the context footprint". Whether a worker can infer its spend from it (uncapped XC read 150 files with zero text about budget, so apparently not) is untested.
refs: /private/tmp/murmuration-w04/author-w04-2/runs/ux-c1 (worker transcript in ~/.claude/projects/*runs-ux-c1-lab/), __reports__/reflective_run/w02/explorer-w02-a/00-findings_v0.md line 29

## S-w04-reproducer-w04-3-2
The hook's n1 is an estimate that sits 3 to 10% below the platform's own sonnet cost at the end of the same run (u-a2 1.10 vs 1.19 B; ux-c1 1.45 vs 1.61; ux-c2 1.83 vs 1.95). The head gives n1 columns on the estimate and "1.6 and 1.9 times B" on platform cost without saying which is which. Threshold 0.9 in the rule is on the estimate; the notes the worker sees are on the estimate too, so the estimate is the right basis for "what the worker was told", but not for "what it spent".
refs: `__instrumenta__/w04c3_verify_n1.py` output, runs/<cell>/meta.json `model_usd`

## S-w04-reproducer-w04-3-3
The rule's clause 1 ("median n1 at least 0.9") is satisfied by any arm that completes a task of 1.1 B, so E2 as pre-registered could return "compliance" for a worker that is as anxious as you like; the head says so, but the protocol itself would return "compliance" for every task at or above 0.9 B that a worker completes. The pre-registered rule for E2b has the same first clause.
refs: __reports__/reflective_run/w04/00-experiment_protocol_v0.md lines 42-65 and 163-172

## S-w04-reproducer-w04-3-4
ux-c1 has one `hook_cancelled` attachment (PostToolUse:Bash, toolu_019PoBcG5eAuEK5rwDpBejny) that ux-c2 and the A cells do not show. Arm C's `handle()` returns None, so what was cancelled is unclear; it did not change the outcome (150 tool calls in both) but the hook's last log line in ux-c1 is a would-be note at 1.4466.
refs: ~/.claude/projects/*runs-ux-c1-lab/*/subagents/agent-*.jsonl, runs/ux-c1/lab/__statera__/harness.jsonl

## S-w04-reproducer-w04-3-5
The head says the platform attachment is in "88 of 88 requests in x-c3"; the transcript has 89 assistant requests and 88 attachments (the first request carries none). Same off-by-one in every capped cell (e2-c: 91 of 92). A harmless count, but a worker's first request lacking the figure is the only request where capped arm C is as blind as uncapped C.
refs: `__instrumenta__/w04c3_verify_runs.py` output (n_req, budget_att)

## S-w04-reproducer-w04-3-6
Exploratory XA uncapped worker ux-a2 stopped at 0.864 of B after only the 75% note (no 87.5% note was shown before the hand-back) with 14% left, naming "USD 0.25 to 0.30" to finish, while in ux-a1 the 87.7% note preceded the stop. Both stops follow a note; which graded note is enough to stop a sonnet explorer is not separated at n = 2.
refs: runs/ux-a2/lab/__statera__/harness.jsonl, runs/ux-a1/lab/__statera__/harness.jsonl
