"""Times creating and closing a multiprocessing.Pool(W) that does one trivial task per worker, with the fork and the spawn start method (macOS's default is spawn), for W = 1, 2, 4, 6, 8, 12; median of 5 in seconds, to stdout.

usage: w07d_pool_start.py   (a process with lab_status imported, as the script would have it, is the parent)
"""
import os, sys, time, statistics, multiprocessing as mp
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
import lab_status  # noqa: F401  (spawn re-imports __main__ only; fork carries this module's state)
def nop(x): return x
if __name__ == "__main__":
    print("W   fork pool (ms)   spawn pool (ms)   load1 %.1f" % os.getloadavg()[0])
    for W in (1, 2, 4, 6, 8, 12):
        out = []
        for method in ("fork", "spawn"):
            ts = []
            for _ in range(5):
                t = time.perf_counter()
                with mp.get_context(method).Pool(W) as p: p.map(nop, range(W), chunksize=1)
                ts.append(time.perf_counter() - t)
            out.append(statistics.median(ts) * 1e3)
        print("%-3d %8.1f         %8.1f" % (W, out[0], out[1]))
