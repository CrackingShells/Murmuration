# Compares user_words.py's text rule (what it would store) with the transcript's own origin marker (origin.kind == "human") over every text user record of the given transcripts; inputs: transcript JSONL paths; output: a 2x2 count table plus up to 8 examples of each disagreement, to stdout.
import json, sys, re, collections, importlib.util, os
spec = importlib.util.spec_from_file_location("uw", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "user_words.py"))
uw = importlib.util.module_from_spec(spec); spec.loader.exec_module(uw)
def stored(prompt):
    p = uw.strip_leading(prompt)
    if not uw.is_genuine(p) or not p.strip() or uw.is_lab_command(p) or uw.is_bare_command(p): return False
    return bool(uw.unwrap_pasted(p).strip())
tab = collections.Counter(); ex = collections.defaultdict(list)
for path in sys.argv[1:]:
    for line in open(path, errors="replace"):
        try: d = json.loads(line)
        except ValueError: continue
        if d.get("type") != "user" or "toolUseResult" in d or d.get("sourceToolAssistantUUID"): continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list): c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        if not isinstance(c, str) or not c.strip(): continue
        if d.get("isMeta"): continue
        o = d.get("origin"); human = isinstance(o, dict) and o.get("kind") == "human"
        key = ("text rule stores" if stored(c) else "text rule skips", "origin human" if human else "origin not human")
        tab[key] += 1
        if len(ex[key]) < 8 and key[0] != "text rule skips" or (key == ("text rule skips", "origin human") and len(ex[key]) < 8):
            ex[key].append((path.split("/")[-1][:8], d.get("timestamp"), d.get("promptSource"), d.get("turnOrigin"), d.get("entrypoint"), re.sub(r"\s+", " ", uw.strip_leading(c))[:70]))
for k, n in sorted(tab.items()): print(n, k)
for k in (("text rule stores", "origin not human"), ("text rule skips", "origin human")):
    print("--", k)
    for e in ex[k]: print("  ", e)
