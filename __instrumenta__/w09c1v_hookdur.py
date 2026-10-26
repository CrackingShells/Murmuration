"""Lists, from every transcript (main and subagent) of the lab's worktrees in ~/.claude/projects, the hook_success attachments of SubagentStart and PostToolBatch hooks that ran the plugin's budget hook: dedup by record uuid, grouped by (event, command string with paths shortened), count/median/min/max of durationMs and first/last timestamp, to stdout; independent of w09f/w09c1 scripts."""
import json, glob, os, collections, statistics as st, re
root = os.path.expanduser("~/.claude/projects")
LAB = ("8cff9e", "928ebd", "bc67fb", "34edd8", "1aa673", "3417be", "a25ae6")
dirs = [d for d in glob.glob(root + "/*") if d.endswith(LAB) and "---reports" not in d]
seen = set(); dup = 0; g = collections.defaultdict(list)
for d in dirs:
    for f in glob.glob(d + "/*.jsonl") + glob.glob(d + "/*/subagents/agent-*.jsonl"):
        for l in open(f, errors="replace"):
            if '"hook_success"' not in l: continue
            try: r = json.loads(l)
            except Exception: continue
            a = r.get("attachment") or {}
            if a.get("type") != "hook_success" or a.get("hookEvent") not in ("SubagentStart", "PostToolBatch"): continue
            u = r.get("uuid")
            if u in seen: dup += 1; continue
            seen.add(u)
            c = re.sub(r"/Users/hacker/\S*?(?=scripts/|bin/)", "<R>/", a.get("command", ""))
            g[(a["hookEvent"], c[:110])].append((a.get("durationMs"), r["timestamp"]))
print("duplicates by uuid:", dup)
for (e, c), v in sorted(g.items()):
    ds = [x[0] for x in v if x[0] is not None]
    print(e, "|", c, "| n", len(v), "median", st.median(ds), "min", min(ds), "max", max(ds), min(x[1] for x in v)[:16], max(x[1] for x in v)[:16])

import random
random.seed(11)
def boot(x, y, n=5000):
    d = []
    for _ in range(n):
        d.append(st.median(random.choices(x, k=len(x))) - st.median(random.choices(y, k=len(y))))
    d.sort(); return round(st.median(x) - st.median(y)), d[int(.025 * n)], d[int(.975 * n)]
def get(e, frag, excl=None):
    return [x[0] for (ev, c), v in g.items() if ev == e and frag in c and (excl is None or excl not in c) for x in v]
for e in ("PostToolBatch", "SubagentStart"):
    S = get(e, "budget.py"); L = get(e, 'run_hook.py" budget'); X = get(e, "run_hook.py budget")
    print(e, "string-lean", boot(S, L), "lean-exec", boot(L, X), "string-exec", boot(S, X))
