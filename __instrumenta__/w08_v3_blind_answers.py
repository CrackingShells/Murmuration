# Prints the final answer of each named run (stream.jsonl 'result' record) under a shuffled blind code, with its truth.json key facts, and writes the code->run key to a file; inputs: RUNS_DIR KEYFILE NAME...; output: stdout and KEYFILE.
import json, os, random, sys
RD, KEY, names = sys.argv[1], sys.argv[2], sys.argv[3:]
random.Random(20261024).shuffle(names)
key = {}
for i, n in enumerate(names):
    code = "X%02d" % i; key[code] = n
    t = json.load(open(os.path.join(RD, n, "truth.json")))
    fin = ""
    for l in open(os.path.join(RD, n, "stream.jsonl")):
        try: d = json.loads(l)
        except ValueError: continue
        if d.get("type") == "result": fin = d.get("result") or fin
    print("=" * 8, code, "seed", t["seed"], "| in flight:", t["in_flight"], "| sentence:", t["sentence"][:50] + "...", "| q5:", t["q5"], "| labels", t["labels"], "| next:", t["next_action"])
    print(fin.strip()[:2500]); print()
json.dump(key, open(KEY, "w"), indent=1)
