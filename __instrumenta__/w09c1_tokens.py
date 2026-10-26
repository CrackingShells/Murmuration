"""Re-derives M1 (PI request 0, w05-c7), M2 (workers' request 0, w02-c4) and M6 (hand-back length, w08-c6) of explorer-w09-f's findings with the resumed PI session counted once, bootstrap intervals (seed 20261025) and first and last hand-backs, from threads.tsv (made by w09f_threads.py) and the transcripts it names (read only); input: threads.tsv path as argv[1]; output: markdown on stdout. Only threads that started before 2026-10-25T00:00Z are used."""
import csv, glob, json, os, sys, random, statistics as st, collections
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter="\t") if r["start"] < "2026-10-25T00:00"]
root = os.path.expanduser("~/.claude/projects"); random.seed(20261025)
def boot(a, b, f=st.median, n=10000):
    d = sorted(f([random.choice(a) for _ in a]) - f([random.choice(b) for _ in b]) for _ in range(n)); return d[int(.025 * n)], d[int(.975 * n)]
def path(r):
    if r["kind"] == "main": return [x for x in glob.glob(root + "/*" + r["proj"][3:] + "/" + r["file"] + "*.jsonl") if "---reports" not in x and "-private-tmp" not in x][0]
    return [x for x in glob.glob(root + "/*" + r["proj"][3:] + "/*/subagents/agent-" + r["file"] + "*.jsonl")][0]
# ---- M1
MERGE1 = "2026-10-21T08:08"
pis = sorted([r for r in rows if r["kind"] == "main" and r["proj"].startswith("wt:") and int(r["reqs"]) > 30], key=lambda r: r["start"])
ids = {}
for r in pis:
    s = set()
    for l in open(path(r), errors="replace"):
        try: x = json.loads(l)
        except Exception: continue
        if x.get("type") == "assistant": s.add(x.get("requestId") or x["message"].get("id"))
    ids[r["file"]] = s
print("## M1 PI request 0, resumed sessions counted once")
indep = []
for i, r in enumerate(pis):
    prev = [p for p in pis[:i] if p["proj"] == r["proj"] and len(ids[p["file"]] & ids[r["file"]]) > 0.5 * len(ids[p["file"]])]
    sh = max([len(ids[p["file"]] & ids[r["file"]]) for p in pis[:i] if p["proj"] == r["proj"]] or [0])
    print("%s %s %s start %s version %s requests %s request-0 %s; request ids shared with an earlier session of the same folder: %d%s" % (r["proj"][3:20], r["file"], "after" if r["start"] > MERGE1 else "before", r["start"][:16], r["version"], r["reqs"], r["req0_tokens"], sh, " -> RESUME, dropped" if prev else ""))
    if not prev: indep.append(r)
b = [int(r["req0_tokens"]) for r in indep if r["start"] <= MERGE1]; a = [int(r["req0_tokens"]) for r in indep if r["start"] > MERGE1]
print("independent sessions: before n=%d %s mean %.0f; after n=%d %s mean %.0f; difference %.0f (%.1f%%); min before %d > max after %d: %s" % (len(b), b, st.mean(b), len(a), a, st.mean(a), st.mean(b) - st.mean(a), 100 * (st.mean(b) - st.mean(a)) / st.mean(b), min(b), max(a), min(b) > max(a)))
from math import comb
print("exact one-sided permutation p (all %d before above all %d after): 1/C(%d,%d) = %.3f" % (len(b), len(a), len(a) + len(b), len(b), 1 / comb(len(a) + len(b), len(b))))
# ---- M2
ws = [r for r in rows if r["kind"] == "sub" and r["proj"].startswith("wt:") and r["agent_type"].startswith("murmuration:") and r["req0_tokens"] not in ("", "None")]
MERGE2 = "2026-10-19T14:53"
pre = [int(r["req0_tokens"]) for r in ws if r["start"] < MERGE2]; post = [int(r["req0_tokens"]) for r in ws if r["start"] >= MERGE2]
lo, hi = boot(pre, post)
print("\n## M2 workers' request 0 (start before 2026-10-25; the 4 wave-9 live explorers excluded)")
print("before n=%d median %d (min %d max %d); after n=%d median %d (min %d max %d); difference %d (%.1f%%), bootstrap 95%% interval of the difference of medians [%d, %d]" % (len(pre), st.median(pre), min(pre), max(pre), len(post), st.median(post), min(post), max(post), st.median(pre) - st.median(post), 100 * (st.median(pre) - st.median(post)) / st.median(pre), lo, hi))
print("sessions in the before group: %s; its latest start %s; first start of the after group %s (no worker between)" % (sorted({r['proj'][3:30] for r in ws if r['start'] < MERGE2}), max(r['start'] for r in ws if r['start'] < MERGE2)[:16], min(r['start'] for r in ws if r['start'] >= MERGE2)[:16]))
cap = sum((st.median(pre) - int(r["req0_tokens"])) * int(r["reqs"]) * 0.10 / 1e6 for r in ws if r["start"] >= MERGE2)
print("ceiling (difference x own requests x USD 0.10/M): USD %.2f over %d later workers" % (cap, len(post)))
# ---- M6
MERGE6 = "2026-10-23T16:30"
def handbacks(r):
    h = []
    for l in open(path(r), errors="replace"):
        if "SubagentHandback" not in l: continue
        try: x = json.loads(l)
        except Exception: continue
        if x.get("type") == "assistant":
            for c in (x["message"].get("content") or []):
                if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "SubagentHandback": h.append(len(str((c.get("input") or {}).get("message", ""))))
    return h
H = [(r, handbacks(r)) for r in ws]
print("\n## M6 hand-back length (characters of the SubagentHandback message)")
print("workers with no SubagentHandback call: %d of %d; with 2 or more: %d" % (sum(1 for r, h in H if not h), len(H), sum(1 for r, h in H if len(h) > 1)))
def line(lab, sel, which):
    v = sorted((h[0] if which == "first" else h[-1]) for r, h in sel if h)
    return "| %s | %s | %d | %d | %d | %d | %d |" % (lab, which, len(v), st.median(v), v[len(v) // 4], v[3 * len(v) // 4], v[-1]), v
print("| group | hand-back | n | median | p25 | p75 | max |"); print("|:--|:--|--:|--:|--:|--:|--:|")
for which in ("first", "last"):
    for lab, sel in (("all before", [x for x in H if x[0]["start"] < MERGE6]), ("all after", [x for x in H if x[0]["start"] >= MERGE6]),
                     ("before, excluding 10-23 (the wave whose own briefs were already treated)", [x for x in H if x[0]["start"] < "2026-10-23"]),
                     ("10-23 before merge", [x for x in H if "2026-10-23" <= x[0]["start"] < MERGE6])):
        s, v = line(lab, sel, which); print(s)
        if lab == "all before": vb = v
        if lab == "all after": va = v
    lo, hi = boot(vb, va); print("  -> %s: bootstrap 95%% interval of before-minus-after median [%d, %d]" % (which, lo, hi))
for t in ("explorer", "author", "reproducer"):
    for lab, sel in (("before", lambda r: r["start"] < MERGE6), ("after", lambda r: r["start"] >= MERGE6)):
        v = sorted(h[0] for r, h in H if r["agent_type"] == "murmuration:" + t and sel(r) and h)
        print("%s %s first n=%d median %d" % (t, lab, len(v), st.median(v)))
print("after the merge (first hand-back chars):", [(r["name"], h[0]) for r, h in sorted(H, key=lambda x: x[0]["start"]) if r["start"] >= MERGE6 and h])
