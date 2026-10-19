"""Aggregate record shapes of one transcript (no content printed)."""
import json, collections, sys
c = collections.Counter()
for l in open(sys.argv[1]):
    try: r = json.loads(l)
    except Exception: continue
    k = (r.get("type"), r.get("subtype"), r.get("operation"), json.dumps(r.get("origin"))[:40] if r.get("origin") else None, bool(r.get("isSidechain")))
    c[k] += 1
for k, v in c.most_common(25): print(v, k)
