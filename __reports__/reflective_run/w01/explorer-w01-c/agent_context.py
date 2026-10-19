#!/usr/bin/env python3
"""Per transcript: how many deferred tool names the agent was told about, their characters, MCP-server count,
and the first assistant turn's input tokens (input + cache_creation + cache_read).  Writes agent_context.csv.
Run: python3 -I agent_context.py <outdir>   (read-only on transcripts)"""
import csv, glob, json, os, sys
HOME = os.path.expanduser("~/.claude/projects")
GEN = HOME + "/-Users-hacker-Documents-explore-combinatorics-on-binary"
RUN = HOME + "/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e"
SESS = [("genesis_566fa912", GEN, "566fa912-7009-421a-9d79-11145e2b8db9"),
        ("design_82e8a947", GEN, "82e8a947-1a0c-441c-bc39-df8e2e5fa743"),
        ("s3ccc590f", GEN, "3ccc590f-0187-4f79-b7af-4955944f1374"),
        ("s2947f9dc", GEN, "2947f9dc-1c3a-452b-97a5-39d4510a1271"),
        ("thisrun_ab96c5ed", RUN, "ab96c5ed-ead3-4b36-9671-6076e3914087")]
rows = []
seen_keys = set()
def one(path, session, key, atype, desc):
    names = set(); first = None; mcp_instr_chars = 0
    for l in open(path, encoding="utf-8", errors="replace"):
        d = json.loads(l)
        if d.get("type") == "attachment":
            a = d["attachment"]
            if a["type"] == "deferred_tools_delta":
                names |= set(a.get("addedNames", [])) 
                names -= set(a.get("removedNames", []))
            if a["type"] == "mcp_instructions_delta":
                mcp_instr_chars += sum(len(b) for b in a.get("addedBlocks", []))
        if d.get("type") == "assistant" and first is None:
            u = (d.get("message") or {}).get("usage") or {}
            first = (u.get("input_tokens", 0) or 0) + (u.get("cache_creation_input_tokens", 0) or 0) + (u.get("cache_read_input_tokens", 0) or 0)
    servers = {n.split("__")[1] for n in names if n.startswith("mcp__")}
    rows.append(dict(session=session, agent_key=key, agent_type=atype, agent_desc=desc, deferred_names=len(names),
                     deferred_chars=sum(len(n) + 1 for n in names), mcp_servers=len(servers), mcp_instr_chars=mcp_instr_chars,
                     first_turn_input_tokens=first, path=path))
for name, base, sid in SESS:
    mp = "%s/%s.jsonl" % (base, sid)
    one(mp, name, "main", "main", "")
    for jp in sorted(glob.glob("%s/%s/subagents/agent-*.jsonl" % (base, sid))):
        k = os.path.basename(jp)[6:-6]
        if k in seen_keys:
            continue
        seen_keys.add(k)
        meta = {}
        m = jp[:-6] + ".meta.json"
        if os.path.exists(m): meta = json.load(open(m))
        one(jp, name, k, meta.get("agentType", "?"), meta.get("name") or meta.get("description", ""))
w = csv.DictWriter(open(sys.argv[1] + "/agent_context.csv", "w", newline=""), list(rows[0].keys()))
w.writeheader(); w.writerows(rows)
print(len(rows))
