# Counts assistant records per message.model in each PI main-thread transcript (read only), to state which PI model produced waves 1-8; prints label, model, count.
# usage: python3 -I w09k_models.py <label>=<transcript.jsonl> [...]
import sys, json, collections
for a in sys.argv[1:]:
    label, path = a.split("=", 1)
    c = collections.Counter()
    for l in open(path, encoding="utf-8", errors="replace"):
        if '"model"' in l:
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if d.get("type") == "assistant" and isinstance(d.get("message"), dict):
                c[d["message"].get("model")] += 1
    for m, n in sorted(c.items(), key=lambda x: -x[1]):
        print(label, m, n)
