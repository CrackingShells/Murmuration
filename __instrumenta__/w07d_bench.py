"""Times shell commands with wall, user and sys CPU (wait4 rusage) and the load average, interleaving the cases round-robin, from `NAME=command` arguments to JSON lines on stdout (and a summary table on stderr).

usage: w07d_bench.py [--n N] NAME=CMD [NAME=CMD ...]
Each CMD runs through `sh -c` with stdout to /dev/null, stderr kept only on failure. Output rows: {name, i, wall, user, sys, load1, rc}. The summary gives min / median / max wall and median user+sys per name.
"""
import json, os, subprocess, sys, time, statistics

def run(cmd):
    t0 = time.perf_counter()
    p = subprocess.Popen(["sh", "-c", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    err = p.stderr.read()
    _, status, ru = os.wait4(p.pid, 0)
    wall = time.perf_counter() - t0
    return wall, ru.ru_utime, ru.ru_stime, os.waitstatus_to_exitcode(status), err

def main(argv):
    n, cases, i = 5, [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--n": n = int(argv[i+1]); i += 2
        else: name, cmd = a.split("=", 1); cases.append((name, cmd)); i += 1
    rows = {name: [] for name, _ in cases}
    for k in range(n):
        for name, cmd in cases:
            wall, u, s, rc, err = run(cmd)
            if rc != 0: sys.stderr.write("%s rc=%d %s\n" % (name, rc, err[-300:].decode("utf-8", "replace")))
            row = dict(name=name, i=k, wall=round(wall, 4), user=round(u, 4), sys=round(s, 4), load1=round(os.getloadavg()[0], 2), rc=rc)
            rows[name].append(row)
            print(json.dumps(row), flush=True)
    for name, _ in cases:
        w = [r["wall"] for r in rows[name]]; c = [r["user"] + r["sys"] for r in rows[name]]
        sys.stderr.write("%-28s wall min %.3f med %.3f max %.3f   cpu med %.3f\n" % (name, min(w), statistics.median(w), max(w), statistics.median(c)))
main(sys.argv[1:])
