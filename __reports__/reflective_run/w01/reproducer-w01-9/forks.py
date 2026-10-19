import json, glob, collections
D = "/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/"
THIS = "/Users/hacker/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl"
where = collections.defaultdict(set); text = collections.defaultdict(set)
for f in sorted(glob.glob(D + "*.jsonl")) + [THIS]:
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("type") == "user" and (r.get("isMeta") or r.get("origin") is None) and not r.get("isSidechain") and "toolUseResult" not in r:
            c = r["message"]["content"]
            if isinstance(c, list) and any(b.get("type") == "tool_result" for b in c if isinstance(b, dict)): continue
            t = c if isinstance(c, str) else "\n".join(b.get("text", "") for b in c if isinstance(b, dict))
            if t.startswith("[Request interrupted"): continue
            where[r["uuid"]].add(f[-14:-6]); text[t].add(r["uuid"])
print("non-typed candidates (origin None, incl isMeta):", len(where), "uuids in >1 file:", sum(len(v) > 1 for v in where.values()))
print("distinct texts:", len(text), " texts with >1 uuid:", sum(len(v) > 1 for v in text.values()))
for t, u in text.items():
    if len(u) > 1: print("  dup text", len(u), repr(t[:60]))
print("--- restricted to author's 14 candidates (reminder-led null-origin or turnOrigin scheduled)")
sel = {}
for f in sorted(glob.glob(D + "*.jsonl")) + [THIS]:
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("type") == "user" and r.get("origin") is None and not r.get("isSidechain") and "toolUseResult" not in r:
            c = r["message"]["content"]
            if isinstance(c, list) and any(b.get("type") == "tool_result" for b in c if isinstance(b, dict)): continue
            t = c if isinstance(c, str) else "\n".join(b.get("text", "") for b in c if isinstance(b, dict))
            if r.get("turnOrigin") == "scheduled" or (t.startswith("<system-reminder>") and r.get("turnOrigin") in (None, "sdk")):
                sel.setdefault(r["uuid"], set()).add((f[-14:-6], r.get("turnOrigin"), r.get("isMeta"), t[:40].replace("\n", " ")))
print(len(sel), "distinct uuids;", sum(len(v) > 1 for v in sel.values()), "in more than one file")
for u, v in sel.items(): print(u[:8], sorted(v)[0], "files:", len({x[0] for x in v}))
