# Builds the w08-g test task and test plugin: from a seed and an output folder S to S/task (claim.md, prices.md, shard_1..6.csv), S/truth.json and S/plug (agents vf-base, vf-lever1, vf-lever2 that differ only in one added line).
# usage: w08g_make_task.py S [seed] [nshards=6] [named_in=agent|claim]   (named_in=claim: the agent file does not list the files; claim.md does, so the reads depend on reading claim.md first and are independent of each other after it)
# (old usage line follows)
# usage: w08g_make_task.py S [seed]   (verifier-like task with 8 independent files named in the brief; truth: dedup by order_id, price table with one override row)
import os, sys, json, random
S = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 9; NS = int(sys.argv[3]) if len(sys.argv) > 3 else 6; NAMED = sys.argv[4] if len(sys.argv) > 4 else 'agent'
rnd = random.Random(seed)
os.makedirs(os.path.join(S, "task"), exist_ok=True)
skus = ["A1", "B2", "C3", "D4", "E5", "F6", "G7", "H8"]
price = {s: round(rnd.uniform(1.0, 9.0), 2) for s in skus}
oid = 1000; shards = []
for i in range(NS):
    rows = []
    for _ in range(14):
        oid += 1; rows.append((oid, rnd.choice(skus), rnd.randint(1, 9)))
    shards.append(rows)
# planted: two orders of shard 2 reappear in shard 5 (same order_id, same content): count once
dup = shards[1][3:5]
shards[NS - 2][2:2] = dup
seen = set(); total = 0.0; naive = 0.0
for rows in shards:
    for (o, s, q) in rows:
        naive += price[s] * q
        if o in seen: continue
        seen.add(o); total += price[s] * q
for i, rows in enumerate(shards, 1):
    with open(os.path.join(S, "task", "shard_%d.csv" % i), "w") as f:
        f.write("order_id,sku,qty\n")
        for (o, s, q) in rows: f.write("%d,%s,%d\n" % (o, s, q))
with open(os.path.join(S, "task", "prices.md"), "w") as f:
    f.write("# Price table (USD per unit)\n\n| sku | price |\n|:--|--:|\n")
    for s in skus: f.write("| %s | %.2f |\n" % (s, price[s]))
    f.write("\nAn order_id is one order: if it appears in two shards it is the same order and counts once.\n")
with open(os.path.join(S, "task", "claim.md"), "w") as f:
    f.write("# c1: total revenue over shard_1.csv .. shard_%d.csv is USD %.2f.\n\nlabel: MEASURED\nscope: the shard files named in the title and prices.md\nmethod: sum of qty x price over every row of every shard.\n" % (NS, naive))
json.dump({"true_total": round(total, 2), "claimed": round(naive, 2)}, open(os.path.join(S, "truth.json"), "w"))
body = ("You verify an empirical claim, independently. Work in the current folder. " + ("The files are claim.md, prices.md and shard_1.csv .. shard_%d.csv. " % NS if NAMED == "agent" else "The claim is in claim.md and names the data files it rests on. ") +
        "Check the claim yourself from the shards and the price table, not by trusting the claim's method. "
        "Finish with exactly two lines: `recomputed_total_usd: <number with 2 decimals>` and `verdict: <SUPPORTED|OVERSTATED|UNSUPPORTED>`, preceded by at most three lines of reason.")
lev = {"base": "", "lever1": "\n\nWhen several tool calls do not depend on each other, send them together in one message.\n",
       "lever2": "\n\nWhen the files you need are named in your task, read all of them in one message (several tool calls together), not one per message.\n"}
os.makedirs(os.path.join(S, "plug", ".claude-plugin"), exist_ok=True); os.makedirs(os.path.join(S, "plug", "agents"), exist_ok=True)
json.dump({"name": "w08g", "version": "0.0.1", "description": "test agents for batching line"}, open(os.path.join(S, "plug", ".claude-plugin", "plugin.json"), "w"))
for k, v in lev.items():
    open(os.path.join(S, "plug", "agents", "vf-%s.md" % k), "w").write("---\nname: vf-%s\ndescription: test verifier\nmodel: sonnet\ntools: Read, Glob, Grep, Bash\n---\n\n%s%s" % (k, body, v))
print(json.load(open(os.path.join(S, "truth.json"))))
