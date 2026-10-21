"""For dumps of w05c4_replay_batched.py --merged --dump DIR, classifies each differing transcript: answers equal once the clock (event time and the 'X of Y min (Z%)' figure) is ignored, or not; and whether log, hand-back files and state are equal.

Input: argv[1] = DIR with <transcript>.old.json / .new.json. Output: one line per transcript that differs in any way, then a count by class.
"""
import json, os, re, sys, collections
d = sys.argv[1]
names = sorted({f.rsplit(".", 2)[0] for f in os.listdir(d) if f.endswith(".old.json")})
TIME = re.compile(r"[\d.]+ of [\d.]+ min \(\d+%\)")
def strip(ans):
    return [[sc, TIME.sub("T", json.dumps(a, sort_keys=True))] for sc, now, a in ans]
cls = collections.Counter()
for n in names:
    o = json.load(open(os.path.join(d, n + ".old.json")))
    w = json.load(open(os.path.join(d, n + ".new.json")))
    exact = o["answers"] == w["answers"]
    mod = strip(o["answers"]) == strip(w["answers"])
    flags = dict(answers_exact=exact, answers_mod_clock=mod, log=o["log"] == w["log"], handbacks=o["handbacks"] == w["handbacks"], state=o["state"] == w["state"])
    if all(flags.values()):
        cls["equal"] += 1
        continue
    key = ",".join(k for k, v in flags.items() if not v)
    cls[key] += 1
    extra = ""
    if not mod:
        so, sw = strip(o["answers"]), strip(w["answers"])
        extra = " n_old=%d n_new=%d" % (len(so), len(sw))
    print(n, key, extra)
print(dict(cls))
