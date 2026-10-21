# Break-even of a 1-hour prompt cache by worker type (waves 4-6): per worker, tokens written (W) and prefix tokens re-written after a pause (R), two counting rules, net USD at Sonnet prices; input explorer-w07-b's requests.tsv; output JSON on stdout.
# usage: python3 -I __instrumenta__/w07_ttl_by_type.py __reports__/wave-07/explorer-w07-b/requests.tsv > out.json
# Rule "timed": a request whose recorded pause (tool_s + wait_s + gap_prev_s) is in (300, 3600] s; R += the previous context's tokens it did not read.
# Rule "miss": a request that read under half the previous context and whose pause is at most 3600 s and over 300 s (or unrecorded: wave 4 has no wait or gap times); R += the same.
# Net of a 1-hour cache = R * (2.50 - 0.10) - (W - R) * (4.00 - 2.50), per million tokens (scripts/lab_status.py PRICES, Sonnet); worth it iff R/W > 1.5/3.9 = 0.385.
import collections, csv, json, sys
fl = lambda x: float(x) if x not in ("", None) else None
rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
W = collections.defaultdict(list)
for r in rows:
    if r["name"] != "PI":
        W[(r["label"], r["name"])].append(r)
typ = lambda n: next((t for t in ("explorer", "author", "reproducer") if n.startswith(t)), "other")
res = {"threshold": 1.5 / 3.9, "workers": {}, "pauses": {}}
for mode in ("timed", "miss"):
    out = []
    for key, rs in W.items():
        rs.sort(key=lambda r: int(r["k"]))
        w = R = 0.0; prev = None; life = 0.0; ev = 0
        for r in rs:
            cr, cw, inp = fl(r["cache_read"]) or 0, fl(r["cache_write"]) or 0, fl(r["input"]) or 0
            ctx = cr + cw + inp
            gap = sum(fl(r[c]) or 0 for c in ("tool_s", "wait_s", "gap_prev_s"))
            life += gap + (fl(r["model_s"]) or 0)
            w += cw
            if prev:
                miss = max(0.0, prev - cr)
                if (mode == "timed" and 300 < gap <= 3600) or (mode == "miss" and cr < 0.5 * prev and gap <= 3600 and (gap > 300 or key[0] == "w4")):
                    R += miss; ev += 1
            prev = ctx
        out.append(dict(wave=key[0], name=key[1], type=typ(key[1]), requests=len(rs), life_min=round(life / 60, 1), W=round(w), R=round(R), events=ev,
                        net=round((R * 2.4 - (w - R) * 1.5) / 1e6, 3)))
    res["workers"][mode] = out
for t in ("author", "reproducer", "explorer"):
    c = collections.Counter()
    for key, rs in W.items():
        if typ(key[1]) != t:
            continue
        for r in rs[1:]:
            g = sum(fl(r[x]) or 0 for x in ("tool_s", "wait_s", "gap_prev_s"))
            c["<=60" if g <= 60 else "60-300" if g <= 300 else "300-3600" if g <= 3600 else ">3600"] += 1
    res["pauses"][t] = c
json.dump(res, sys.stdout, indent=1)
