## S-w06-reproducer-w06-1-1
The projection's per-tool character counts (`__reports__/wave-05/author-w05-2/desktop_projection_D_e6b.txt`, kept list sums to 63,648) are about 0.6-1.5x too large against what the wire carried, uniformly across kept and removed tools (Artifact 55,375 vs 36,410 in the wave-5 PI's api-request-shape; ScheduleWakeup 8,096 vs 4,778). The claim calls it "not resolved". The projection's tokens band (33k-49k) was nonetheless right. What measure produced the larger counts (pretty-printed JSON, a snapshot field that is not the wire tool)? If the band was derived from those counts, it hit by luck or by a compensating error.
refs: `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-lab-system-optimization-1aa673/6b0e1f2a-b6d1-40f5-840c-f38548cd357e.jsonl` (first api-request-shape), `__instrumenta__/w06c1_rederive_request0.py`

## S-w06-reproducer-w06-1-2
The wave-5 PI (6b0e1f2a) has 3 distinct api-request shape hashes over 148 requests, this session has 1 over 27. What changed in the wave-5 PI's tool list or system prompt mid-session (a deferred tool loaded through ToolSearch, a plugin reload)? If a later shape in a treated session ever adds a denied tool, the claim's "request 0" scope would be hiding it. I did not check the later shapes of 6b0e1f2a, and this session's later requests only by hash.
refs: same wave-5 JSONL, `api-request-shape` records 2 and 3

## S-w06-reproducer-w06-1-3
Denied names are still visible as text in request 0: the Agent tool's description lists "(Tools: All tools except Artifact, ...)" for each agent type, the skill listing names artifact and workflow skills, and the Desktop system prompt has a `<built_in_browser>` paragraph describing `mcp__Claude_Browser__*` while the tools are absent. Does the model then try to call them or tell the user it has them? The transcript of this session after request 0 would show it; I did not read it.
refs: this session's api-request-blob records 34 and 35 (blob 35 holds the agent and skill listings)

## S-w06-reproducer-w06-1-4
The line removes names from the deferred listing too, not only from the loaded tools (209 names here vs 212 in the wave-5 PI: ArtifactComments, ArtifactData, the Simulator `build` tool). The wave-5 w05-c7 claim and the projection track "removed deferred names" as 3; the Desktop run agrees. Nothing odd, but it is a second cut by the same line that nobody has costed in tokens (a few hundred chars).
refs: `deferred_tools_delta` attachments in both transcripts
