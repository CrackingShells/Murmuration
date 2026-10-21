"""Times alternating calls of two lab_status.py copies on one lab checkout with the DEFAULT cache path (no LAB_STATUS_CACHE), from the two script paths and a lab root to one line per call, the cache files present after each call, and medians on stdout (does a version-named cache file stop the thrash of w07c4_cache_thrash.py).

usage: w07c4_cache_thrash_default.py A.py B.py LAB_ROOT [ROUNDS=6]
Sequence as in w07c4_cache_thrash.py. The cache files are those of `<LAB_ROOT>/__statera__/.harness/lab_status_cache*.json`; they are the lab's own (git-ignored) files, A's name is lab_status_cache.json, B's lab_status_cache.v2.json. Unsets LAB_STATUS_CACHE for the children.
"""
import glob
import os
import statistics
import subprocess
import sys
import time


def run(script, root):
    env = {k: v for k, v in os.environ.items() if k != "LAB_STATUS_CACHE"}
    t = time.perf_counter()
    p = subprocess.run([sys.executable, "-I", script, "--spend", "--project", root], capture_output=True, text=True, env=env)
    assert p.returncode == 0 and p.stdout.startswith("## Spend"), p.stderr[:200]
    return time.perf_counter() - t, len(p.stdout)


def main(a, b, root, rounds="6"):
    rounds = int(rounds)
    script = {"A": a, "B": b}
    seq = ["A", "A", "B", "B"] + ["A", "B"] * rounds + ["A", "A", "B", "B"]
    times = []
    for i, k in enumerate(seq):
        w, n = run(script[k], root)
        files = sorted(os.path.basename(f) for f in glob.glob(os.path.join(root, "__statera__", ".harness", "lab_status_cache*.json")))
        times.append((i, k, w))
        print("%2d %s %.3f s  output %d bytes  cache files: %s" % (i, k, w, n, ", ".join(files)))
    alt = [w for i, k, w in times if 4 <= i < 4 + 2 * rounds]
    print("alternating phase: median %.3f s (n=%d), max %.3f s; load1 %.2f" % (statistics.median(alt), len(alt), max(alt), os.getloadavg()[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
