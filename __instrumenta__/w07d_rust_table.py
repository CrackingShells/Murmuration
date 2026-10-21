"""Turns a w07d_rs `rep` log (stderr lines `rep K threads T wall_s W thread_s read R scan S serde P ...`, load lines kept) into the scaling table: wall min/med/max, speedup, efficiency, summed thread time, from the log path to stdout.

usage: w07d_rust_table.py LOG
"""
import re, sys, collections, statistics
d = collections.defaultdict(list); cpu = collections.defaultdict(list)
for l in open(sys.argv[1]):
    m = re.match(r"rep \d+ threads (\d+) wall_s ([\d.]+) thread_s read ([\d.]+) scan ([\d.]+) serde ([\d.]+)", l)
    if m:
        t = int(m[1]); d[t].append(float(m[2])); cpu[t].append(float(m[3]) + float(m[4]) + float(m[5]))
b = statistics.median(d[1])
print("threads | wall ms min / med / max | speedup (med) | efficiency | summed thread time ms")
for t in sorted(d):
    w = d[t]; print("%-7d | %5.1f / %5.1f / %5.1f | %.2f | %.2f | %.0f" % (t, min(w) * 1e3, statistics.median(w) * 1e3, max(w) * 1e3, b / statistics.median(w), b / statistics.median(w) / t, statistics.median(cpu[t]) * 1e3))
