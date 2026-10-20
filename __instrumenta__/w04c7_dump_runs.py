# prints, per run folder under a run root, every tool call (name, input head) with the character length of its result, the result record's cost, and the files added or changed in the run's lab __instrumenta__ relative to a scripts folder; input: RUNROOT SCRIPTS ids; output: text on stdout (independent of the author's e3_measure.py)
import json, os, sys, hashlib
root, scripts = sys.argv[1], sys.argv[2]
ids = sys.argv[3:]
def h(p): return hashlib.md5(open(p,'rb').read()).hexdigest()
for rid in ids:
    print("=====", rid)
    calls = []; res = {}; cost = None
    for line in open(os.path.join(root, rid, "run.jsonl")):
        try: r = json.loads(line)
        except ValueError: continue
        if r.get("type") == "result": cost = r.get("total_cost_usd")
        c = (r.get("message") or {}).get("content")
        if not isinstance(c, list): continue
        for b in c:
            if r["type"] == "assistant" and b.get("type") == "tool_use":
                calls.append((b["id"], b["name"], b["input"]))
            if r["type"] == "user" and b.get("type") == "tool_result":
                x = b.get("content")
                res[b["tool_use_id"]] = (len(x) if isinstance(x, str) else sum(len(y.get("text","")) for y in x if isinstance(y, dict)), bool(b.get("is_error")))
    for i, (cid, n, inp) in enumerate(calls):
        s = json.dumps(inp)
        print(i, n.replace("mcp__plugin_colgrep-mcp_colgrep__","colgrep."), s[:260].replace("\\n"," ; "), "->", res.get(cid))
    li = os.path.join(root, rid, "lab", "__instrumenta__")
    now = set(f for f in os.listdir(li) if os.path.isfile(os.path.join(li, f)))
    st = set(os.listdir(scripts))
    print("new:", sorted(now-st), "removed:", sorted(st-now))
    print("modified:", sorted(f for f in st & now if h(os.path.join(li,f)) != h(os.path.join(scripts,f))))
    print("cost", cost)
