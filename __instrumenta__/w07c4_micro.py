"""Times git_worktrees of two copies of lab_status.py in process on one folder, from the two script paths and the folder to median / min / max milliseconds on stdout (the cost the o4 pairs are meant to remove).

usage: w07c4_micro.py A.py B.py ROOT [N=200]
"""
import importlib.util
import os
import statistics
import sys
import time


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


a, b, root = sys.argv[1:4]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 200
mods = {"A": load(a, "A"), "B": load(b, "B")}
res = {"A": [], "B": []}
for i in range(n):
    for k in ("A", "B") if i % 2 == 0 else ("B", "A"):
        t = time.perf_counter()
        out = mods[k].git_worktrees(root)
        res[k].append((time.perf_counter() - t) * 1e3)
print("worktrees listed: %d; equal: %s; load1 %.2f" % (len(out), mods["A"].git_worktrees(root) == mods["B"].git_worktrees(root), os.getloadavg()[0]))
for k in "AB":
    print("%s: median %.2f ms, min %.2f, max %.2f (n=%d)" % (k, statistics.median(res[k]), min(res[k]), max(res[k]), n))
