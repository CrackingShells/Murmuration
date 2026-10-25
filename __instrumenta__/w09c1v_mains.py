"""Lists every top-level session transcript (no subagents) of the lab's Murmuration worktrees and main project, from ~/.claude/projects, to stdout: project, session id, first timestamp, version, requests (unique requestId), request-0 tokens (input+cache write+cache read of the first assistant record), shared request ids with earlier sessions of the same folder; independent of the w09f/w09c1 scripts."""
import json, glob, os, sys
root = os.path.expanduser("~/.claude/projects")
dirs = [d for d in sorted(glob.glob(root + "/*Murmuration*")) if "---reports" not in d and "probes" not in d]
rows = []
for d in dirs:
    for f in glob.glob(d + "/*.jsonl"):
        first = None; ts0 = None; ver = None; ids = []
        for l in open(f, errors="replace"):
            try: r = json.loads(l)
            except Exception: continue
            if ts0 is None and r.get("timestamp"): ts0 = r["timestamp"]
            if ver is None and r.get("version"): ver = r["version"]
            if r.get("type") == "assistant":
                m = r.get("message", {}); rid = r.get("requestId") or m.get("id")
                if rid and rid not in ids: ids.append(rid)
                u = m.get("usage") or {}
                t = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
                if first is None and t > 0 and m.get("model") != "<synthetic>": first = t
        rows.append((os.path.basename(d)[-40:], os.path.basename(f)[:8], ts0, ver, ids, first))
rows.sort(key=lambda x: x[2] or "")
seen = {}
for p, s, ts, v, ids, first in rows:
    shared = sum(1 for i in ids if i in seen)
    for i in ids: seen.setdefault(i, s)
    if len(ids) >= 20:
        print(p, s, ts, v, len(ids), first, "shared", shared)
