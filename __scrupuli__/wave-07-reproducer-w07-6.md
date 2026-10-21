## S-w07-reproducer-w07-6-1
My first four sessions (A4, AR, B4, BR) ran with an empty `agents/author.md` in the export (a bug of mine: `open(p,"w")` evaluated before `read`). Claude Code did not fail: `murmuration:author` dispatched a generic agent with 12 tools, 33k context. No warning appeared in the .err files. A malformed or empty plugin agent file is silently accepted, which matters for any later edit of `agents/author.md`.
refs: /private/tmp/murmuration-w07/reproducer-w07-6/invalid_empty_agent/

## S-w07-reproducer-w07-6-2
In the invalid pair, AR request 2 read 19,874 tokens after 338 s although its own earlier entry had expired, and A4 request 2 (same time, 333 s) read 0. AR read the entry A4 had re-written seconds earlier: two concurrent sessions of the same arm share a prefix beyond the system prompt. That shows the concurrency effect the author suspected is real, but it also shows the prefix shared reaches 20k tokens, so the 5,202 in the valid A4 is not the whole shared prefix. What writes a 5,202-token entry that survives 333 s in an A session? Not isolated (cold-hour A run missing).
refs: invalid_empty_agent/runs/, c1c3_recheck.md; valid A4 in ~/.claude/projects/-private-tmp-murmuration-w07-reproducer-w07-6-work-A4 (first agent file)

## S-w07-reproducer-w07-6-3
Wave-4 `model_s`, `gap_prev_s`, `wait_s` are blank in `explorer-w07-b/requests.tsv` for all 405 author rows, so five of the 14 held and both "short" re-writes of c4 rest on tool_s only. Which parser version produced wave 4, and can it be rerun?
refs: __reports__/wave-07/explorer-w07-b/requests.tsv; __instrumenta__/w07c7r_c4_sensitivity.py output

## S-w07-reproducer-w07-6-4
The resumed B author in BC read 100% across 339 s, but the A resume is untested; whether a resumed author is billed at the 5m rate in A is inferred, not measured. Also my BC main thread noted the author warned "330 s wait exceeds the 4.5 minute limit in its instructions" and still obeyed: the agent file's own wait rule did not stop the wait.
refs: /private/tmp/murmuration-w07/reproducer-w07-6/runs/BC.json; ~/.claude/projects/-private-tmp-murmuration-w07-reproducer-w07-6-work-BC (agent-af6c02fc2ffe9af3a.jsonl, requests 5-7)
