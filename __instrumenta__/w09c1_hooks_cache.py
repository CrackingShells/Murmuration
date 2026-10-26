"""Re-derives M3 (platform-recorded duration of the budget hook per command form, records counted once by uuid, bootstrap intervals of the differences of medians) and the per-author view of M4 (pauses over 300 s per author in three eras, permutation test, effect of the one outlier author) from the transcripts of the lab's worktrees (read only) and threads.tsv (argv[1]); output: markdown on stdout; seed 20261025; records that start after 2026-10-25T00:00Z are left out."""
import glob, json, os, sys, csv, random, datetime, collections, statistics as st
root = os.path.expanduser("~/.claude/projects"); random.seed(20261025)
def boot(a, b, n=10000):
    d = sorted(st.median([random.choice(a) for _ in a]) - st.median([random.choice(b) for _ in b]) for _ in range(n)); return d[int(.025 * n)], d[int(.975 * n)]
files = set()
for pat in ("*Murmuration-murmuration-*", "*Murmuration-blissful*", "*Murmuration-lab-sys*", "*Murmuration-xeno*"):
    for d in glob.glob(root + "/" + pat):
        if "---reports" in d or "-private-tmp" in d: continue
        files |= set(glob.glob(d + "/*.jsonl")) | set(glob.glob(d + "/*/subagents/*.jsonl"))
g = collections.defaultdict(dict); dup = 0
for f in sorted(files):
    for l in open(f, errors="replace"):
        if '"hook_success"' not in l: continue
        try: r = json.loads(l)
        except Exception: continue
        a = r.get("attachment") or {}; c = a.get("command") or ""
        if "budget" not in c or r["timestamp"] >= "2026-10-25T00:00": continue
        form = "4 binary" if "bin/murmuration budget" in c else (("2 lean, string form (run_hook.py quoted)" if 'run_hook.py" budget' in c else "3 exec form (run_hook.py)") if "run_hook.py" in c else "1 budget.py, string form")
        k = (a.get("hookEvent"), form)
        if r.get("uuid") in g[k]: dup += 1
        g[k][r.get("uuid")] = (r["timestamp"], a["durationMs"])
print("## M3 hook durations, each record once by uuid (%d duplicate records removed)" % dup)
print("| event | form | n | median ms | p90 ms | first to last (UTC) |"); print("|:--|:--|--:|--:|--:|:--|")
D = {}
for k in sorted(g, key=lambda k: (k[0], k[1])):
    v = sorted(g[k].values()); d = sorted(x[1] for x in v); D[k] = d
    print("| %s | %s | %d | %d | %d | %s to %s |" % (k[0], k[1][2:], len(d), st.median(d), d[int(.9 * (len(d) - 1))], v[0][0][:16], v[-1][0][:16]))
for ev in ("PostToolBatch", "SubagentStart"):
    for a, b in (("1 budget.py, string form", "2 lean, string form (run_hook.py quoted)"), ("2 lean, string form (run_hook.py quoted)", "3 exec form (run_hook.py)"), ("1 budget.py, string form", "3 exec form (run_hook.py)")):
        if (ev, a) in D and (ev, b) in D:
            lo, hi = boot(D[(ev, a)], D[(ev, b)]); print("%s %s -> %s: median %d -> %d, difference %d ms, bootstrap 95%% interval [%d, %d]" % (ev, a[2:12], b[2:12], st.median(D[(ev, a)]), st.median(D[(ev, b)]), st.median(D[(ev, a)]) - st.median(D[(ev, b)]), lo, hi))
# ---- M4 per author
H = os.path.dirname(os.path.abspath(sys.argv[1])) + "/"
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter="\t") if r["kind"] == "sub" and r["agent_type"] == "murmuration:author" and r["proj"].startswith("wt:") and r["start"] < "2026-10-25"]
def T(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
per = {0: [], 1: [], 2: []}
for r in rows:
    fs = [f for f in glob.glob(root + "/*" + r["proj"][3:] + "/*/subagents/agent-*.jsonl") if os.path.basename(f)[6:14] == r["file"] and "---reports" not in f]
    last = {}; order = []
    for l in open(fs[0], errors="replace"):
        try: x = json.loads(l)
        except Exception: continue
        if x.get("type") == "assistant":
            rid = x.get("requestId") or x["message"].get("id")
            if rid not in last: order.append(rid)
            last[rid] = x["timestamp"]
    ts = [T(last[i]) for i in order]; gaps = [b - a for a, b in zip(ts, ts[1:]) if b - a > 300]
    era = 0 if r["start"] < "2026-10-21T08:08" else (1 if r["start"] < "2026-10-21T17:38" else 2)
    per[era].append((r["name"] or r["file"], len(gaps), max(gaps) / 60 if gaps else 0, r["proj"][3:20]))
print("\n## M4 pauses over 300 s per author (gap between the last record of one request and the next request)")
for e, lab in enumerate(("a before w05-c1", "b w05-c1..w07-c7", "c after w07-c7")):
    v = [x[1] for x in per[e]]; print("%s: authors %d, pauses %d, per author %.2f, authors with at least one pause %d, max pauses by one author %d" % (lab, len(v), sum(v), sum(v) / len(v), sum(1 for x in v if x), max(v)))
    print("   top:", sorted(per[e], key=lambda x: -x[1])[:3])
def perm(a, b, n=20000):
    obs = st.mean(a) - st.mean(b); z = a + b; c = 0
    for _ in range(n):
        random.shuffle(z); c += (st.mean(z[:len(a)]) - st.mean(z[len(a):])) >= obs
    return obs, c / n
a = [x[1] for x in per[0]]; b = [x[1] for x in per[1]]; c = [x[1] for x in per[2]]
print("pauses per author a - b: %.2f, one-sided permutation p %.3f; b - c: %.2f, p %.3f; a - c: %.2f, p %.3f" % (*perm(a, b), *perm(b, c), *perm(a, c)))
a2 = sorted(a)[:-1]; print("era a without its top author: %.2f pauses per author (n=%d) vs b %.2f; permutation p %.3f" % (st.mean(a2), len(a2), st.mean(b), perm(a2, b)[1]))
