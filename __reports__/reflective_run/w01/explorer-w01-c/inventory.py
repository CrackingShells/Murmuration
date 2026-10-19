#!/usr/bin/env python3
"""t11: MCP servers visible (with tool counts) and servers reported 'failed to connect', per main session.
Source: attachment deferred_tools_delta (addedNames) and the 'failed to connect' block inside mcp_instructions_delta text.
Run: python3 -I inventory.py <dir>"""
import csv, json, os, re, sys, collections
H = os.path.expanduser("~/.claude/projects")
G = H + "/-Users-hacker-Documents-explore-combinatorics-on-binary/"
R = H + "/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/"
S = [("genesis_566fa912", G + "566fa912-7009-421a-9d79-11145e2b8db9.jsonl"), ("design_82e8a947", G + "82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl"),
     ("s3ccc590f", G + "3ccc590f-0187-4f79-b7af-4955944f1374.jsonl"), ("s2947f9dc", G + "2947f9dc-1c3a-452b-97a5-39d4510a1271.jsonl"),
     ("thisrun_ab96c5ed", R + "ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl")]
out = []
for name, p in S:
    tools = collections.defaultdict(set); failed = {}
    for l in open(p, errors="replace"):
        if "failed to connect" in l:
            for m in re.finditer(r"([A-Za-z0-9_.-]+) \(([A-Z_]+)\): \\\"([^\\]*)\\\"", l[l.find("failed to connect"):l.find("failed to connect") + 900].replace("\\n", " ")):
                failed[m.group(1)] = m.group(2) + ": " + m.group(3)
        d = json.loads(l)
        if d.get("type") == "attachment" and d["attachment"].get("type") == "deferred_tools_delta":
            for n in d["attachment"].get("addedNames", []):
                if n.startswith("mcp__"):
                    _, srv, tl = n.split("__", 2); tools[srv].add(tl)
    for s, t in sorted(tools.items()): out.append((name, s, "connected", len(t), ""))
    for s, why in sorted(failed.items()): out.append((name, s, "failed", 0, why))
with open(sys.argv[1] + "/t11_server_inventory.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["session", "server", "state", "n_tools", "failure"]); w.writerows(out)
print(len(out))
