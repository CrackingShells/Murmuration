# For classified denied calls, print the lines that trigger the guard (bypass words / CLAUDE_CONFIG_DIR= / settings-file write) and the lines that run `claude`; input: classified.json group start end; output: stdout
import json, re, sys, importlib.util
rows = json.load(open(sys.argv[1])); g = sys.argv[2]
spec = importlib.util.spec_from_file_location("pg", "scripts/permission_guard.py"); G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
TRIG = {"G1": G.BYPASS, "G2": re.compile(r"CLAUDE_CONFIG_DIR=|--setting-sources|--bare|--safe-mode|disableAllHooks"), "G3": re.compile(r"settings(\.local)?\.json|managed-settings")}[g]
RUN = re.compile(r"""(^|[\s;&|(`'"\[,])claude(\s|['"],|$)""")
sel = [(i, r) for i, r in enumerate(rows) if r["group"] == g]
a, b = int(sys.argv[3]), int(sys.argv[4])
for i, r in sel[a:b]:
    print("#%d %s %s dwd=%s data_hd=%d cwd=%s" % (i, r["session"], r["ts"][5:16], r["denied_without_data_heredocs"], r["n_data_heredocs"], (r["cwd"] or "")[-40:]))
    print("   H:", r["command"][:90].replace("\n", " ⏎ "))
    lines = r["command"].split("\n"); kt = kr = 0
    for n, ln in enumerate(lines):
        if TRIG.search(ln) and kt < 3: print("   T%d:" % n, ln.strip()[:190]); kt += 1
        if RUN.search(ln) and kr < 2 and not TRIG.search(ln): print("   R%d:" % n, ln.strip()[:190]); kr += 1
