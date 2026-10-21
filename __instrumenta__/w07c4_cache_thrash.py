"""Times alternating calls of two lab_status.py copies (A = older, B = newer cache version) that share ONE cache file, from the two script paths and a lab root to one line per call and the medians on stdout (what an old and a new script do to each other's cache).

usage: w07c4_cache_thrash.py A.py B.py LAB_ROOT [ROUNDS=6]
Sequence: A A (A warm), B B (B reads A's file), then ROUNDS times A B alternately, then A A and B B again. Each call is a process, `--spend --project LAB_ROOT`, with LAB_STATUS_CACHE one scratch file; the cache version of each script is printed. Also prints whether the two outputs of the alternating phase agree in size (the live tree grows, so only size is compared) and the cache file's version after each call.
"""
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time


def run(script, root, cache):
    t = time.perf_counter()
    p = subprocess.run([sys.executable, "-I", script, "--spend", "--project", root], capture_output=True, text=True,
                       env=dict(os.environ, LAB_STATUS_CACHE=cache))
    assert p.returncode == 0 and p.stdout.startswith("## Spend"), p.stderr[:200]
    return time.perf_counter() - t, len(p.stdout)


def main(a, b, root, rounds="6"):
    cache = os.path.join(tempfile.mkdtemp(prefix="w07c4-thrash-"), "shared.json")
    for name, s in (("A", a), ("B", b)):
        print("%s: CACHE_VERSION %s" % (name, re.search(r"^CACHE_VERSION = (\d+)", open(s).read(), re.M).group(1)))
    seq = ["A", "A", "B", "B"] + ["A", "B"] * int(rounds) + ["A", "A", "B", "B"]
    script = {"A": a, "B": b}
    times = []
    for i, k in enumerate(seq):
        w, n = run(script[k], root, cache)
        v = json.load(open(cache)).get("v")
        times.append((i, k, w))
        print("%2d %s %.3f s  output %d bytes  cache file version after: %s" % (i, k, w, n, v))
    alt = [w for i, k, w in times if 4 <= i < 4 + 2 * int(rounds)]
    print("alternating phase: median %.3f s (n=%d); same-script repeat calls (positions 1, 3, last two pairs): %s" % (
        statistics.median(alt), len(alt), ", ".join("%.3f" % w for i, k, w in times if i in (1, 3, len(seq) - 3, len(seq) - 1))))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
