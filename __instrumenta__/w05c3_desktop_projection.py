#!/usr/bin/env python3
"""ESTIMATE of what a `tools:` line would remove from a Desktop PI's request-0 context: reads the prompt_snapshot tool schemas and the deferred_tools_delta names of one Desktop PI transcript (.jsonl), applies the `tools:` (allowlist) or `disallowedTools:` (denylist) line of an agent file by name and by `server__*` wildcard, prints characters kept/removed (loaded schemas, deferred names) and the token range chars x [0.211, 0.342]; inputs: <transcript> <agent file> ; output: stdout.
0.211 = tokens per character of tool schemas measured in w05-c3 (headless A minus B, 15,5xx tokens over 73.5k characters); 0.342 = explorer-w05-b's all-category fit. Nothing is run on the Desktop: the result presumes the app filters its MCP tools by `tools:` like the CLI does."""
import fnmatch, json, re, sys
tr, agent = sys.argv[1], sys.argv[2]
lines = [l for l in open(agent) if l.startswith("tools:") or l.startswith("disallowedTools:")]
deny = lines[0].startswith("disallowedTools:"); pats = [p.strip() for p in lines[0].split(":", 1)[1].split(",") if p.strip()]
keep = (lambda n: not any(fnmatch.fnmatchcase(n, p) for p in pats)) if deny else (lambda n: any(fnmatch.fnmatchcase(n, p) for p in pats))
snap = None; deferred = []
for l in open(tr):
    r = json.loads(l)
    if r.get("type") != "attachment":
        continue
    a = r["attachment"]
    if a.get("type") == "prompt_snapshot" and "tools" in a and snap is None:
        snap = a["tools"]
    if a.get("type") == "deferred_tools_delta" and snap is None:
        deferred += a.get("addedNames", [])
    if snap is not None:
        break
tot = sum(len(json.dumps(t)) for t in snap); kept = [t for t in snap if keep(t["name"])]; ck = sum(len(json.dumps(t)) for t in kept)
dk = [n for n in deferred if keep(n)]
print("loaded tools: %d, %d chars; kept by the line: %d tools, %d chars; removed %d chars" % (len(snap), tot, len(kept), ck, tot - ck))
print("deferred names: %d, %d chars; kept %d names, %d chars; removed %d chars" % (len(deferred), sum(len(n) + 1 for n in deferred), len(dk), sum(len(n) + 1 for n in dk), sum(len(n) + 1 for n in deferred) - sum(len(n) + 1 for n in dk)))
rem = tot - ck
print("removed schema tokens: %d to %d" % (rem * 0.211, rem * 0.342))
print("kept loaded tools:", sorted((t["name"], len(json.dumps(t))) for t in kept))
print("removed loaded tools (largest 12):", sorted(((t["name"], len(json.dumps(t))) for t in snap if not keep(t["name"])), key=lambda x: -x[1])[:12])
print("removed deferred names, by prefix:", {k: sum(1 for n in deferred if not keep(n) and (n.split("__")[1] if n.startswith("mcp__") else "(built-in)") == k) for k in sorted({(n.split("__")[1] if n.startswith("mcp__") else "(built-in)") for n in deferred if not keep(n)})})
