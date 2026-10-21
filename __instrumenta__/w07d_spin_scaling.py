"""Shows where this machine's performance cores end: W forked processes each run the same fixed integer loop; prints the slowest and median per-process time and the aggregate throughput (W*work/wall) for W = 1..12, from nothing to a table on stdout.

usage: w07d_spin_scaling.py [reps]
Work per process: sum(i*i for i in range(1_500_000)) twice (about 0.15 s on one P core). Processes start together on a barrier-free fork; start cost is excluded (each reports its own time around the loop). The machine is shared with other agents: the load average is printed per W.
"""
import os, sys, time, statistics, multiprocessing as mp
def work(_):
    t = time.perf_counter()
    s = 0
    for _ in range(2):
        s += sum(i * i for i in range(1_500_000))
    return time.perf_counter() - t
if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    base = None
    ctx = mp.get_context("fork")
    print("W  per-proc median  per-proc max   wall(incl. fork)  aggregate throughput (rel. to 1 proc)  load1")
    for W in range(1, 13):
        med, mx, wall = [], [], []
        for _ in range(reps):
            t = time.perf_counter()
            with ctx.Pool(W) as pool:
                ts = pool.map(work, range(W), chunksize=1)
            wall.append(time.perf_counter() - t); med.append(statistics.median(ts)); mx.append(max(ts))
        m = statistics.median(med)
        if base is None: base = m
        print("%-2d %.3f           %.3f          %.3f             %.2f                                   %.1f" % (W, m, statistics.median(mx), statistics.median(wall), W * base / statistics.median(mx), os.getloadavg()[0]))
