#!/usr/bin/env python3
"""For each murmuration worker subagent transcript (wave class as in w07e_worker_tools.py) prints request 0: version, usage total, loaded tool names (api-request-shape), tools JSON chars, and the deferred-name list chars/count per MCP server from the first deferred_tools_delta attachment; input: ~/.claude/projects/*/*/subagents/agent-*.jsonl; output: TSV on stdout (type, version, req0, n_loaded, tools_chars, loaded names, deferred counts per server, deferred chars).
Usage: w07e_worker_req0.py [max rows per type]. Read-only; no credentials printed."""
import glob, json, os, sys, collections, re
root = os.path.expanduser("~/.claude/projects"); lim = int(sys.argv[1]) if len(sys.argv) > 1 else 3; seen = collections.Counter()
print("type\tversion\treq0\tn_loaded\ttools_chars\tloaded\tdeferred_by_server\tdeferred_chars\tfile")
for f in sorted(glob.glob(os.path.join(root, "*", "*", "subagents", "agent-*.jsonl")), key=os.path.getmtime, reverse=True):
    proj = f.split(os.sep)[-4]
    if not ("claude-worktrees-Murmuration" in proj and "---" not in proj and "-runs-" not in proj and "scratch" not in proj): continue
    try: at = json.load(open(f[:-6] + ".meta.json")).get("agentType", "")
    except Exception: continue
    ty = at.split(":")[-1]
    if not at.startswith("murmuration") or seen[ty] >= lim: continue
    shape = None; first = None; dnames = []; dchars = 0
    for l in open(f):
        try: r = json.loads(l)
        except ValueError: continue
        if r.get("type") == "api-request-shape" and shape is None: shape = r
        if r.get("type") == "assistant" and first is None: first = r
        if r.get("type") == "attachment" and r["attachment"].get("type") == "deferred_tools_delta" and not dnames:
            dnames = r["attachment"].get("addedNames", []); dchars = sum(len(x) + 1 for x in dnames)
        if first is not None and shape is not None and dnames: break
    if not first or not shape: continue
    seen[ty] += 1
    u = first["message"]["usage"]; tot = u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"]
    tools = shape["shape"].get("tools", [])
    srv = collections.Counter((re.match(r"mcp__(.+?)__", n).group(1) if n.startswith("mcp__") else "builtin") for n in dnames)
    print("\t".join(str(x) for x in (ty, shape.get("version"), tot, len(tools), len(json.dumps(tools)), ",".join(t["name"] for t in tools), dict(srv), dchars, os.path.basename(f))))
