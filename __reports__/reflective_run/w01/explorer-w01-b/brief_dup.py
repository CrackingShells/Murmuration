#!/usr/bin/env python3
"""explorer-w01-b: how much of each explorer brief of this run restates text the agent already holds
(its agent file, the preloaded skill, the files the brief names).  6-word shingles, case-insensitive.
Run: python3 -I brief_dup.py   (reads the six briefs from this run's main transcript)"""
import json, re, csv, sys
R = "/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/"
T = "/Users/hacker/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl"
def sh(t, n=6):
    w = re.findall(r"\w+", t.lower()); return set(tuple(w[i:i+n]) for i in range(max(0, len(w)-n+1)))
src = {
  "agent_file(explorer.md)": open(R+"agents/explorer.md").read(),
  "preloaded_skill(SKILL.md)": open(R+"skills/research-loop/SKILL.md").read(),
  "framing.md": open(R+"__design__/framing.md").read(),
  "wave-01.md": open(R+"__statera__/wave-01.md").read(),
  "briefs.md": open(R+"skills/research-loop/references/briefs.md").read(),
}
briefs = {}
for l in open(T):
    d = json.loads(l); m = d.get("message", {})
    if isinstance(m, dict) and isinstance(m.get("content"), list):
        for b in m["content"]:
            if b.get("type") == "tool_use" and b["name"] == "Agent":
                briefs[b["input"]["name"]] = b["input"]["prompt"]
rows = []
for n, t in sorted(briefs.items()):
    s = sh(t)
    r = {"brief": n, "chars": len(t)}
    allsrc = set()
    for k, v in src.items():
        x = sh(v); allsrc |= x
        r[k] = round(len(s & x)/len(s), 3)
    r["any_of_above"] = round(len(s & allsrc)/len(s), 3)
    others = set()
    for m_, t2 in briefs.items():
        if m_ != n: others |= sh(t2)
    r["other_five_briefs"] = round(len(s & others)/len(s), 3)
    rows.append(r)
w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
