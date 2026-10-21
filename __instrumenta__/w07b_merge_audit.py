# Prints a seeded random sample of the turn pairs that w07b_loop_tables.py counted as mergeable (merges.tsv, loose mode) with the commands or paths of both turns, so a person can judge if the second call needed the first one's result; inputs: merges.tsv, the three session roots; output: stdout (or a file by redirect). Usage: w07b_merge_audit.py MERGES_TSV N SEED ROOT [ROOT ...]  (ROOT = main transcript .jsonl; workers read from its subagents folder)
import sys, os, glob, json, random, re
tsv, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
roots = sys.argv[4:]
files = {}
for r in roots:
    for f in glob.glob(r[:-6] + "/subagents/agent-*.jsonl"):
        files[os.path.basename(f)[6:-6]] = f
rows = [l.rstrip("\n").split("\t") for l in open(tsv)][1:]
random.seed(seed)
sample = random.sample(rows, min(n, len(rows)))
SCRUB = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|[A-Za-z0-9_-]{32,}|(?i:api[_-]?key|token|secret)\S*)")
def head(name, inp):
    t = inp.get("command") if name == "Bash" else " ".join(str(inp.get(k)) for k in ("file_path", "path", "pattern", "query") if inp.get(k)) or json.dumps(inp)
    return SCRUB.sub("<scrubbed>", (t or "").replace("\n", " "))[:170]
cache = {}
def turns(agent):
    if agent in cache:
        return cache[agent]
    order, msgs = [], {}
    for l in open(files[agent], errors="replace"):
        if '"type": "assistant"' not in l[:60] and '"assistant"' not in l[:400]:
            continue
        try: r = json.loads(l)
        except ValueError: continue
        if r.get("type") != "assistant": continue
        m = r["message"]
        if m.get("model") == "<synthetic>": continue
        if m["id"] not in msgs:
            msgs[m["id"]] = []; order.append(m["id"])
        for b in m.get("content") or []:
            if b.get("type") == "tool_use":
                msgs[m["id"]].append((b["name"], b.get("input") or {}))
    cache[agent] = [msgs[i] for i in order]
    return cache[agent]
for r in sorted(sample, key=lambda r: (r[0], r[1], int(r[3]))):
    lab, ag, name, j = r[0], r[1], r[2], int(r[3])
    T = turns(ag)
    print("--- %s %s turn %d (strict=%s)" % (lab, name, j, r[8]))
    for k in (j - 1, j):
        for nm, inp in T[k]:
            print("  %s %s: %s" % ("prev" if k == j - 1 else "NEXT", nm, head(nm, inp)))
