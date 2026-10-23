# Compares the PI's context growth per request in the 12 requests after the lab's one real compaction (s1 request 276) with its growth before it, from s1_w1-3_requests.tsv to a short table on stdout: a proxy for the tokens the PI re-reads to recover what the summary lost.
"""usage: w08e_recovery_growth.py REQUESTS_TSV [compaction request index, default 276]. Growth = ctx[k] - ctx[k-1] of consecutive requests that were cache hits (cr >= 0.9 x previous ctx); jumps over 20,000 tokens are listed apart."""
import csv, statistics, sys
rq = list(csv.DictReader(open(sys.argv[1]), delimiter="\t")); K = int(sys.argv[2]) if len(sys.argv) > 2 else 276
ctx = [int(r["ctx"]) for r in rq]; cr = [int(r["cr"]) for r in rq]
def growth(a, b): return [ctx[k] - ctx[k - 1] for k in range(a, b) if k > 0 and cr[k] >= 0.9 * ctx[k - 1] and 0 <= ctx[k] - ctx[k - 1] <= 20000]
for name, a, b in (("before: requests 1-%d" % (K - 1), 1, K), ("before: the 100 requests up to %d" % (K - 1), K - 100, K), ("after: %d-%d" % (K + 1, K + 12), K + 1, K + 13)):
    g = growth(a, b); print("%s: n=%d, mean %.0f, median %.0f, p90 %.0f, sum %d" % (name, len(g), statistics.mean(g), statistics.median(g), sorted(g)[int(.9 * len(g))], sum(g)))
big = [(k, ctx[k] - ctx[k - 1]) for k in range(K + 1, K + 13) if ctx[k] - ctx[k - 1] > 20000]
print("jumps over 20k in %d-%d: %s" % (K + 1, K + 12, big))
base = statistics.mean(growth(K - 100, K)); g = growth(K + 1, K + 13)
print("excess growth over the pre-compaction 100-request mean x %d requests: %.0f tokens (context at %d %d, at %d %d)" % (len(g), sum(g) - base * len(g), K, ctx[K], K + 12, ctx[K + 12]))
