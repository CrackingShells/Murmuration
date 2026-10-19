#!/usr/bin/env python3
"""t10: per agent, calls by tool family (Bash-python, Wolfram, colgrep, arxiv, ddg, web builtins, ToolSearch, total).  python3 -I per_agent_mcp.py <dir>"""
import csv, collections, re, sys
D = sys.argv[1]
rows = list(csv.DictReader(open(D + "/calls_dedup_classified.csv")))
fam = collections.defaultdict(collections.Counter)
for r in rows:
    k = (r["group"], r["agent_key"][:8], r["agent_desc"][:38])
    t = r["tool"]
    if t == "Bash":
        f = "bash_python" if re.search(r"python3?\b", r["input_head"]) else "bash_other"
    elif r["server"] == "WolframToolkit": f = "wolfram"
    elif r["server"].startswith("plugin_colgrep"): f = "colgrep"
    elif r["server"] == "arxiv": f = "arxiv"
    elif r["server"] == "ddg": f = "ddg"
    elif r["server"] == "context7": f = "context7"
    elif t in ("WebFetch", "WebSearch"): f = "web_builtin"
    elif t == "ToolSearch": f = "ToolSearch"
    elif t in ("Read", "Write", "Edit"): f = "file_tools"
    else: f = "other"
    fam[k][f] += 1
cols = ["bash_python", "bash_other", "file_tools", "wolfram", "colgrep", "arxiv", "ddg", "context7", "web_builtin", "ToolSearch", "other"]
with open(D + "/t10_per_agent_tool_families.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["group", "agent", "desc"] + cols + ["total"])
    for k, c in sorted(fam.items()):
        w.writerow(list(k) + [c[x] for x in cols] + [sum(c.values())])
