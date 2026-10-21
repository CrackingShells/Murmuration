# w07-c3 reproduction: runs N pairs of one scenario with w07c3_repro_run_arm.py, both arms of a pair started together, order alternating; inputs SCENARIO N [FIRST]; outputs runs/<scenario>_<i>_{A,B}/ and runs/pairs_<scenario>.log under /private/tmp/murmuration-w07/reproducer-w07-3
"""usage: w07c3_run_pairs.py SCENARIO N [FIRST]    The order of the two process starts alternates per pair (A first on odd pairs, B first on even pairs)."""
import os, subprocess, sys

S = "/private/tmp/murmuration-w07/reproducer-w07-3"
H = os.path.dirname(os.path.abspath(__file__)) + "/w07c3_repro_run_arm.py"
scen, n = sys.argv[1], int(sys.argv[2])
first = int(sys.argv[3]) if len(sys.argv) > 3 else 1
os.makedirs(S + "/runs", exist_ok=True)
log = open("%s/runs/pairs_%s.log" % (S, scen), "a")
for i in range(first, first + n):
    l0 = os.getloadavg()[0]
    order = ("A", "B") if i % 2 else ("B", "A")
    ps = []
    for arm in order:
        ps.append(subprocess.Popen([sys.executable, H, arm, "%s_%d_%s" % (scen, i, arm), scen], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
    outs = [p.communicate()[0].strip() for p in ps]
    line = "pair %d load_start %.2f load_end %.2f | %s" % (i, l0, os.getloadavg()[0], " | ".join(outs))
    print(line, flush=True); log.write(line + "\n"); log.flush()
