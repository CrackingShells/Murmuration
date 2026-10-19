import json, collections, sys
c = collections.Counter(); ex = {}
for l in open(sys.argv[1]):
    try: r = json.loads(l)
    except Exception: continue
    if r.get("type") == "attachment":
        a = r.get("attachment", {})
        k = ("att", a.get("type"), a.get("commandMode"), tuple(sorted(a.keys())))
        c[k] += 1
    elif r.get("type") == "user":
        m = r.get("message", {}); cont = m.get("content")
        k = ("user", "str" if isinstance(cont, str) else "list:" + ",".join(sorted({b.get("type", "?") for b in cont if isinstance(b, dict)})), r.get("isMeta"), json.dumps(r.get("origin"))[:30] if r.get("origin") else None, r.get("turnOrigin"), "sourceToolUseID" in r or "toolUseResult" in r)
        c[k] += 1
for k, v in c.most_common(40): print(v, k)
