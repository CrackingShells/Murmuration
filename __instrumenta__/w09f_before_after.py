"""Before/after tables for three landed changes (w05-c7 PI denylist, w02-c4 workers without Skill, w08-c6 short hand-backs) from `__reports__/wave-09/explorer-w09-f/threads.tsv` (made by `__instrumenta__/w09f_threads.py`) and the PI transcripts it names (read only); output: markdown on stdout, the PI's per-session USD priced at list price (PRICES copied from scripts/lab_status.py)."""
import csv, glob, json, os, statistics as st, collections
H = os.path.dirname(os.path.abspath(__file__)) + "/../__reports__/wave-09/explorer-w09-f/"
rows = list(csv.DictReader(open(H + "threads.tsv"), delimiter="\t"))
PR = {"opus": (4.0, 20.0, 0.20, 5.0, 8.0), "sonnet": (2.0, 10.0, 0.10, 2.5, 4.0)}
def usd_and_reads(path):
    last = {}
    for l in open(path, errors="replace"):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("type") == "assistant":
            m = r.get("message", {})
            if m.get("model") == "<synthetic>": continue
            last[r.get("requestId") or m.get("id")] = m
    tot = 0.0; n = 0
    for m in last.values():
        u = m.get("usage") or {}; p = PR["opus" if "opus" in (m.get("model") or "") else "sonnet"]
        cc = u.get("cache_creation") or {}
        w5 = cc.get("ephemeral_5m_input_tokens", None); w1 = cc.get("ephemeral_1h_input_tokens", 0)
        if w5 is None: w5, w1 = u.get("cache_creation_input_tokens") or 0, 0
        tot += ((u.get("input_tokens") or 0) * p[0] + (u.get("output_tokens") or 0) * p[1] + (u.get("cache_read_input_tokens") or 0) * p[2] + w5 * p[3] + w1 * p[4]) / 1e6
        n += 1
    return tot, n
print("## M1: the PI's request 0 before and after the denylist line (w05-c7, merged fed7a08 at 2026-10-21T08:08Z)")
print("| session | start (UTC) | version | requests | request-0 tokens | PI main-thread USD (list) | rel. to merge |")
print("|:--|:--|:--|--:|--:|--:|:--|")
pis = sorted([r for r in rows if r["kind"] == "main" and r["proj"].startswith("wt:") and int(r["reqs"]) > 30], key=lambda r: r["start"])
base = {}
for r in pis:
    d = glob.glob(os.path.expanduser("~/.claude/projects/*" + r["proj"][3:] + "/" + r["file"] + "*.jsonl"))
    d = [x for x in d if "---reports" not in x and "-private-tmp" not in x]
    usd, n = usd_and_reads(d[0]) if d else (float("nan"), 0)
    after = r["start"] > "2026-10-21T08:08"
    print("| %s %s | %s | %s | %s | %s | %.2f | %s |" % (r["proj"][3:25], r["file"], r["start"][:16], r["version"], r["reqs"], r["req0_tokens"], usd, "after" if after else "before"))
    base.setdefault(after, []).append((int(r["req0_tokens"]), int(r["reqs"]), usd))
b = st.mean(x[0] for x in base[False]); a = st.mean(x[0] for x in base[True]); print("\nmean request 0 before %.0f (n=%d), after %.0f (n=%d), difference %.0f (%.1f%%)" % (b, len(base[False]), a, len(base[True]), b - a, 100 * (b - a) / b))
cr = 0.20
for (t, n, u) in base[True]:
    print("  after-session: %d requests x %.0f tokens x USD %.2f/M cache read = USD %.2f ceiling of saving (+ one write at 8/M: %.2f) vs session USD %.2f = %.1f%%" % (n, b - t, cr, (b - t) * n * cr / 1e6, (b - t) * 8 / 1e6, u, 100 * ((b - t) * n * cr / 1e6) / u))
print("\n## M2: workers' request 0 by type and day (w02-c4, merged 84ff038 at 2026-10-19T14:53Z)")
ws = [r for r in rows if r["kind"] == "sub" and r["proj"].startswith("wt:") and r["agent_type"].startswith("murmuration:") and r["req0_tokens"] not in ("", "None")]
print("| type | day (UTC) | n | median request 0 | min | max | median requests | max start |"); print("|:--|:--|--:|--:|--:|--:|--:|:--|")
g = collections.defaultdict(list)
for r in ws: g[(r["agent_type"][12:], r["start"][:10])].append(r)
for k in sorted(g):
    v = [int(r["req0_tokens"]) for r in g[k]]; q = [int(r["reqs"]) for r in g[k]]
    print("| %s | %s | %d | %d | %d | %d | %d | %s |" % (k[0], k[1], len(v), st.median(v), min(v), max(v), st.median(q), max(r["start"] for r in g[k])[11:16]))
pre = [r for r in ws if r["start"] < "2026-10-19T14:53"]; post = [r for r in ws if r["start"] >= "2026-10-19T14:53"]
b2 = st.median(int(r["req0_tokens"]) for r in pre); a2 = st.median(int(r["req0_tokens"]) for r in post)
print("\nbefore the merge n=%d median %d; after n=%d median %d; difference %d (%.1f%%)" % (len(pre), b2, len(post), a2, b2 - a2, 100 * (b2 - a2) / b2))
cap = sum((b2 - int(r["req0_tokens"])) * int(r["reqs"]) * 0.10 / 1e6 for r in post)
print("ceiling of saving over the %d later workers: sum of (difference x requests) x USD 0.10/M (Sonnet cache read) = USD %.2f" % (len(post), cap))
print("\n## M3: hand-back length (characters of the SubagentHandback message) by start time (w08-c6, merged 16b05a8 at 2026-10-23T16:30Z)")
print("| period | n | median chars | p25 | p75 | max |"); print("|:--|--:|--:|--:|--:|--:|")
def per(lab, sel):
    v = sorted(int(r["handback_chars"]) for r in sel if r["handback_chars"] not in ("", "0"))
    if v: print("| %s | %d | %d | %d | %d | %d |" % (lab, len(v), st.median(v), v[len(v)//4], v[(3*len(v))//4], v[-1]))
for t in ("explorer", "author", "reproducer"):
    S = [r for r in ws if r["agent_type"] == "murmuration:" + t]
    per(t + " before", [r for r in S if r["start"] < "2026-10-23T16:30"])
    per(t + " after", [r for r in S if r["start"] >= "2026-10-23T16:30"])
S = ws; per("all before", [r for r in S if r["start"] < "2026-10-23T16:30"]); per("all after", [r for r in S if r["start"] >= "2026-10-23T16:30"])
print("\nafter the merge, one row per worker (name, start, chars):")
for r in sorted([r for r in ws if r["start"] >= "2026-10-23T16:30"], key=lambda r: r["start"]): print("  ", r["name"], r["start"][:16], r["handback_chars"])
mw = [int(r["handback_chars"]) for r in ws if r["start"] < "2026-10-23T16:30" and r["handback_chars"] not in ("", "0")]
print("\nby wave day before the merge (median chars, n):")
d = collections.defaultdict(list)
for r in ws:
    if r["start"] < "2026-10-23T16:30" and r["handback_chars"] not in ("", "0"): d[r["start"][:10]].append(int(r["handback_chars"]))
for k in sorted(d): print("  ", k, int(st.median(d[k])), len(d[k]))
