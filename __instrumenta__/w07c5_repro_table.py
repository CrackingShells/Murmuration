# Tabulates reproducer-w07-2's live sessions from the work folder argv[1] (runs.jsonl, dbg-*.log, lab-*/__statera__/user_words.md, session transcripts under ~/.claude/projects, read only): per session the user_words hook's debug lines (backgrounded ms, finish time after start, hook ERROR lines), the entries written, the last write time after the hook start, the time from the prompt's user record to the next api-request record and the record's origin fields; output: stdout.
import json, os, sys, re, glob, datetime, statistics
W = sys.argv[1]; runs = [json.loads(l) for l in open(W + "/runs.jsonl") if json.loads(l).get("session_id")]
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
def prompts(path):
    recs = [json.loads(l) for l in open(path)]; out = []
    for i, d in enumerate(recs):
        if d.get("type") == "user" and "toolUseResult" not in d and d.get("promptId") and isinstance(d.get("message", {}).get("content"), (str, list)):
            nxt = next((ts(x["timestamp"]) for x in recs[i + 1:] if x.get("type") == "api-request" and x.get("timestamp")), None)
            c = d["message"]["content"]; c = c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))
            out.append((ts(d["timestamp"]), (nxt - ts(d["timestamp"])) if nxt else None, d.get("entrypoint"), (d.get("origin") or {}).get("kind"), c.strip()[:30]))
    return out
rows = []
print("%-8s %-5s %-16s %-9s %-26s %-8s %-9s %-9s %-10s %s" % ("session", "env", "plugin", "bg ms", "hook finish after start s", "entries", "write-start", "user->api", "entrypoint", "origin"))
for r in runs:
    n = r["name"]; dbg = open(W + "/dbg-%s.log" % n, errors="replace").read().splitlines()
    ups = [l for l in dbg if "user_words.py" in l or "async_hook" in l or "inject_plan" in l]
    start = None; fin = None; bg = None; err = None
    for l in dbg:
        if "user_words.py" in l and "moved to the background" in l: start = ts(l.split()[0]); bg = re.search(r"\((\d+)ms\)", l).group(1)
        if "async_hook" in l and "produced no response payload" in l and fin is None: fin = ts(l.split()[0])
        if "user_words.py" in l and "finished with status" in l and start is None:
            fin = ts(l.split()[0]); m = re.search(r"\((\d+)ms\)", l); start = fin - int(m.group(1)) / 1000
        if "[ERROR]" in l and "UserPromptSubmit" in l and err is None: err = (ts(l.split()[0]) - start) if start else None
    lab = r["lab"]; f = lab + "/__statera__/user_words.md"
    ent = len(re.findall(r"^## \d{4}", open(f).read(), re.M)) if os.path.exists(f) else 0
    wr = (os.stat(f).st_mtime - start) if (os.path.exists(f) and start) else None
    tr = glob.glob(os.path.expanduser("~/.claude/projects/*" + os.path.basename(lab).replace(".", "-") + "/%s.jsonl" % r["session_id"]))
    pr = prompts(tr[0])[-1] if tr else (None, None, None, None, None)
    rows.append((n, r, pr))
    print("%-8s %-5s %-16s %-9s %-26s %-8d %-9s %-9s %-10s %s%s" % (n, r["kind"], r["plugin"], bg, ("%.3f" % (fin - start)) if (fin and start) else None, ent, ("%.2f" % wr) if wr is not None else None, ("%.3f" % pr[1]) if pr[1] else None, pr[2], pr[3], ("   ERROR line at +%.2fs" % err) if err else ""))
for kind, label in (("exp-branch", "v1 async"), ("exp-main", "main sync")):
    xs = [pr[1] for n, r, pr in rows if r["plugin"] == kind and pr[1] and n != "s0r"]
    print("user->first api-request, %s: n=%d median %.3f min %.3f max %.3f" % (label, len(xs), statistics.median(xs), min(xs), max(xs)))
print("\nresumed session s0 -> s0r, entries:"); print(open(W + "/lab-s0/__statera__/user_words.md").read())
