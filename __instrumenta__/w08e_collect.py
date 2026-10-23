# Collects every compaction of the w08e headless runs (stream.jsonl compact_boundary + debug.log forked-agent usage) into one tsv on stdout, with the Opus 5.5 list price of each compaction request.
"""usage: w08e_collect.py S   (S = /private/tmp/murmuration-w08/explorer-w08-e; reads S/runs/*/stream.jsonl and debug.log). Columns: run, n, window, pre_tokens, post_tokens, duration_ms, input_uncached, output, cache_read, cache_write, usd_opus55."""
import glob, json, os, re, sys
S = sys.argv[1]
print("\t".join("run n window pre_tokens post_tokens duration_ms input_uncached output cache_read cache_write usd_opus55".split()))
for d in sorted(glob.glob(os.path.join(S, "runs", "*"))):
    sj = os.path.join(d, "stream.jsonl")
    if not os.path.exists(sj) or not os.path.exists(os.path.join(d, "debug.log")): continue
    b = []
    for l in open(sj):
        try: x = json.loads(l)
        except ValueError: continue
        if x.get("type") == "system" and x.get("subtype") == "compact_boundary": b.append(x["compact_metadata"])
    dbg = open(os.path.join(d, "debug.log"), errors="replace").read()
    fa = re.findall(r"Forked agent \[([\w-]+)\] finished: \d+ messages.*?totalUsage: input=(\d+) output=(\d+) cacheRead=(\d+) cacheCreate=(\d+)", dbg)
    w = re.findall(r"effectiveWindow=(\d+)", dbg); w = w[0] if w else ""
    for n, (m, f) in enumerate(zip(b, fa), 1):
        i, o, r, c = map(int, f[1:])
        print("\t".join(map(str, [os.path.basename(d), n, w, m["pre_tokens"], m["post_tokens"], m["duration_ms"], i, o, r, c, "%.4f" % ((i * 4 + o * 20 + r * 0.2 + c * 8) / 1e6)])))
