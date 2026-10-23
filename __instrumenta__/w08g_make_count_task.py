# Builds the w08-g read-only task: from a seed and an output folder S to S/task (claim.md with a table of claimed row counts for N shard files, shard_1..N.csv), S/truth.json (the shards whose claimed count is wrong) and S/plug (agents vf-base and vf-lever1, tools Read, Glob, Grep only, differing in one added line).
# usage: w08g_make_count_task.py S [seed] [nshards=8]   (the claim names the files; no shell tool, so each file takes one Read call and the reads are independent of each other)
import os, sys, json, random
S = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 5; NS = int(sys.argv[3]) if len(sys.argv) > 3 else 8
rnd = random.Random(seed); os.makedirs(os.path.join(S, "task"), exist_ok=True)
counts = []; claimed = []
for i in range(1, NS + 1):
    n = rnd.randint(9, 16); counts.append(n)
    with open(os.path.join(S, "task", "shard_%d.csv" % i), "w") as f:
        f.write("order_id,sku,qty\n")
        for r in range(n): f.write("%d,%s,%d\n" % (1000 * i + r, rnd.choice("ABCDEFGH") + str(rnd.randint(1, 9)), rnd.randint(1, 9)))
    claimed.append(n)
wrong = sorted(rnd.sample(range(1, NS + 1), 2))
for w in wrong: claimed[w - 1] += rnd.choice([-1, 1, 2])
with open(os.path.join(S, "task", "claim.md"), "w") as f:
    f.write("# c1: the data rows (header excluded) of shard_1.csv .. shard_%d.csv are as follows.\n\nlabel: MEASURED\nscope: the shard files named below\n\n| file | claimed data rows |\n|:--|--:|\n" % NS)
    for i in range(1, NS + 1): f.write("| shard_%d.csv | %d |\n" % (i, claimed[i - 1]))
json.dump({"wrong": ["shard_%d.csv" % w for w in wrong], "true_counts": counts}, open(os.path.join(S, "truth.json"), "w"))
body = ("You verify an empirical claim, independently. Work in the current folder. The claim is in claim.md and names the data files it rests on. Count the data rows of every file yourself. "
        "Finish with exactly two lines: `wrong_files: <comma-separated file names whose claimed count is wrong, or none>` and `verdict: <SUPPORTED|OVERSTATED|UNSUPPORTED>`.")
lev = {"base": "", "lever1": "\n\nWhen several tool calls do not depend on each other, send them together in one message.\n"}
os.makedirs(os.path.join(S, "plug", ".claude-plugin"), exist_ok=True); os.makedirs(os.path.join(S, "plug", "agents"), exist_ok=True)
json.dump({"name": "w08g", "version": "0.0.1", "description": "test agents for batching line"}, open(os.path.join(S, "plug", ".claude-plugin", "plugin.json"), "w"))
for k, v in lev.items():
    open(os.path.join(S, "plug", "agents", "vf-%s.md" % k), "w").write("---\nname: vf-%s\ndescription: test verifier\nmodel: sonnet\ntools: Read, Glob, Grep\n---\n\n%s%s" % (k, body, v))
print(json.load(open(os.path.join(S, "truth.json")))["wrong"])
