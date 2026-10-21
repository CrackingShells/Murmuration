# Independent check of the user_words origin rule: from every user record in ~/.claude/projects (argv[2:] or all) and the user's words files (argv[1] glob list, comma-separated), computes (a) the record-field categories with my own classifier (no import of the author's), (b) for each field-category what the script under test (argv path in env UW) decides by human_prompt on a replayed transcript prefix, and (c) which entries of the user's words files (typed prompts as recorded) the new rule would drop; output: stdout tables.
import json, os, sys, glob, re, collections, importlib.util
uw_path = os.environ["UW"]
spec = importlib.util.spec_from_file_location("uw", uw_path); uw = importlib.util.module_from_spec(spec); spec.loader.exec_module(uw)
files = sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")))
def text_of(d):
    c = d.get("message", {}).get("content")
    if isinstance(c, str): return c
    if isinstance(c, list): return "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return ""
def cat(d):
    o = d.get("origin"); k = o.get("kind") if isinstance(o, dict) else None
    if k: return "origin:" + k
    return "none:%s/%s/%s" % (d.get("promptSource"), d.get("turnOrigin"), d.get("entrypoint"))
cnt = collections.Counter(); verdict = collections.Counter(); by_text = collections.defaultdict(list)
for f in files:
    try: lines = open(f, errors="replace").read().splitlines()
    except OSError: continue
    for i, l in enumerate(lines):
        if '"type":"user"' not in l.replace(' ', ''): continue
        try: d = json.loads(l)
        except ValueError: continue
        if d.get("type") != "user" or "toolUseResult" in d or d.get("sourceToolAssistantUUID") or not d.get("promptId"): continue
        t = text_of(d)
        if not t.strip(): continue
        c = cat(d); m = uw.record_mark(d)
        cnt[c] += 1; verdict[(c, m)] += 1
        by_text[t].append((c, m, f))
print("categories (field values) and the script's record_mark verdict:")
for (c, m), n in sorted(verdict.items(), key=lambda x: -x[1]): print("%6d  %-45s %s" % (n, c, m))
# entries of the user's words files
ents = []
for p in sys.argv[1].split(","):
    s = open(p).read()
    for blk in re.split(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}\n\n", s, flags=re.M)[1:]: ents.append((p, blk.strip()))
print("\nuser words entries:", len(ents))
drop = []; nomatch = 0; allc = collections.Counter()
for p, e in ents:
    key = e[:50]
    hits = [h for k, v in by_text.items() if key in k for h in v]  # the entry's first 50 chars occur in the record's text
    if not hits: nomatch += 1; continue
    ms = [h[1] for h in hits]
    if True not in ms and None not in ms and False in ms: drop.append((p, e[:70], collections.Counter(h[0] for h in hits)))
    allc[tuple(sorted(set(str(m) for m in ms)))] += 1
print("entries with no transcript match by 40 chars:", nomatch)
print("entries whose every matching record is dropped by the origin rule: %d" % len(drop))
for p, e, c in drop: print("  ", os.path.basename(os.path.dirname(os.path.dirname(p))), repr(e), dict(c))

print('entries by set of marks of matching records:', dict(allc))
