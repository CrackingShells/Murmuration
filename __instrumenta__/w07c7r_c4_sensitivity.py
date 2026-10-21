# Independent recomputation of the w07-c7 c4 break-even (1-hour cache for authors, waves 4-7) from the two request TSVs, plus sensitivity of the sign to the gap rule, the re-write rule, the token basis and to leaving one author out; inputs: explorer-w07-b requests.tsv, author-w07-6 requests_w7.tsv, harness.jsonl; output: markdown on stdout. Not importing the author's code.
# usage: w07c7r_c4_sensitivity.py REQ456 REQ7 HARNESS
import csv, sys, json, collections, random
fl = lambda x: float(x) if x not in ("", None) else None
rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t")) + list(csv.DictReader(open(sys.argv[2]), delimiter="\t"))
ids = {}
for l in open(sys.argv[3]):
    d = json.loads(l)
    if d.get("agent_id"): ids[d["agent_id"]] = (d.get("name"), d.get("type"))
A = collections.defaultdict(list)
for r in rows:
    if r["label"] == "w7":
        nm, ty = ids.get(r["name"], (r["name"], "?"))
        if ty != "murmuration:author": continue
        A[("w7", nm)].append(r)
    elif r["name"].startswith("author"): A[(r["label"], r["name"])].append(r)
for k in A: A[k].sort(key=lambda r: int(r["k"]))
print("authors", len(A), "requests", sum(len(v) for v in A.values()))
blank = collections.Counter(); tot = collections.Counter()
for (lab, n), rs in A.items():
    for r in rs: tot[lab] += 1; blank[lab] += (fl(r["model_s"]) is None)
print("blank model_s by wave:", {k: "%d/%d" % (blank[k], tot[k]) for k in tot})
def run(readfrac=0.5, wfrac=0.5, lo=300, hi=3600, gapmode="full", basis="prev", drop=None, authors=None):
    sv = ex = 0.0; n = 0; W = 0.0; per = {}
    for key, rs in A.items():
        if authors is not None and key not in authors: continue
        if key == drop: continue
        w = 0.0; s = 0.0; prev = None; pw = 0.0
        for i, r in enumerate(rs):
            cr, cw, inp = fl(r["cache_read"]) or 0, fl(r["cache_write"]) or 0, fl(r["input"]) or 0
            ctx = cr + cw + inp; w += cw
            if prev and cr < readfrac * prev and cw > wfrac * prev:
                p = rs[i - 1]; g = lambda c: fl(r[c]) if c in r else None
                ms = fl(p["model_s"]) or 0; ts = fl(p["tool_s"]) or 0; gp = fl(r["gap_prev_s"]) or 0; wt = fl(r["wait_s"]) or 0
                if gapmode == "full": el = ms + ts + gp + wt
                elif gapmode == "nomodel": el = ts + gp + wt
                elif gapmode == "ttfb": el = (fl(p["ttfb_s"]) or 0) + ts + gp + wt
                if lo < el <= hi: s += (prev if basis == "prev" else cw); n += 1
            prev = ctx
        per[key] = (s, w); sv += s; W += w
    saved = sv * 2.4 / 1e6; extra = (W - sv) * 1.5 / 1e6
    return n, sv, W, saved - extra, per
n, sv, W, net, per = run()
print("\nbase: n=%d tokens=%.2fM write=%.2fM net=%+.2f ratio=%.3f (break-even 0.385)" % (n, sv / 1e6, W / 1e6, net, sv / W))
print("\n| variant | n re-writes held | re-written tokens | net USD |\n|:--|--:|--:|--:|")
for name, kw in [("read<0.5,write>0.5 (author rule)", {}), ("read<0.9, write>0.1 (c2-like)", dict(readfrac=0.9, wfrac=0.1)), ("read<0.8, write>0.2", dict(readfrac=0.8, wfrac=0.2)),
                 ("gap without model_s", dict(gapmode="nomodel")), ("gap with ttfb instead of model_s", dict(gapmode="ttfb")),
                 ("lower bound 240 s", dict(lo=240)), ("lower bound 280 s", dict(lo=280)), ("lower bound 330 s", dict(lo=330)), ("lower bound 360 s", dict(lo=360)), ("lower bound 600 s", dict(lo=600)), ("upper bound 3000 s", dict(hi=3000)), ("upper bound 3300 s", dict(hi=3300)), ("tokens = actual cache_write of the re-write request", dict(basis="write")),
                 ("waves 4-6 only", dict(authors=[k for k in A if k[0] != "w7"]))]:
    n2, sv2, W2, net2, _ = run(**kw); print("| %s | %d | %.2fM | %+.2f |" % (name, n2, sv2 / 1e6, net2))
print("\nleave one author out (net):")
for k in sorted(A):
    n2, sv2, W2, net2, _ = run(drop=k)
    if abs(net2 - net) > 0.15: print("  drop %s: net %+.2f (n %d)" % (k, net2, n2))
print("\nper-author tokens held / write:", {"%s/%s" % k: (round(v[0] / 1e3), round(v[1] / 1e3)) for k, v in per.items() if v[0]})
random.seed(1); ks = list(A); nb = 20000; neg = 0; nets = []
for _ in range(nb):
    smp = [random.choice(ks) for _ in ks]
    s = sum(per[k][0] for k in smp); w = sum(per[k][1] for k in smp)
    v = (s * 2.4 - (w - s) * 1.5) / 1e6; nets.append(v); neg += v <= 0
nets.sort(); print("\nbootstrap over authors (20000, seed 1): P(net<=0) = %.3f; net 5%%/50%%/95%% = %+.2f %+.2f %+.2f" % (neg / nb, nets[int(.05 * nb)], nets[nb // 2], nets[int(.95 * nb)]))
