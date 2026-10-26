# Counts what the PI read before its first Agent dispatch (the orientation stretch), per session, from <dir>/<label>_turns.jsonl written by w09d_turns.py; writes <dir>/orientation_table.tsv and prints it.
# usage: python3 -I w09d_orient.py <dir> <label> [...]
import json, sys, os, re, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w09d_turns import obj_class
d = sys.argv[1]
out = []
for lab in sys.argv[2:]:
    steps = []
    for l in open(os.path.join(d, lab + "_turns.jsonl")):
        t = json.loads(l)
        steps += [(t["n"], s) for s in t["steps"]]
    # first dispatch
    idx = next((i for i, (_, s) in enumerate(steps) if any(c["kind"] == "dispatch" for c in s["calls"])), len(steps))
    pre = steps[: idx + 1]   # includes the dispatching step
    t0 = steps[0][1]["t"]; t1 = pre[-1][1]["t"]
    reads = []
    for _, s in pre:
        for c in s["calls"]:
            if c["kind"] in ("read-whole", "read-part", "bash-view", "bash-query", "lab_status", "git", "search") or c.get("reads_too"):
                reads.append(c)
    chars = sum(c["res_chars"] or 0 for c in reads)
    byclass = collections.Counter()
    for c in reads:
        cl = obj_class(c["paths"][0]) if c["paths"] else c["kind"]
        byclass[cl] += c["res_chars"] or 0
    ntext = sum(1 for _, s in pre if s["text"])
    out.append([lab, len(pre), len(reads), chars, int(t1 - t0), ntext, "; ".join("%s %d" % kv for kv in byclass.most_common(5))])
cols = ["label", "steps_to_first_dispatch", "reads", "chars_read", "secs", "steps_with_text", "top_classes_by_chars"]
with open(os.path.join(d, "orientation_table.tsv"), "w") as f:
    f.write("\t".join(cols) + "\n")
    for r in out:
        f.write("\t".join(str(x) for x in r) + "\n")
        print(r)
