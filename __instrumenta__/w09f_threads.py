"""Lists every main-thread and subagent transcript of the lab's worktrees (read only) with start, end, version, model, agent type, name, request count, request-0 token total (input+cache write+cache read of the first request), summed output tokens the character length of the last assistant text and of the last SubagentHandback message; inputs: ~/.claude/projects/*Murmuration* (excluding the scratch probe folders); output: TSV on stdout."""
import json, glob, os, sys
root = os.path.expanduser("~/.claude/projects")
dirs = [d for d in sorted(glob.glob(root + "/*tmp-claude-worktrees-Murmuration-*")) if "---reports" not in d]
dirs += [root + "/-Users-hacker-Documents-src-CrackingShells-Murmuration"]
def scan(path):
    ts0 = ts1 = ver = model = None; hb = 0; req = {}; first = None; last_text = ""; order = []
    for l in open(path, errors="replace"):
        try: r = json.loads(l)
        except Exception: continue
        t = r.get("timestamp")
        if t:
            ts0 = ts0 or t; ts1 = t
        if r.get("version"): ver = ver or r["version"]
        if r.get("type") == "assistant":
            m = r.get("message", {}); u = m.get("usage") or {}
            rid = r.get("requestId") or m.get("id")
            if m.get("model") and m["model"] != "<synthetic>": model = m["model"]
            if rid not in req:
                order.append(rid)
                tot = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
                if first is None and tot > 0: first = tot
            req[rid] = u.get("output_tokens") or 0
            for b in (m.get("content") or []):
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "SubagentHandback": hb = len(str((b.get("input") or {}).get("message", "")))
            txt = "".join(b.get("text", "") for b in (m.get("content") or []) if isinstance(b, dict) and b.get("type") == "text")
            if txt.strip(): last_text = txt
    return ts0, ts1, ver, model, len(req), first, sum(req.values()), len(last_text), hb
print("\t".join("proj kind agent_type name file start end version model reqs req0_tokens out_tokens last_text_chars handback_chars".split()))
for d in dirs:
    proj = os.path.basename(d).replace("-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-", "wt:").replace("-Users-hacker-Documents-src-CrackingShells-Murmuration", "main")
    for f in sorted(glob.glob(d + "/*.jsonl")):
        s = scan(f); print("\t".join(map(str, [proj, "main", "", "", os.path.basename(f)[:8], *s])))
        for a in sorted(glob.glob(f[:-6] + "/subagents/agent-*.jsonl")):
            meta = {}
            try: meta = json.load(open(a[:-6] + ".meta.json"))
            except Exception: pass
            s = scan(a); print("\t".join(map(str, [proj, "sub", meta.get("agentType", ""), meta.get("name", ""), os.path.basename(a)[6:14], *s])))
