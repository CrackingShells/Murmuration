"""Checks that lab_status.py (new, with parse cache) prints byte-identical output to main's for cache off/cold/warm, and times the four cases interleaved, from two script paths, a frozen CLAUDE_CONFIG_DIR and a project folder to a table on stdout and a JSONL of runs.

usage: w05c5_repro_m1_m2.py OLD.py NEW.py CFG PROJECT SCRATCH [n=20] [out.jsonl]
Own code (does not import the author's instruments): cold = cache file removed before the timed start (not timed), unlike the author's `rm` inside the command.
"""
import os, random, statistics, subprocess, sys, time, json
old, new, cfg, proj, scr = sys.argv[1:6]
n = int(sys.argv[6]) if len(sys.argv) > 6 else 20
out = sys.argv[7] if len(sys.argv) > 7 else os.path.join(scr, "runs.jsonl")
os.makedirs(scr, exist_ok=True)
cf = os.path.join(scr, "c.json")
def run(script, cache, pre=None):
    if pre and os.path.exists(cf): os.unlink(cf)
    env = dict(os.environ, CLAUDE_CONFIG_DIR=cfg, LAB_STATUS_CACHE=cache)
    t = time.perf_counter(); r0 = os.times()
    p = subprocess.run([sys.executable, script, "--project", proj], capture_output=True, env=env)
    t = time.perf_counter() - t
    return p.stdout, p.returncode, t * 1000
# m1
ref, rc, _ = run(old, "off")
print("main bytes", len(ref), "rc", rc)
for name, cache, pre in (("new-off", "off", 0), ("new-cold", cf, 1), ("new-warm", cf, 0), ("new-warm2", cf, 0)):
    o, rc, _ = run(new, cache, pre)
    print("m1", name, len(o), rc, "IDENTICAL" if o == ref else "DIFFERS")
print("cache file bytes", os.path.getsize(cf))
# m2
cells = [("main", old, "off", 0), ("new-off", new, "off", 0), ("new-cold", new, cf, 1), ("new-warm", new, cf, 0)]
run(new, cf, 1)
for _ in range(2):
    for c in cells: run(c[1], c[2], c[3])
res = {c[0]: [] for c in cells}
rows = []
for i in range(n):
    random.shuffle(cells)
    for name, s, cache, pre in cells:
        o, rc, ms = run(s, cache, pre)
        res[name].append(ms); rows.append({"round": i, "case": name, "ms": ms, "rc": rc, "h": hash(o)})
json.dump(rows, open(out, "w"))
base = statistics.median(res["main"])
for k, v in res.items():
    v = sorted(v)
    print("%-9s median %7.1f  p90 %7.1f  min %7.1f  max %7.1f  vs main %+5.1f%%" % (k, statistics.median(v), v[int(0.9 * len(v)) - 1], v[0], v[-1], 100 * (statistics.median(v) / base - 1)))
# the live lab (puzzle files) changes under the run, so compare within a round, not against the first output
import collections
byr = collections.defaultdict(set)
for r in rows: byr[r["round"]].add(r["h"])
print("rounds in which the four outputs are identical: %d of %d" % (sum(len(v) == 1 for v in byr.values()), len(byr)), " nonzero rc:", sum(r["rc"] != 0 for r in rows))
