"""Splits the platform-recorded duration of the SubagentStart budget hook by command form and by the number of such records (any form, any worktree) within 5 s of it, itself included, from the transcripts of the lab's worktrees (read only; each record once by uuid); argv[1] = "frozen" (records before 2026-10-25T00:00Z) or "all"; output: markdown on stdout."""
import glob, json, os, sys, collections, statistics as st, datetime
root = os.path.expanduser("~/.claude/projects"); frozen = sys.argv[1] == "frozen"
files = set()
for pat in ("*Murmuration-murmuration-*", "*Murmuration-blissful*", "*Murmuration-lab-sys*", "*Murmuration-xeno*"):
    for d in glob.glob(root + "/" + pat):
        if "---reports" in d or "-private-tmp" in d: continue
        files |= set(glob.glob(d + "/*.jsonl")) | set(glob.glob(d + "/*/subagents/*.jsonl"))
R = {}
for f in sorted(files):
    for l in open(f, errors="replace"):
        if '"hook_success"' not in l or "SubagentStart" not in l: continue
        try: r = json.loads(l)
        except Exception: continue
        a = r.get("attachment") or {}; c = a.get("command") or ""
        if a.get("hookEvent") != "SubagentStart" or "budget" not in c: continue
        if frozen and r["timestamp"] >= "2026-10-25T00:00": continue
        form = "binary" if "bin/murmuration budget" in c else (("lean (string)" if 'run_hook.py" budget' in c else "exec") if "run_hook.py" in c else "string (budget.py)")
        R[r["uuid"]] = (datetime.datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).timestamp(), form, a["durationMs"])
V = sorted(R.values()); g = collections.defaultdict(list)
for t, form, d in V:
    n = sum(1 for t2, _, _ in V if abs(t2 - t) <= 5); g[(form, "1" if n == 1 else ("2" if n == 2 else ">=3"))].append(d)
print("records %s: %d" % (sys.argv[1], len(V)))
print("| form | starts within 5 s | n | median ms | min | max |"); print("|:--|:--|--:|--:|--:|--:|")
for k in sorted(g): print("| %s | %s | %d | %.1f | %d | %d |" % (k[0], k[1], len(g[k]), st.median(g[k]), min(g[k]), max(g[k])))
for form in ("exec", "binary"):
    allv = sum((g[(form, c)] for c in ("1", "2", ">=3")), []); print("%s: %d records, %d in a batch of 2 or more" % (form, len(allv), len(allv) - len(g[(form, "1")])))
