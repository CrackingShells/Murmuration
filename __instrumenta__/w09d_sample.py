# Draws the stratified sample of turns to hand-code (seed 9), from <dir>/<label>_turns.jsonl written by w09d_turns.py; writes <dir>/sample.tsv (label, turn, stratum) and <dir>/batch_NN.txt (the turn summaries, about 20 turns a file, for reading).
# usage: python3 -I w09d_sample.py <dir>
import json, sys, os, random
d = sys.argv[1]
random.seed(9)
labs = ["w123", "w4", "w5", "w6", "w7", "w8"]
quota = {  # per label: orientation, human, B-H0, B-raw(H1/H1n), B-word(W), B-long, B-spread, N, X
    "w123": dict(O=1, H=2, H0=2, R=2, W=2, L=1, S=1, N=1, X=0),
    "w4": dict(O=1, H=2, H0=2, R=0, W=2, L=1, S=1, N=0, X=0),
    "w5": dict(O=1, H=3, H0=3, R=3, W=3, L=2, S=2, N=1, X=2),
    "w6": dict(O=1, H=4, H0=3, R=4, W=4, L=2, S=2, N=1, X=2),
    "w7": dict(O=1, H=4, H0=3, R=4, W=4, L=2, S=2, N=1, X=1),
    "w8": dict(O=1, H=3, H0=3, R=4, W=4, L=2, S=2, N=1, X=0),
}
chosen = []
for lab in labs:
    T = [json.loads(l) for l in open(os.path.join(d, lab + "_turns.jsonl"))]
    q = quota[lab]
    used = set()
    def pick(pool, k, tag):
        pool = [t for t in pool if t["n"] not in used]
        random.shuffle(pool)
        for t in pool[:k]:
            used.add(t["n"]); chosen.append((lab, t["n"], tag))
    # orientation: turn 0 (the session's first turn)
    used.add(T[0]["n"]); chosen.append((lab, T[0]["n"], "O"))
    B = [t for t in T if t["triggers"][0]["kind"] == "B"]
    pick([t for t in T if t["triggers"][0]["kind"] == "H" and t["n"] > 0], q["H"], "H")
    pick([t for t in B if "H0" in t["codes"]], q["H0"], "B-H0")
    pick([t for t in B if "H1" in t["codes"] or "H1n" in t["codes"]], q["R"], "B-raw")
    pick([t for t in B if "W" in t["codes"]], q["W"], "B-word")
    pick(sorted(B, key=lambda t: -len(t["steps"]))[:8], q["L"], "B-long")
    pick(B, q["S"], "B-spread")
    pick([t for t in T if t["triggers"][0]["kind"] == "N"], q["N"], "N")
    pick([t for t in T if t["triggers"][0]["kind"] == "X" and t["n"] > 0], q["X"], "X")
chosen.sort(key=lambda x: (labs.index(x[0]), x[1]))
with open(os.path.join(d, "sample.tsv"), "w") as f:
    f.write("label\tturn\tstratum\n")
    for c in chosen:
        f.write("%s\t%d\t%s\n" % c)
S = {}
for lab in labs:
    for l in open(os.path.join(d, lab + "_turns.jsonl")):
        t = json.loads(l); S[(lab, t["n"])] = t
buf, k, n = [], 0, 0
for lab, tn, tag in chosen:
    s = S[(lab, tn)]["summary"]
    cap = 3800 if tag == "O" else 1500
    buf.append("#%d [%s] %s" % (n, tag, s[:cap])); n += 1
    if len(buf) == 20:
        open(os.path.join(d, "batch_%02d.txt" % k), "w").write("\n\n".join(buf)); buf = []; k += 1
if buf:
    open(os.path.join(d, "batch_%02d.txt" % k), "w").write("\n\n".join(buf))
print(len(chosen), "turns,", k + 1, "batches")
