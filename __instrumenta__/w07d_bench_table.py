"""Summarises a w07d_bench.py JSON-lines log per case name (wall min / median / max, median CPU, load average range), from the log path to a table on stdout.

usage: w07d_bench_table.py LOG.jsonl [LOG2.jsonl ...]
"""
import json, statistics, collections, sys
for path in sys.argv[1:]:
    d = collections.OrderedDict()
    for l in open(path):
        r = json.loads(l); d.setdefault(r['name'], []).append(r)
    print("#", path)
    for k, v in d.items():
        w = [x['wall'] for x in v]; c = [x['user'] + x['sys'] for x in v]
        print("%-14s n=%d wall min %.3f med %.3f max %.3f  cpu med %.2f  load1 %.1f-%.1f" % (k, len(v), min(w), statistics.median(w), max(w), statistics.median(c), min(x['load1'] for x in v), max(x['load1'] for x in v)))
