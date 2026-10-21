# For each entry of a lab's user_words.md, finds the transcript user record(s) whose text contains the entry's first 50 characters and prints their (promptSource, turnOrigin, origin.kind); inputs: user_words.md path, transcript JSONL paths; output: stdout table, one row per entry.
import json, re, sys
words, files = sys.argv[1], sys.argv[2:]
text = open(words, encoding="utf-8").read()
parts = re.split(r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2})\n", text, flags=re.M)
entries = [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts) - 1, 2)]
keys = {}
for i, (when, body) in enumerate(entries):
    k = re.sub(r"\s+", " ", body)[:50]
    keys[i] = k
hits = {i: set() for i in keys}
for p in files:
    for line in open(p, errors="replace"):
        if '"type":"user"' not in line.replace('": ', '":') : continue
        try: d = json.loads(line)
        except ValueError: continue
        if d.get("type") != "user" or "toolUseResult" in d: continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list): c = " ".join(b.get("text", "") for b in c if isinstance(b, dict))
        if not isinstance(c, str): continue
        flat = re.sub(r"\s+", " ", c)
        o = d.get("origin"); ok = o.get("kind") if isinstance(o, dict) else o
        for i, k in keys.items():
            if k and k in flat: hits[i].add((d.get("promptSource"), d.get("turnOrigin"), ok, p.split("/")[-1][:8]))
for i, (when, body) in enumerate(entries):
    print(when, "|", keys[i][:50].ljust(50), "|", sorted(hits[i]) or "no transcript record found")
