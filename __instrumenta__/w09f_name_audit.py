"""Audits the worker names that budget.py wrote in `start` records of each worktree's `__statera__/harness.jsonl` against the name in the dispatch's own `.meta.json` (same agent_id, under ~/.claude/projects, read only); inputs: the harness files of the sibling worktrees; output: per file starts, starts with a meta name, mismatches, unconfirmed names, as markdown on stdout."""
import json, glob, os, collections
root = os.path.expanduser("~/.claude/projects"); lab = os.path.abspath(os.path.dirname(__file__) + "/../..") 
meta = {}
for m in glob.glob(root + "/*/*/subagents/agent-*.meta.json"):
    try: meta[os.path.basename(m)[6:-10]] = json.load(open(m)).get("name") or ""
    except Exception: pass
print("| lab folder | starts | with meta name | start name != meta name | name_unconfirmed | of the mismatches, source |"); print("|:--|--:|--:|--:|--:|:--|")
tot = [0, 0, 0]
for f in sorted(glob.glob(lab + "/*/__statera__/harness.jsonl")):
    n = w = bad = un = 0; src = collections.Counter()
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("event") != "start": continue
        n += 1; un += bool(r.get("name_unconfirmed")); real = meta.get(r["agent_id"])
        if real:
            w += 1
            if r.get("name") != real and not r.get("name_unconfirmed"): bad += 1; src[r.get("source")] += 1
    print("| %s | %d | %d | %d | %d | %s |" % (f.split("/")[-3][:34], n, w, bad, un, dict(src)))
