# Tabulates, over every text user record of the given transcripts (default: the lab population), the record's origin fields (origin.kind, promptSource, turnOrigin, entrypoint, isMeta, userType, version-major) with counts, plus which top-level keys differ between the groups; inputs: transcript paths (or none for the population); output: stdout tables.
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w07c2_population import population
paths = sys.argv[1:] or population()
tab = collections.Counter(); keys = collections.defaultdict(collections.Counter); ex = {}
for path in paths:
    for line in open(path, errors="replace"):
        if '"type":"user"' not in line.replace('": "', '":"'): continue
        try: d = json.loads(line)
        except ValueError: continue
        if d.get("type") != "user" or "toolUseResult" in d or d.get("sourceToolAssistantUUID"): continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list): c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        if not isinstance(c, str) or not c.strip(): continue
        o = d.get("origin"); ok = o.get("kind") if isinstance(o, dict) else (None if o is None else repr(o))
        k = (ok, d.get("promptSource"), d.get("turnOrigin"), d.get("entrypoint"), d.get("isMeta"), d.get("userType"), bool(d.get("promptId")))
        tab[k] += 1; ex.setdefault(k, path.split("/")[-1][:8])
        for kk in d: keys[k][kk] += 1
print("(origin.kind, promptSource, turnOrigin, entrypoint, isMeta, userType, has promptId) -> n, example session")
for k, n in tab.most_common(): print(n, k, ex[k])
print("\nkeys present in every record of a group, and keys present in only some (n/total)")
for k, n in tab.most_common():
    print(k, n); print("   always:", sorted(x for x, m in keys[k].items() if m == n)); print("   some:", sorted((x, m) for x, m in keys[k].items() if m != n))
