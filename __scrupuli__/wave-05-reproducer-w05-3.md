## S-w05-reproducer-w05-3-1
Headless arm A (no `tools:` line) has no `WebFetch` in its init tools (29 tools) while B has it (21 tools, WebFetch present). Naming a tool in `tools:` adds one that the default set lacks. So the default tool set of a headless PI is not a superset of a named allowlist; the claim notes it, but nobody knows why (entrypoint, plan, or a flag).
refs: /private/tmp/murmuration-w05/reproducer-w05-3/runs/A1/stdout.jsonl and B1/stdout.jsonl (init record, `tools`)

## S-w05-reproducer-w05-3-2
The explorer's "beta" reply does not appear in the Agent tool result; the result says the report "was delivered as a message". A check that greps the Agent tool_result for "beta" finds nothing; only the sub-transcript or the stream shows it. In both arms the explorer is first blocked by the SubagentHandback harness hook (it wants a findings report although the brief says "Write no file") and hands back on the second try. A smoke task that always costs the worker one hook round is not neutral, though it is identical in A and B.
refs: ~/.claude/projects/-private-tmp-murmuration-w05-reproducer-w05-3-runs-B1-lab/*/subagents/agent-a47fe7781b3ae4459.jsonl

## S-w05-reproducer-w05-3-3
The measured B is e0fc3ab plus one line, but the branch tip tree (baba44f) has other hooks and scripts. The claim says B "stays on the branch tip"; no run uses that tree. Hooks add text to request 0 on some events, so the margin of about 500 tokens could move.
refs: `git diff e0fc3ab baba44f --stat -- hooks scripts`

## S-w05-reproducer-w05-3-4
Request 0 of arm B is 15,013 against a threshold gap of 15,000: 497 tokens of slack in the registered rule, and the three pair differences differ by 2 tokens. The rule's constant (15,000) was registered before the measurement of schema sizes, yet the list was written after the pilot. The rule then decides little: it passes by construction once the list is cut by schema size. Is a margin of that kind a result or a tuning?
refs: __reports__/wave-05/author-w05-2/e6_table_A_B.tsv
