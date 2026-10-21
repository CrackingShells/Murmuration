# pools the per-worker detail written by w05c_worker_phases.py into shares by role and phase (requests, list-price USD, seconds), by token type, and lists the largest tool outputs, failed calls, re-reads and cold resumes; input: worker_phase_detail.json; output: markdown on stdout
import json, sys, collections

d = json.load(open(sys.argv[1]))
W5 = 0.1  # USD per million, cache read (Sonnet 5.5) -- same table as scripts/lab_status.py
P = (2.0, 10.0, 0.10, 2.5)  # input, output, cache read, cache write 5 min


def role(n):
    return "author" if n.startswith("author") else "reproducer" if n.startswith("reproducer") else "explorer" if n.startswith("explorer") else "other"


def pct(a, b):
    return "%.0f%%" % (100 * a / b) if b else "-"


groups = {"author": [], "reproducer": [], "explorer": [], "other": [], "all": []}
for n, a in d.items():
    groups[role(n)].append((n, a))
    groups["all"].append((n, a))

print("## Token-type split of list-price USD (input, cache write, cache read, output)")
print("| group | workers | requests | USD | input | cache write | cache read | output |")
print("|:--|--:|--:|--:|--:|--:|--:|--:|")
for g, ws in groups.items():
    comp = collections.Counter()
    nreq = 0
    for n, a in ws:
        for x in a["reqs"]:
            nreq += 1
            comp["in"] += x["inp"] * P[0] / 1e6
            comp["cw"] += x["cw"] * P[3] / 1e6
            comp["cr"] += x["cr"] * P[2] / 1e6
            comp["out"] += x["out"] * P[1] / 1e6
    t = sum(comp.values())
    if ws: print("| %s | %d | %d | %.2f | %s | %s | %s | %s |" % (g, len(ws), nreq, t, pct(comp["in"], t), pct(comp["cw"], t), pct(comp["cr"], t), pct(comp["out"], t)))

CATS = ["handback", "exchange", "deliver", "run", "write-other", "outside", "doc", "search", "wait", "look", "other", "none"]
print("\n## Phase shares (category of each request's tool calls; strongest call wins)")
for g, ws in groups.items():
    if not ws:
        continue
    req, usd, sec = collections.Counter(), collections.Counter(), collections.Counter()
    for n, a in ws:
        for x in a["reqs"]:
            req[x["cat"]] += 1
            usd[x["cat"]] += x["usd"]
            sec[x["cat"]] += x["model_s"] + x["tool_s"]
    R, U, S = sum(req.values()), sum(usd.values()), sum(sec.values())
    print("\n### %s: %d requests, USD %.2f, %.0f s" % (g, R, U, S))
    print("| category | requests | share | USD | share | seconds | share |")
    print("|:--|--:|--:|--:|--:|--:|--:|")
    for c in CATS:
        if req[c]:
            print("| %s | %d | %s | %.3f | %s | %.0f | %s |" % (c, req[c], pct(req[c], R), usd[c], pct(usd[c], U), sec[c], pct(sec[c], S)))

print("\n## Orientation prefix (requests before the first run/write/deliver/exchange/handback call, first run only)")
print("| worker | requests | prefix req | share | USD | prefix USD | share | s | prefix s | share |")
print("|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for n, a in d.items():
    R = a["reqs"]
    pr = [x for x in R if x["prefix"]]
    U = sum(x["usd"] for x in R)
    S = sum(x["model_s"] + x["tool_s"] for x in R)
    pu = sum(x["usd"] for x in pr)
    ps = sum(x["model_s"] + x["tool_s"] for x in pr)
    print("| %s | %d | %d | %s | %.3f | %.3f | %s | %.0f | %.0f | %s |" % (n, len(R), len(pr), pct(len(pr), len(R)), U, pu, pct(pu, U), S, ps, pct(ps, S)))

print("\n## Fixed start cost: first request (cache write of ~13-14k tokens) plus carrying that context for every later request at cache-read price")
tot_fixed = 0
for g in ("author", "reproducer", "explorer"):
    if not groups[g]:
        continue
    fx, tt = 0, 0
    for n, a in groups[g]:
        R = a["reqs"]
        f = R[0]["usd"] + R[0]["ctx"] * (len(R) - 1) * P[2] / 1e6
        fx += f
        tt += sum(x["usd"] for x in R)
    print("- %s: %.2f of %.2f (%s)" % (g, fx, tt, pct(fx, tt)))

print("\n## Cold resumes and in-run cache expiries (ESTIMATE: cache-write tokens x (write - read price); read price would have applied had the cache been warm)")
cold = []
for n, a in d.items():
    for r in a["resumes"]:
        if r["first_cw"] > 20000:
            cold.append((n, "resume %d (%s)" % (r["run"], r["origin"]), r["idle_s"], r["first_cw"], r["first_cw"] * (P[3] - P[2]) / 1e6, r["requests"], r["usd"], r["active_s"]))
    for m in a["misses"]:
        cold.append((n, "mid-run request %d" % m["n"], m["gap_s"], m["cw"], m["usd_extra"], 1, None, None))
print("| worker | event | idle or gap s | cache-write tokens | premium USD | requests in run | run USD | run active s |")
print("|:--|:--|--:|--:|--:|--:|--:|--:|")
for c in sorted(cold, key=lambda c: -c[4]):
    print("| %s | %s | %.0f | %d | %.3f | %s | %s | %s |" % (c[0], c[1], c[2], c[3], c[4], c[5], "-" if c[6] is None else "%.3f" % c[6], "-" if c[7] is None else "%.0f" % c[7]))
print("sum premium: %.2f of %.2f total" % (sum(c[4] for c in cold), sum(sum(x["usd"] for x in a["reqs"]) for a in d.values())))

print("\n## Warm resumes (cache read of the whole context): first-request cost vs the run it opens")
print("| worker | run | origin | idle s | first request USD | run requests | run USD | run active s |")
print("|:--|--:|:--|--:|--:|--:|--:|--:|")
for n, a in d.items():
    for r in a["resumes"]:
        if r["first_cw"] <= 20000:
            print("| %s | %d | %s | %.0f | %.3f | %d | %.3f | %.0f |" % (n, r["run"], r["origin"], r["idle_s"], r["first_usd"], r["requests"], r["usd"], r["active_s"]))

print("\n## Failed calls (is_error)")
for n, a in d.items():
    for f in a["fails"]:
        print("- %s req %d %s `%s` -> %s" % (n, f["n"], f["name"], f["arg"][:70], f["head"][:100]))

print("\n## Re-reads (same file by Read or a bare cat/head/sed/tail, more than once) and repeated Bash commands")
for n, a in d.items():
    if a["rereads"]:
        print("- %s: %s" % (n, {k.split("/")[-1]: v for k, v in a["rereads"].items()}))
for n, a in d.items():
    if a["repeats"]:
        print("- %s repeated bash: %s" % (n, {k[:60]: v for k, v in a["repeats"].items()}))

print("\n## Largest tool outputs by carry cost (one cache write, then a cache read at every later request; 4 chars per token)")
allc = []
for n, a in d.items():
    for c in a["carry"]:
        allc.append((c["usd"], n, c))
tot = sum(u for u, _, _ in allc)
print("pooled carry cost of all tool outputs: %.2f USD of %.2f total spend" % (tot, sum(sum(x["usd"] for x in a["reqs"]) for a in d.values())))
for thr in (2000, 8000, 20000):
    sel = [(u, n, c) for u, n, c in allc if c["chars"] > thr]
    print("- outputs over %d chars: %d of %d calls, carry %.2f USD (%s of carry)" % (thr, len(sel), len(allc), sum(u for u, _, _ in sel), pct(sum(u for u, _, _ in sel), tot)))
print("| carry USD | worker | request | call | chars | later requests | what |")
print("|--:|:--|--:|:--|--:|--:|:--|")
for u, n, c in sorted(allc, key=lambda t: -t[0])[:15]:
    print("| %.3f | %s | %d | %s | %d | %d | `%s` |" % (u, n, c["n"], c["name"], c["chars"], c["later"], c["arg"][:80].replace("|", "/")))

# ---------------------------------------------------------------- additions: time split, failure classes, batching, waits
import re
print("\n## Seconds by category, model side vs tool side")
msum, tsum = collections.Counter(), collections.Counter()
for n, a in d.items():
    for x in a["reqs"]:
        msum[x["cat"]] += x["model_s"]
        tsum[x["cat"]] += x["tool_s"]
print("| category | model s | tool s | tool share |")
print("|:--|--:|--:|--:|")
for c in CATS:
    if msum[c] + tsum[c]:
        print("| %s | %.0f | %.0f | %s |" % (c, msum[c], tsum[c], pct(tsum[c], msum[c] + tsum[c])))
print("| all | %.0f | %.0f | %s |" % (sum(msum.values()), sum(tsum.values()), pct(sum(tsum.values()), sum(msum.values()) + sum(tsum.values()))))
waits = [(x["tool_s"], n, x["n"], x["calls"]) for n, a in d.items() for x in a["reqs"] if x["tool_s"] > 120]
print("\ntool waits over 120 s: %d calls, %.0f s of %.0f s tool time" % (len(waits), sum(w[0] for w in waits), sum(tsum.values())))
for w in sorted(waits, reverse=True)[:12]:
    print("- %s req %d: %.0f s `%s`" % (w[1], w[2], w[0], (w[3][0][1] if w[3] else "")[:110].replace("\n", " ")))

def klass(f):
    h, a = f["head"], f["arg"]
    if "Blocked: sleep" in h:
        return "sleep blocked by the harness"
    if h.startswith("Exit code 1 (eval):") and "not found" in h:
        return "zsh: unquoted == or =word"
    if "PATH_NOT_FOUND" in h:
        return "colgrep: relative path"
    if "No such tool" in h:
        return "tool not available to this worker"
    if "Permission for this command was denied" in h:
        return "permission denied"
    if h.startswith("Exit code"):
        return "nonzero exit (probe, diff/grep/git/python traceback)"
    return "other"
print("\n## Failed calls by class (request cost = the whole request at that context; the retry costs one more)")
cl = collections.defaultdict(lambda: [0, 0.0, set()])
tot_calls = sum(len(x["calls"]) for a in d.values() for x in a["reqs"])
for n, a in d.items():
    for f in a["fails"]:
        k = klass(f)
        cl[k][0] += 1
        cl[k][1] += a["reqs"][f["n"]]["usd"]
        cl[k][2].add(n)
print("calls in total: %d; failed: %d" % (tot_calls, sum(v[0] for v in cl.values())))
print("| class | calls | workers | USD of those requests |")
print("|:--|--:|--:|--:|")
for k, v in sorted(cl.items(), key=lambda kv: -kv[1][0]):
    print("| %s | %d | %d | %.3f |" % (k, v[0], len(v[2]), v[1]))

print("\n## Calls per request")
cc = collections.Counter(len(x["calls"]) for a in d.values() for x in a["reqs"])
print(dict(sorted(cc.items())))

print("\n## Chains of consecutive read-only requests (look, doc, outside, search) that could have been one command")
lo = hi = nchain = 0
RO = ("look", "doc", "outside", "search")
for n, a in d.items():
    R = a["reqs"]
    i = 0
    while i < len(R):
        if R[i]["cat"] in RO and R[i]["run"] == 0:
            j = i
            while j + 1 < len(R) and R[j + 1]["cat"] in RO and R[j + 1]["run"] == R[i]["run"]:
                j += 1
            if j > i:
                nchain += 1
                for k in range(i + 1, j + 1):
                    lo += R[k]["ctx"] * P[2] / 1e6  # at least the cache read of the whole context
                    hi += R[k]["usd"]
            i = j + 1
        else:
            i += 1
tot = sum(x["usd"] for a in d.values() for x in a["reqs"])
print("chains of 2 or more: %d; USD saved if each chain were one request: between %.2f (cache reads only) and %.2f (whole requests) of %.2f (%s to %s)" % (nchain, lo, hi, tot, pct(lo, tot), pct(hi, tot)))

print("\n## Exchange latency (reproducer's question to the author's answer arriving in its queue)")
import datetime
def _ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
sends = []   # (worker, t, to)
arrive = []  # (worker, t, from, kind)
for n, a in d.items():
    for l in open(a["path"]):
        if '"SendMessage"' in l or 'agent-message from=' in l or '"origin"' in l:
            r = json.loads(l)
            t = _ts(r["timestamp"]) if r.get("timestamp") else None
            if r.get("type") == "assistant":
                for b in r["message"]["content"]:
                    if b.get("type") == "tool_use" and b["name"] == "SendMessage":
                        sends.append((n, t, b["input"].get("to"), len(json.dumps(b["input"]))))
            else:
                o = r.get("origin") or (r.get("attachment") or {}).get("origin") or {}
                if o.get("kind") == "peer" and r.get("timestamp"):
                    arrive.append((n, t, o.get("from"), r.get("type")))
print("| reproducer | author | question chars | answer after s | requests in the window | USD of those | of which a bare wait (sleep/until/poll) |")
print("|:--|:--|--:|--:|--:|--:|--:|")
lat = []
for (n, t, to, ch) in sends:
    if not n.startswith("reproducer"):
        continue
    nxt = sorted([x for x in arrive if x[0] == n and x[2] == to and x[1] >= t])
    reqs_in = [x for x in d[n]["reqs"] if nxt and t <= x["t"] <= nxt[0][1]]
    waits_in = [x for x in reqs_in if x["calls"] and re.match(r"\s*(sleep|until|timeout \d+ sh -c .until)", x["calls"][0][1] or "")]
    if nxt:
        lat.append(nxt[0][1] - t)
        print("| %s | %s | %d | %.0f | %d | %.3f | %d |" % (n, to, ch, nxt[0][1] - t, len(reqs_in), sum(x["usd"] for x in reqs_in), len(waits_in)))
    else:
        print("| %s | %s | %d | none seen | - | - | - |" % (n, to, ch))
if lat:
    lat.sort()
    print("\nanswer latency: n=%d, median %.0f s, min %.0f s, max %.0f s" % (len(lat), lat[len(lat) // 2], lat[0], lat[-1]))
print("\n## Cost of the exchange on the author side (runs opened by a peer message)")
pe = [(n, r) for n, a in d.items() for r in a["resumes"] if r["origin"] == "peer"]
print("peer-opened author runs: %d, USD %.2f, of which first requests %.2f; active %.0f s" % (len(pe), sum(r["usd"] for _, r in pe), sum(r["first_usd"] for _, r in pe), sum(r["active_s"] for _, r in pe)))
co = [(n, r) for n, a in d.items() for r in a["resumes"] if r["origin"] == "coordinator"]
print("coordinator-opened runs (raises, instructions): %d, USD %.2f; active %.0f s" % (len(co), sum(r["usd"] for _, r in co), sum(r["active_s"] for _, r in co)))
tn = [(n, r) for n, a in d.items() for r in a["resumes"] if r["origin"] == "task-notification"]
print("task-notification-opened runs: %d, USD %.2f" % (len(tn), sum(r["usd"] for _, r in tn)))

print("\n## ESTIMATE: split every tool wait over 240 s into polls of at most 240 s (so the 5 minute cache never lapses)")
import math
prem = extra = 0.0
nev = 0
for n, a in d.items():
    for m in a["misses"]:
        prev = a["reqs"][m["n"] - 1]
        k = max(1, math.ceil(m["gap_s"] / 240.0) - 1)  # extra requests
        poll = prev["ctx"] * P[2] / 1e6 + 200 * P[1] / 1e6  # a cache read of the context plus a short command
        prem += m["usd_extra"]
        extra += k * poll
        nev += 1
print("mid-run cache lapses: %d, premium %.2f USD; polling cost %.2f USD; net saving %.2f USD of %.2f total spend (%s)" % (nev, prem, extra, prem - extra, tot, pct(prem - extra, tot)))

print("\n## Orientation, three bounds (share of the worker's list-price USD / seconds)")
print("strict = requests among the first 3 of the first run whose strongest call is doc/search/outside; prefix = requests before the first run/write call (reads of evidence included); wide = every doc/search/outside request of any run")
print("| worker | strict req | strict USD | strict % | strict s | prefix % USD | wide % USD |")
print("|:--|--:|--:|--:|--:|--:|--:|")
tot_strict = tot_all = tot_prefix = tot_wide = 0.0
for n, a in d.items():
    R = a["reqs"]
    U = sum(x["usd"] for x in R)
    st = [x for x in R if x["n"] < 3 and x["run"] == 0 and x["cat"] in ("doc", "search", "outside")]
    pr = sum(x["usd"] for x in R if x["prefix"])
    wi = sum(x["usd"] for x in R if x["cat"] in ("doc", "search", "outside"))
    tot_strict += sum(x["usd"] for x in st); tot_all += U; tot_prefix += pr; tot_wide += wi
    print("| %s | %d | %.3f | %s | %.0f | %s | %s |" % (n, len(st), sum(x["usd"] for x in st), pct(sum(x["usd"] for x in st), U), sum(x["model_s"] + x["tool_s"] for x in st), pct(pr, U), pct(wi, U)))
print("pooled: strict %s, prefix %s, wide %s of %.2f USD" % (pct(tot_strict, tot_all), pct(tot_prefix, tot_all), pct(tot_wide, tot_all), tot_all))
