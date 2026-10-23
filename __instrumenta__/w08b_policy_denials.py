# Counts, per wave, the Bash calls that tried a denied corpus search (recursive grep, rg, find -exec grep, xargs grep) or used COLGREP_BYPASS, whether the call errored, and which tool the worker used next; inputs: w08b_calls.py OUT.tsv + OUT.private.jsonl; output: printed table (no raw text). Usage: python3 -I w08b_policy_denials.py OUT_PREFIX
import csv, json, os, re, sys, collections
pre = sys.argv[1]
R = list(csv.DictReader(open(pre + ".tsv"), delimiter="\t"))
P = [json.loads(l) for l in open(pre + ".private.jsonl")]
cmd = {(p["w"], p["a"], p["seq"]): p["cmd"] for p in P if "cmd" in p}
byk = collections.defaultdict(list)
for r in R:
    byk[(r["wave"], r["agent"])].append(r)
DEN = re.compile(r"(\bgrep\s+(-\w*[rR]\w*|--recursive)\b|\brg\b|find\b.*-exec\s+grep|xargs\s+grep)")
tab = collections.Counter()
nxt = collections.Counter()
for k, calls in byk.items():
    calls.sort(key=lambda r: int(r["seq"]))
    for i, c in enumerate(calls):
        if not c["class"].startswith("bash_"):
            continue
        cm = cmd.get((k[0], k[1], int(c["seq"])), "")
        byp = "COLGREP_BYPASS" in cm
        den = bool(DEN.search(cm))
        if den or byp:
            tab[(k[0], "denied-form" if den else "bypass", "error" if c["error"] == "1" else "ok")] += 1
            if i + 1 < len(calls):
                nxt[calls[i + 1]["class"]] += 1
for k in sorted(tab):
    print(k, tab[k])
print("next call after a denied-form/bypass call:", nxt.most_common(12))
