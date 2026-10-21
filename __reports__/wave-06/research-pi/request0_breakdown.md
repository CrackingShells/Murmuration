# What fills the first request, PI and workers (wave 6, after the close)

MEASURED from this session's transcript (`74fa512e…`, Claude Code 2.1.304, Desktop) and its
subagent transcripts, read-only. Characters, not tokens. Earlier fits give 0.21–0.34 tokens per
character (w05-c3), so token figures here would be ESTIMATEs.

PI (`murmuration:research-pi`), request 0 = 46,738 tokens:

| Part | Characters |
|:--|--:|
| tool schemas (23 loaded) | 41,937 |
| skills listing (90 installed skills) | 30,072 |
| system prompt (Claude Code + research-pi body + Desktop text) | 28,326 |
| deferred tool names (105) | 9,020 |
| agent-type listing | 7,657 |
| user instructions, worktree and session-start reminders (first user message) | 7,826 |
| SessionStart hook context (tool routing and search policy) | about 2,100 |
| environment, connecting servers, MCP instructions, auto mode | about 4,200 |

Workers: 17 subagents, request 0 = 13,928–14,784 tokens, 8 loaded tools each, no skills listing.
The `tools:` allowlists already do for workers what the denylist does for the PI.

Lead for wave 7: the PI needs one skill (`research-loop`) out of the 90 listed. Whether denying
`Skill`, or `Skill(...)` rules, removes the listing while keeping that skill is untested.
