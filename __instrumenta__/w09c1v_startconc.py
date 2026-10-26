"""For SubagentStart budget-hook records (hook_success attachments in the transcripts of the lab's worktrees incl. the live wave-9 one, dedup by uuid), prints durationMs against how many SubagentStart budget records fall within 5 s (concurrent starts), per command form, to stdout; independent of w09f/w09c1 scripts."""
import json, glob, os, statistics as st, datetime
root = os.path.expanduser("~/.claude/projects")
LAB = ("8cff9e", "928ebd", "bc67fb", "34edd8", "1aa673", "3417be", "a25ae6")
T = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
seen = set(); rec = []
for d in glob.glob(root + "/*"):
    if not d.endswith(LAB) or "---reports" in d: continue
    for f in glob.glob(d + "/*.jsonl") + glob.glob(d + "/*/subagents/agent-*.jsonl"):
        for l in open(f, errors="replace"):
            if '"hook_success"' not in l: continue
            try: r = json.loads(l)
            except Exception: continue
            a = r.get("attachment") or {}
            if a.get("hookEvent") != "SubagentStart" or "budget" not in a.get("command", "") or r["uuid"] in seen: continue
            seen.add(r["uuid"])
            c = a["command"]; form = "binary" if "bin/murmuration" in c else ("exec" if "run_hook.py budget" in c and '"' not in c else ("lean" if "run_hook.py" in c else "string"))
            rec.append((form, T(r["timestamp"]), a["durationMs"]))
for form in ("string", "lean", "exec", "binary"):
    s = sorted(x for x in rec if x[0] == form)
    conc = {}
    for x in s: conc[x] = sum(1 for y in s if abs(y[1] - x[1]) <= 5)
    for k in (1, 2, 3):
        v = [x[2] for x in s if (conc[x] == k if k < 3 else conc[x] >= 3)]
        if v: print(form, "concurrent starts", k if k < 3 else ">=3", "n", len(v), "median", st.median(v), "min", min(v), "max", max(v))
print("binary records:", [(round(x[1]), x[2]) for x in sorted(x for x in rec if x[0] == "binary")])
