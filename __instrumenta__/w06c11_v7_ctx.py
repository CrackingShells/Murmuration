# Show lines of denied calls (classified.json) matching a regex with context; input: classified.json index... -e regex -C n; output: stdout
import json, re, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument("idx", nargs="+", type=int); ap.add_argument("-e", default="settings"); ap.add_argument("-C", type=int, default=1); ap.add_argument("-w", type=int, default=220); ap.add_argument("-m", type=int, default=6)
a = ap.parse_args(); rows = json.load(open("/private/tmp/murmuration-w06/reproducer-w06-7/out/classified.json")); R = re.compile(a.e)
for i in a.idx:
    r = rows[i]; L = r["command"].split("\n"); print("#%d %s %s len=%d lines=%d | %s" % (i, r["session"], r["group"], len(r["command"]), len(L), r["why"][:80]))
    shown = set(); k = 0
    for n, ln in enumerate(L):
        if R.search(ln) and k < a.m:
            k += 1
            for j in range(max(0, n - a.C), min(len(L), n + a.C + 1)):
                if j not in shown: shown.add(j); print("  %3d| %s" % (j, L[j].strip()[:a.w]))
            print("  ---")
