"""Prints min / median / max wall of each JSON line of a w07d_parsers.py `time` log, as a table, from the log path to stdout.

usage: w07d_table.py LOG.jsonl
"""
import sys, json, statistics
for l in open(sys.argv[1]):
    d = json.loads(l); w = d['walls']
    print('%-9s W=%-2d min %.3f med %.3f max %.3f load %.1f' % (d['variant'], d['workers'], min(w), statistics.median(w), max(w), d['load1']))
