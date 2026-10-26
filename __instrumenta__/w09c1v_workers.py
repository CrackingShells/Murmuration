"""Lists every subagent (worker) transcript under the lab's Murmuration worktrees and main project in ~/.claude/projects, to stdout as TSV: project, parent session, agent id, type, name, first timestamp, request-0 tokens (first assistant record with usage), unique requests, first and last SubagentHandback message length; independent of the w09f/w09c1 scripts."""
import json, glob, os
root = os.path.expanduser("~/.claude/projects")
dirs = [d for d in sorted(glob.glob(root + "/*Murmuration*")) if "---reports" not in d and "probes" not in d]
print("\t".join("proj parent agent type name start req0 reqs hb_first hb_last nhb".split()))
for d in dirs:
    for a in sorted(glob.glob(d + "/*/subagents/agent-*.jsonl")):
        meta = {}
        try: meta = json.load(open(a[:-6] + ".meta.json"))
        except Exception: pass
        ts0 = None; first = None; ids = set(); hbs = []
        for l in open(a, errors="replace"):
            try: r = json.loads(l)
            except Exception: continue
            if ts0 is None and r.get("timestamp"): ts0 = r["timestamp"]
            if r.get("type") != "assistant": continue
            m = r.get("message", {}); ids.add(r.get("requestId") or m.get("id"))
            u = m.get("usage") or {}
            t = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
            if first is None and t > 0 and m.get("model") != "<synthetic>": first = t
            for b in m.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                    hbs.append(len(str((b.get("input") or {}).get("message", ""))))
        print("\t".join(map(str, [os.path.basename(d), os.path.basename(os.path.dirname(os.path.dirname(a)))[:8], os.path.basename(a)[6:14], meta.get("agentType", ""), meta.get("name", ""), ts0, first, len(ids), hbs[0] if hbs else "", hbs[-1] if hbs else "", len(hbs)])))
