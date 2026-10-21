# prints, for each E3 run folder, the tool calls of the stream-json transcript in order (name, first 300 chars of input, error flag, result length), the final cost, and a tree diff of __instrumenta__/ against the starting commit; input: run root and run ids; output: text on stdout (independent re-reading for verifying w04-c4)
import json, sys, os, subprocess
root = sys.argv[1]
W = int(os.environ.get("W", "300"))
for rid in sys.argv[2:]:
    d = os.path.join(root, "runs", rid)
    calls = {}; order = []; cost = None
    for l in open(os.path.join(d, "run.jsonl")):
        try: e = json.loads(l)
        except Exception: continue
        t = e.get("type")
        if t == "assistant":
            for c in e["message"]["content"]:
                if c.get("type") == "tool_use":
                    calls[c["id"]] = {"name": c["name"], "input": json.dumps(c["input"])[:W], "sub": e.get("parent_tool_use_id") is not None}
                    order.append(c["id"])
        elif t == "user":
            m = e["message"]["content"]
            if isinstance(m, list):
                for c in m:
                    if c.get("type") == "tool_result" and c["tool_use_id"] in calls:
                        cc = c.get("content"); n = len(cc) if isinstance(cc, str) else len(json.dumps(cc))
                        calls[c["tool_use_id"]]["err"] = bool(c.get("is_error")); calls[c["tool_use_id"]]["len"] = n
        elif t == "result":
            cost = e.get("total_cost_usd")
    print("=====", rid, "cost", cost)
    for i, k in enumerate(order, 1):
        c = calls[k]
        print(f" {i:2d} {'[sub] ' if c['sub'] else ''}{c['name']} err={c.get('err')} len={c.get('len')} {c['input']}")
    lab = os.path.join(d, "lab")
    r = subprocess.run(["git", "-C", lab, "diff", "--stat", "--name-status", "44b042e", "HEAD"], capture_output=True, text=True)
    print(" diff vs start commit:\n" + "\n".join("   " + x for x in r.stdout.splitlines()))
    r = subprocess.run(["git", "-C", lab, "status", "--short"], capture_output=True, text=True)
    print(" uncommitted:", r.stdout.replace("\n", " | ")[:300])
