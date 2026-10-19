#!/usr/bin/env python3
"""Extract every tool call (and its result) from the Claude Code transcripts into one CSV.

Read-only on the transcripts.  Run:  python3 -I extract_calls.py <outdir>
Output: <outdir>/tool_calls.csv  (one row per tool_use, joined to its tool_result)
        <outdir>/agents.csv      (one row per transcript: session, agent id, agentType, model, counts)
Columns of tool_calls.csv are listed in FIELDS.
"""
import csv
import glob
import json
import os
import re
import sys

HOME = os.path.expanduser("~/.claude/projects")
GEN = HOME + "/-Users-hacker-Documents-explore-combinatorics-on-binary"
RUN = HOME + "/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e"
SESSIONS = [
    ("genesis_566fa912", GEN, "566fa912-7009-421a-9d79-11145e2b8db9"),
    ("design_82e8a947", GEN, "82e8a947-1a0c-441c-bc39-df8e2e5fa743"),
    ("s3ccc590f", GEN, "3ccc590f-0187-4f79-b7af-4955944f1374"),
    ("s2947f9dc", GEN, "2947f9dc-1c3a-452b-97a5-39d4510a1271"),
    ("thisrun_ab96c5ed", RUN, "ab96c5ed-ead3-4b36-9671-6076e3914087"),
]
FIELDS = ["session", "agent_key", "agent_type", "agent_desc", "model", "ts", "seq", "tool", "server",
          "tool_use_id", "is_error", "res_len", "input_head", "res_head", "tsq_query"]


def server_of(tool):
    if tool.startswith("mcp__"):
        parts = tool.split("__")
        return parts[1] if len(parts) > 2 else "mcp?"
    return "builtin"


def text_of(content):
    if isinstance(content, str):
        return content
    out = []
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text":
                    out.append(c.get("text", ""))
                elif c.get("type") == "tool_reference":
                    out.append("<tool_reference %s>" % c.get("tool_name", ""))
                else:
                    out.append("<%s>" % c.get("type"))
    return "\n".join(out)


def clip(s, n):
    s = re.sub(r"\s+", " ", s or "")
    return s[:n]


def parse(path, session, agent_key, agent_type, agent_desc, rows, agents):
    uses = {}
    seq = 0
    model = ""
    n_asst = 0
    out_tok = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("type")
            m = d.get("message")
            if not isinstance(m, dict):
                continue
            c = m.get("content")
            if t == "assistant":
                n_asst += 1
                model = m.get("model", model) or model
                u = m.get("usage") or {}
                out_tok += u.get("output_tokens", 0) or 0
                if isinstance(c, list):
                    for b in c:
                        if b.get("type") == "tool_use":
                            seq += 1
                            inp = b.get("input") or {}
                            q = ""
                            if b.get("name") == "ToolSearch":
                                q = inp.get("query", "")
                            uses[b["id"]] = {
                                "session": session, "agent_key": agent_key, "agent_type": agent_type,
                                "agent_desc": agent_desc, "model": model, "ts": d.get("timestamp", ""),
                                "seq": seq, "tool": b.get("name", ""), "server": server_of(b.get("name", "")),
                                "tool_use_id": b["id"], "is_error": "", "res_len": "", "input_head": clip(json.dumps(inp), 300),
                                "res_head": "", "tsq_query": q}
            elif t == "user" and isinstance(c, list):
                for b in c:
                    if b.get("type") == "tool_result" and b.get("tool_use_id") in uses:
                        r = uses[b["tool_use_id"]]
                        txt = text_of(b.get("content"))
                        r["is_error"] = 1 if b.get("is_error") else 0
                        r["res_len"] = len(txt)
                        r["res_head"] = clip(txt, 400)
    rows.extend(uses.values())
    agents.append({"session": session, "agent_key": agent_key, "agent_type": agent_type, "agent_desc": agent_desc,
                   "model": model, "tool_calls": len(uses), "assistant_msgs": n_asst, "out_tokens": out_tok,
                   "path": path})


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    rows, agents = [], []
    for name, base, sid in SESSIONS:
        main_path = "%s/%s.jsonl" % (base, sid)
        if os.path.exists(main_path):
            parse(main_path, name, "main", "main", "", rows, agents)
        for jp in sorted(glob.glob("%s/%s/subagents/agent-*.jsonl" % (base, sid))):
            key = os.path.basename(jp)[len("agent-"):-len(".jsonl")]
            meta = {}
            mp = jp[:-len(".jsonl")] + ".meta.json"
            if os.path.exists(mp):
                meta = json.load(open(mp))
            ty = meta.get("agentType", "?")
            desc = meta.get("name") or meta.get("description", "")
            parse(jp, name, key, ty, desc, rows, agents)
    with open(outdir + "/tool_calls.csv", "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    with open(outdir + "/agents.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(agents[0].keys()))
        w.writeheader()
        w.writerows(agents)
    print(len(rows), "calls;", len(agents), "transcripts")


if __name__ == "__main__":
    main(sys.argv[1])
