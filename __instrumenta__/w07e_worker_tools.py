#!/usr/bin/env python3
"""Counts, per murmuration worker type (explorer, author, reproducer, proof-adversary), the tools its subagent transcripts ever called, from ~/.claude/projects/*/*/subagents/agent-*.jsonl and their .meta.json (agentType); splits wave work (project dirs of the Murmuration worktrees, no '---reports' / 'runs' scratch) from probe/headless dirs; output: <out>/worker_tool_calls.tsv (type, class, tool, calls, subagents using it), <out>/worker_subagents.tsv (one row per subagent: type, class, n tool calls, tools used, ToolSearch queries) and a summary on stdout.
Usage: w07e_worker_tools.py <out dir>. Read-only on transcripts; prints no credentials."""
import glob, json, os, sys, collections
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
root = os.path.expanduser("~/.claude/projects")
TYPES = ("explorer", "author", "reproducer", "proof-adversary")
calls = collections.defaultdict(lambda: collections.Counter()); users = collections.defaultdict(lambda: collections.defaultdict(set)); nsub = collections.Counter(); rows = []
for f in glob.glob(os.path.join(root, "*", "*", "subagents", "agent-*.jsonl")):
    mf = f[:-6] + ".meta.json"
    try: at = json.load(open(mf)).get("agentType", "")
    except Exception: continue
    ty = at.split(":")[-1]
    if ty not in TYPES or not at.startswith("murmuration"): continue
    proj = f.split(os.sep)[-4]
    cls = "wave" if ("claude-worktrees-Murmuration" in proj and "---" not in proj and "-runs-" not in proj and "scratch" not in proj) else "probe"
    nsub[(ty, cls)] += 1; used = collections.Counter(); qs = []
    for l in open(f):
        try: r = json.loads(l)
        except ValueError: continue
        if r.get("type") != "assistant": continue
        c = r.get("message", {}).get("content", [])
        if not isinstance(c, list): continue
        for b in c:
            if b.get("type") == "tool_use":
                used[b["name"]] += 1
                if b["name"] == "ToolSearch": qs.append(str(b.get("input", {}).get("query", ""))[:50])
    for k, v in used.items():
        calls[(ty, cls)][k] += v; users[(ty, cls)][k].add(f)
    rows.append((ty, cls, sum(used.values()), ",".join("%s:%d" % kv for kv in used.most_common()), "|".join(qs)))
with open(os.path.join(out, "worker_tool_calls.tsv"), "w") as o:
    o.write("type\tclass\tsubagents_of_type\ttool\tcalls\tsubagents_using\n")
    for k in sorted(calls):
        for tool, n in calls[k].most_common():
            o.write("%s\t%s\t%d\t%s\t%d\t%d\n" % (k[0], k[1], nsub[k], tool, n, len(users[k][tool])))
with open(os.path.join(out, "worker_subagents.tsv"), "w") as o:
    o.write("type\tclass\tn_calls\ttools\ttoolsearch_queries\n")
    for r in rows: o.write("\t".join(str(x) for x in r) + "\n")
print({"%s/%s" % k: v for k, v in sorted(nsub.items())})
