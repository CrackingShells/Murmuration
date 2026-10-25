"""Tabulates the platform-recorded duration (attachment.durationMs of hook_success) of the plugin's budget hook per hook event and per command form, with the earliest and latest record of each, from the transcripts of the lab's worktrees (read only, main threads and subagents); output: markdown on stdout. Only hooks that wrote stdout leave a record."""
import glob, json, os, collections, statistics as st
root = os.path.expanduser("~/.claude/projects")
files = set()
for pat in ("*Murmuration-murmuration-*", "*Murmuration-blissful*", "*Murmuration-lab-sys*", "*Murmuration-xeno*"):
    for d in glob.glob(root + "/" + pat):
        if "---reports" in d or "-private-tmp" in d: continue
        files |= set(glob.glob(d + "/*.jsonl")) | set(glob.glob(d + "/*/subagents/*.jsonl"))
g = collections.defaultdict(list)
for f in sorted(files):
    for l in open(f, errors="replace"):
        if '"hook_success"' not in l: continue
        try: r = json.loads(l)
        except Exception: continue
        a = r.get("attachment") or {}
        c = a.get("command") or ""
        if "budget" not in c: continue
        form = "binary" if "bin/murmuration budget" in c else (("run_hook.py, quoted (string form)" if 'run_hook.py" budget' in c else "run_hook.py, unquoted") if "run_hook.py" in c else "budget.py (string form)")
        g[(a.get("hookEvent"), form)].append((r["timestamp"], a["durationMs"]))
print("| event | command form | n | median ms | p90 ms | first record | last record |"); print("|:--|:--|--:|--:|--:|:--|:--|")
for k in sorted(g):
    v = sorted(g[k]); d = sorted(x[1] for x in v)
    print("| %s | %s | %d | %d | %d | %s | %s |" % (k[0], k[1], len(d), st.median(d), d[int(0.9 * (len(d) - 1))], v[0][0][:16], v[-1][0][:16]))
