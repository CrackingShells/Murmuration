# Estimates, per worker type and wave, what a 1-hour prompt-cache TTL (write price 4.0 against 2.5 USD per Mtok for Sonnet 5.5, lab_status.PRICES) would save on the cache re-writes after long gaps against what it costs on every other cache write; input: explorer-w07-b's requests.tsv (one row per request: cache_read, cache_write, input tokens, client/idle/tool seconds); output: markdown table on stdout.
# usage: w07g_ttl_breakeven.py requests.tsv   Rule: a miss is a request with k>0 whose cache_read < 0.5 x previous context (read+write+input) and cache_write > 0.5 x previous context, after an elapsed time (previous tool_s + wait_s + gap) over 300 s when the row holds it; saved = missed tokens x (2.5-0.1)/1e6; extra = (writes - missed) x (4.0-2.5)/1e6.
import csv, sys, collections
rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
by = collections.defaultdict(list)
for r in rows:
    if r["name"] != "PI":
        by[(r["label"], r["name"])].append(r)
f = lambda x: float(x) if x not in ("", None) else 0.0
agg = collections.defaultdict(lambda: [0, 0, 0.0, 0, 0.0])  # workers, misses, missed tokens, write tokens, usd
for (lab, name), rs in by.items():
    rs.sort(key=lambda r: int(r["k"]))
    typ = "author" if "author" in name or name.startswith("a") and False else None
    typ = next((t for t in ("author", "reproducer", "explorer") if t in name), "other")
    a = agg[typ]
    a[0] += 1
    prev = None
    for r in rs:
        ctx = f(r["cache_read"]) + f(r["cache_write"]) + f(r["input"])
        a[3] += f(r["cache_write"]); a[4] += f(r["usd"])
        if prev and f(r["cache_read"]) < 0.5 * prev and f(r["cache_write"]) > 0.5 * prev:
            a[1] += 1; a[2] += prev
        prev = ctx
print("| type | workers | re-writes after a cache drop (rule) | tokens re-written | all cache-write tokens | worker USD | saved by 1h (USD) | extra on other writes (USD) | net |\n|:--|--:|--:|--:|--:|--:|--:|--:|--:|")
tot = [0, 0, 0.0, 0, 0.0]
for typ, a in sorted(agg.items()):
    sv = a[2] * 2.4 / 1e6; ex = (a[3] - a[2]) * 1.5 / 1e6
    print("| %s | %d | %d | %.2fM | %.2fM | %.2f | %.2f | %.2f | %+.2f |" % (typ, a[0], a[1], a[2] / 1e6, a[3] / 1e6, a[4], sv, ex, sv - ex))
    for i in range(5): tot[i] += a[i]
sv = tot[2] * 2.4 / 1e6; ex = (tot[3] - tot[2]) * 1.5 / 1e6
print("| all | %d | %d | %.2fM | %.2fM | %.2f | %.2f | %.2f | %+.2f |" % (tot[0], tot[1], tot[2] / 1e6, tot[3] / 1e6, tot[4], sv, ex, sv - ex))
