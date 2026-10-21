# Summarises the live q2 sessions of w07-c2: joins probe.jsonl (sorted by hook start) to runs.jsonl (in run order) from the folder argv[1] and prints, per session, the wait until the prompt's transcript record was readable (from hook start), whether the record existed at the child's start, the record's origin fields, whether the branch's user_words.py stored the prompt, and the q2 count (found within 0.3 s among the first prompts run with the branch script); output: stdout.
import json, sys, os, statistics
W = sys.argv[1]
runs = [json.loads(l) for l in open(os.path.join(W, "runs.jsonl"))]
probe = sorted((json.loads(l) for l in open(os.path.join(W, "probe.jsonl"))), key=lambda d: d.get("t0", 0))
assert len(runs) == len(probe), (len(runs), len(probe))
print("name  hooks  prompt  wait_s(first readable, from hook start)  file existed at child start  record entrypoint  stored by branch script  payload keys")
q2 = []
for r, d in zip(runs, probe):
    lab = os.path.join(W, "lab-" + ("f00" if r["name"] == "r-f00" else "p00" if r["name"] == "r-p00" else r["name"]))
    f = os.path.join(lab, "__statera__", "user_words.md")
    stored = (os.path.exists(f) and "ok." in open(f).read()) if r["plugin"] == "both" else None
    w = d.get("wait_s")
    print("%-6s %-5s %-6s %-8s %-5s %-14s %-6s %s" % (r["name"], r["plugin"], "later" if r["resume"] else "first", "none" if w is None else "%.3f" % w, d.get("existed_at_start"), (d.get("record_fields") or {}).get("entrypoint"), stored, d["keys"]))
    if r["plugin"] == "both" and not r["resume"] and r["name"].startswith("f"): q2.append(w)
found = [w for w in q2 if w is not None and w <= 0.3]
print("\nq2: first prompts with the branch script as a hook: %d sessions; record readable within 0.3 s of hook start in %d (threshold 8)" % (len(q2), len(found)))
print("wait until readable (s), those sessions: min %.3f median %.3f max %.3f" % (min(q2), statistics.median(q2), max(q2)))
