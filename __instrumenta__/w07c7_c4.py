# Recomputes the 1-hour-cache break-even for authors (waves 4-7) from per-request TSVs (w07b_turns_tsv.py format; wave 4-6 rows from explorer-w07-b's requests.tsv, wave 7 rows from the same parser on the wave-7 PI transcript) with write prices (USD per Mtok: 5-minute 2.5, 1-hour 4.0, read 0.1; Sonnet 5.5, lab_status.PRICES, price ratio checked in w07c7_prices.py); a re-write is a request whose cache_read < 0.5 x previous context and cache_write > 0.5 x previous context; its gap is previous model_s + tool_s + this gap_prev_s + wait_s, binned <=300 s, 300-3600 s (a 1-hour cache would have held it), >3600 s (it would not); output markdown tables on stdout.
# usage: w07c7_c4.py REQUESTS_TSV_W456 TSV_W7 HARNESS_JSONL   (harness.jsonl maps wave-7 agent ids to names and types; other rows are named author-wNN-k)
import csv, sys, json, collections
f = lambda x: float(x) if x not in ("", None) else 0.0
rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t")) + list(csv.DictReader(open(sys.argv[2]), delimiter="\t"))
ids = {}
for l in open(sys.argv[3]):
    d = json.loads(l)
    if d.get("agent_id"): ids[d["agent_id"]] = (d.get("name"), d.get("type"))
by = collections.defaultdict(list)
for r in rows:
    n = r["name"]
    if r["label"] == "w7":
        nm, ty = ids.get(n, (n, "?"))
        if ty != "murmuration:author": continue
        r["name"] = nm
    elif "author" not in n: continue
    by[(r["label"], r["name"])].append(r)
W5, W1, RD = 2.5, 4.0, 0.1
tot = collections.defaultdict(float); per = []
for (lab, name), rs in sorted(by.items()):
    rs.sort(key=lambda r: int(r["k"]))
    prev = None; nm = {"le300": 0, "mid": 0, "gt3600": 0}; tk = {"le300": 0.0, "mid": 0.0, "gt3600": 0.0}; w = 0.0; usd = 0.0
    for i, r in enumerate(rs):
        ctx = f(r["cache_read"]) + f(r["cache_write"]) + f(r["input"]); w += f(r["cache_write"]); usd += f(r["usd"])
        if prev and f(r["cache_read"]) < 0.5 * prev and f(r["cache_write"]) > 0.5 * prev:
            p = rs[i - 1]
            el = f(p["model_s"]) + f(p["tool_s"]) + f(r["gap_prev_s"]) + f(r["wait_s"])
            b = "le300" if el <= 300 else ("mid" if el <= 3600 else "gt3600")
            nm[b] += 1; tk[b] += prev
        prev = ctx
    per.append((lab, name, len(rs), nm, tk, w, usd))
    for b in nm: tot["n_" + b] += nm[b]; tot["t_" + b] += tk[b]
    tot["w"] += w; tot["usd"] += usd; tot["workers"] += 1
print("| wave | author | requests | re-writes <=300 s | 300-3600 s | >3600 s | tokens re-written 300-3600 s | all write tokens | USD |\n|:--|:--|--:|--:|--:|--:|--:|--:|--:|")
for lab, name, n, nm, tk, w, usd in per:
    print("| %s | %s | %d | %d | %d | %d | %.0f | %.0f | %.2f |" % (lab, name, n, nm["le300"], nm["mid"], nm["gt3600"], tk["mid"], w, usd))
saved = tot["t_mid"] * (W5 - RD) / 1e6                 # a read at 0.1 instead of a re-write at 2.5, for re-writes a 1-hour entry would have held
extra = (tot["w"]) * (W1 - W5) / 1e6                   # every write token costs 1.5 more per Mtok, including the re-writes it now reads instead (upper bound of the extra: those are not written)
extra_exact = (tot["w"] - tot["t_mid"]) * (W1 - W5) / 1e6
print("\n| authors | re-writes in 300-3600 s | tokens | all write tokens | USD spend | saved (read 0.1 instead of write 2.5) | extra on remaining writes (4.0 - 2.5) | net |\n|--:|--:|--:|--:|--:|--:|--:|--:|")
print("| %d | %d | %.2fM | %.2fM | %.2f | %.2f | %.2f | %+.2f |" % (tot["workers"], tot["n_mid"], tot["t_mid"] / 1e6, tot["w"] / 1e6, tot["usd"], saved, extra_exact, saved - extra_exact))
print("\nre-writes <=300 s: %d (%.2fM tokens; not a TTL miss on the 5-minute rule: a different cause); >3600 s: %d (%.2fM tokens; a 1-hour entry would also have expired)" % (tot["n_le300"], tot["t_le300"] / 1e6, tot["n_gt3600"], tot["t_gt3600"] / 1e6))
