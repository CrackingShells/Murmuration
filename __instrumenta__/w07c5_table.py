# Tabulates the live v1 sessions of w07-c5 from the work folder argv[1] (runs.jsonl, dbg-*.log, lab-*/__statera__/user_words.md, the sessions' transcripts): per session whether the platform backgrounded the user_words hook (and the ms it recorded), when the async hook finished (debug line), the entry written (count, delay of the file's last write after the hook started), the time from each prompt's user record to the next api-request record, and the crash trace of the mixed session; output: stdout tables (r2, r3, r4, r5 rows).
import json, sys, os, re, glob, datetime, statistics
W = sys.argv[1]
runs = [json.loads(l) for l in open(os.path.join(W, "runs.jsonl"))]
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
def transcript(r):
    lab = "f01" if r["name"] == "t-resume" else r["name"]
    return glob.glob(os.path.expanduser("~/.claude/projects/*%s-lab-%s/%s.jsonl" % (os.path.basename(W), lab, r["session_id"])))[0]
def prompts(path):
    """[(user record ts, text, next api-request ts or None)] in file order."""
    recs = [json.loads(l) for l in open(path)]
    out = []
    for i, d in enumerate(recs):
        if d.get("type") == "user" and "toolUseResult" not in d and isinstance(d.get("message", {}).get("content"), (str, list)) and d.get("promptId"):
            c = d["message"]["content"]; c = c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))
            nxt = next((ts(x["timestamp"]) for x in recs[i + 1:] if x.get("type") == "api-request" and x.get("timestamp")), None)
            out.append((ts(d["timestamp"]), c.strip()[:40], nxt, d.get("entrypoint"), d.get("origin"), d.get("promptSource")))
    return out
print("session  env       backgrounded(ms)  hook ran (s)  entries  last write after hook start (s)  user->first api-request (s)  record entrypoint")
r3 = []; rows = {}
for r in runs:
    name = r["name"]
    dbg = open(os.path.join(W, "dbg-%s.log" % name), errors="replace").read().splitlines()
    bg = [(ts(l.split()[0]), re.search(r"moved to the background \((\d+)ms\)", l)) for l in dbg if "user_words.py" in l and "moved to the background" in l]
    done = [ts(l.split()[0]) for l in dbg if "produced no response payload" in l]
    pr = prompts(transcript(r))
    lab = os.path.join(W, "lab-" + ("f01" if name == "t-resume" else name)); f = os.path.join(lab, "__statera__", "user_words.md")
    n_ent = len(re.findall(r"^## \d{4}", open(f).read(), re.M)) if os.path.exists(f) else 0
    wr = os.stat(f).st_mtime if os.path.exists(f) else None
    # for the resumed session the debug log covers the second prompt only
    t_bg = bg[0][0] if bg else None
    hook_s = (done[0] - t_bg) if (done and t_bg) else None
    last = pr[-1]
    api = (last[2] - last[0]) if last[2] else None
    rows[name] = dict(bg=bg[0][1].group(1) if bg else None, hook_s=hook_s, entries=n_ent, write_after=(wr - t_bg) if (wr and t_bg) else None, api=api, ent=last[3], env="terminal" if r["terminal_like"] else "inherited", prompts=pr)
    x = rows[name]
    print("%-8s %-9s %-17s %-13s %-8d %-32s %-28s %s" % (name, x["env"], x["bg"], "%.3f" % hook_s if hook_s else None, n_ent, "%.3f" % x["write_after"] if x["write_after"] else None, "%.3f" % api if api else None, x["ent"]))
    if name != "mixed": r3.append(api)
ok_bg = sum(1 for n, x in rows.items() if n != "mixed" and x["bg"] is not None)
print("\nr3: platform backgrounded the user_words hook in %d of %d sessions (mixed excluded); recorded start cost ms: %s" % (ok_bg, len(rows) - 1, sorted(int(x["bg"]) for n, x in rows.items() if n != "mixed" and x["bg"])))
print("r3: time from user record to first api-request, v1 sessions (s): median %.3f min %.3f max %.3f (n=%d)" % (statistics.median(r3), min(r3), max(r3), len(r3)))
m = rows["mixed"]; print("r3: main's script sync in the mixed session (n=1): user->first api-request %.3f s" % m["api"])
inh = [n for n, x in rows.items() if x["env"] == "inherited" and n not in ("mixed",)]; ter = [n for n, x in rows.items() if x["env"] == "terminal" and n != "t-resume"]
print("\nr2 inherited-env sessions (rule: drop): %s" % [(n, rows[n]["entries"], "%.3f" % rows[n]["hook_s"] if rows[n]["hook_s"] else None) for n in inh])
print("r2 terminal-like sessions (rule: keep, found if written < 1.5 s after hook start; the fallback writes at 3 s): %s" % [(n, rows[n]["entries"], "%.3f" % rows[n]["write_after"] if rows[n]["write_after"] else None) for n in ter])
# found in time = the async hook finished (debug line) within 1.5 s of its start, long before the 3 s the fallback would take; f01's file also holds the resumed prompt, so its first entry is checked as ">= 1" and its write time is taken from the hook
good = sum(1 for n in inh if rows[n]["entries"] == 0 and rows[n]["hook_s"] is not None and rows[n]["hook_s"] < 1.5) + sum(1 for n in ter if rows[n]["entries"] >= 1 and rows[n]["hook_s"] is not None and rows[n]["hook_s"] < 1.5)
print("r2: sessions where the async hook found the record in time and its outcome matches the rule: %d of %d" % (good, len(inh) + len(ter)))
f01 = os.path.join(W, "lab-f01", "__statera__", "user_words.md"); print("\nr4: lab-f01 (first prompt, then the resumed prompt), entries in file order:"); print(open(f01).read())

print("\nr5, the mixed session (main's script sync, a crashing copy of the v1 script as a sync row and as an async row with the same command): hook lines of the debug log")
for l in open(os.path.join(W, "dbg-mixed.log"), errors="replace"):
    if re.search(r"UserPromptSubmit|async_hook", l) and "cc-plugin" not in l: print("  " + re.sub(r"/private/tmp/murmuration-w07/author-w07-2/", "<work>/", l.strip())[:330])
