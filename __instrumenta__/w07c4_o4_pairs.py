"""Times interleaved pairs of warm `lab_status.py --spend` calls of two copies (A, B) on the live tree, from the two script paths and a lab root to JSON lines per call, a per-pair table and the sign / median summary of protocol P4 o4 on stdout.

usage: w07c4_o4_pairs.py A.py B.py LAB_ROOT OUT.jsonl [--pairs 30] [--seed 1]
Each variant has its own cache file (LAB_STATUS_CACHE under a scratch folder) and is called once, unmeasured, before the pairs, so that the cache is warm. Inside a pair the order A,B or B,A is drawn from a seeded generator. Wall time is taken around the child process (perf_counter), CPU time from the children's rusage, the 1-minute load average just before the pair.
Rule (registered): B faster in at least 20 of 30 pairs. Reports the median per-pair saving (A - B), its quartiles, min and max, and the one-sided binomial p-value of the count under p = 0.5.
"""
import json
import math
import os
import random
import resource
import statistics
import subprocess
import sys
import tempfile
import time


def call(script, root, cache):
    env = dict(os.environ, LAB_STATUS_CACHE=cache)
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t = time.perf_counter()
    p = subprocess.run([sys.executable, "-I", script, "--spend", "--project", root], capture_output=True, text=True, env=env)
    wall = time.perf_counter() - t
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    assert p.returncode == 0 and p.stdout.startswith("## Spend"), (p.returncode, p.stderr[:200], p.stdout[:200])
    return wall, (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime), len(p.stdout)


def main(a, b, root, out, *rest):
    pairs = int(rest[rest.index("--pairs") + 1]) if "--pairs" in rest else 30
    seed = int(rest[rest.index("--seed") + 1]) if "--seed" in rest else 1
    rng = random.Random(seed)
    scratch = tempfile.mkdtemp(prefix="w07c4-o4-")
    caches = {"A": os.path.join(scratch, "A.json"), "B": os.path.join(scratch, "B.json")}
    scripts = {"A": a, "B": b}
    for k in "AB":
        call(scripts[k], root, caches[k])   # cold, unmeasured
    for k in "AB":
        call(scripts[k], root, caches[k])   # warm, unmeasured
    rows = []
    with open(out, "w") as fh:
        for i in range(pairs):
            order = ["A", "B"] if rng.random() < 0.5 else ["B", "A"]
            load = os.getloadavg()[0]
            rec = {"pair": i, "order": "".join(order), "load1": round(load, 2)}
            for k in order:
                w, c, n = call(scripts[k], root, caches[k])
                rec[k + "_wall"], rec[k + "_cpu"], rec[k + "_bytes"] = round(w, 4), round(c, 4), n
            fh.write(json.dumps(rec) + "\n")
            rows.append(rec)
    saving = [r["A_wall"] - r["B_wall"] for r in rows]
    faster = sum(s > 0 for s in saving)
    p = sum(math.comb(pairs, j) for j in range(faster, pairs + 1)) / 2 ** pairs
    q = statistics.quantiles(saving, n=4) if len(saving) > 1 else [0, 0, 0]
    print("pair order load1  A_wall  B_wall  saving(A-B)  A_cpu  B_cpu")
    for r, s in zip(rows, saving):
        print("%4d %5s %5.2f  %.3f   %.3f   %+.3f       %.2f   %.2f" % (r["pair"], r["order"], r["load1"], r["A_wall"], r["B_wall"], s, r["A_cpu"], r["B_cpu"]))
    print("pairs %d, seed %d: B faster in %d of %d (one-sided p under no saving %.2g); rule needs >= %d of 30" % (pairs, seed, faster, pairs, p, 20))
    print("A wall median %.3f (min %.3f max %.3f); B wall median %.3f (min %.3f max %.3f)" % (
        statistics.median(r["A_wall"] for r in rows), min(r["A_wall"] for r in rows), max(r["A_wall"] for r in rows),
        statistics.median(r["B_wall"] for r in rows), min(r["B_wall"] for r in rows), max(r["B_wall"] for r in rows)))
    print("per-pair saving: median %.3f, quartiles %.3f / %.3f, min %.3f, max %.3f" % (statistics.median(saving), q[0], q[2], min(saving), max(saving)))
    print("CPU median A %.3f B %.3f; load1 over the batch %.2f to %.2f (median %.2f); bytes of output equal in all pairs: %s" % (
        statistics.median(r["A_cpu"] for r in rows), statistics.median(r["B_cpu"] for r in rows),
        min(r["load1"] for r in rows), max(r["load1"] for r in rows), statistics.median(r["load1"] for r in rows),
        all(abs(r["A_bytes"] - r["B_bytes"]) < 200 for r in rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
