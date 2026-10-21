# w06-c9: counts production lines (everything outside `def selftest` .. `def main`) and selftest lines of budget.py, handback.py and run_hook.py in two plugin trees; inputs: two plugin roots (main, build); output: a markdown table on stdout (wc -l of the files, and the split)
import os, sys


def split(path):
    if not os.path.exists(path):
        return 0, 0, 0
    lines = open(path).read().splitlines()
    a = next((i for i, l in enumerate(lines) if l.startswith("def selftest")), None)
    b = next((i for i, l in enumerate(lines) if l.startswith("def main")), None)
    test = (b - a) if a is not None and b is not None else 0
    return len(lines), len(lines) - test, test


print("| file | main: whole / production / selftest | build: whole / production / selftest |\n|:--|:--|:--|")
tot = [0, 0, 0, 0, 0, 0]
for f in ("budget.py", "handback.py", "run_hook.py"):
    a, b = split(os.path.join(sys.argv[1], "scripts", f)), split(os.path.join(sys.argv[2], "scripts", f))
    print("| %s | %d / %d / %d | %d / %d / %d |" % ((f,) + a + b))
    tot = [x + y for x, y in zip(tot, a + b)]
print("| total | %d / %d / %d | %d / %d / %d |" % tuple(tot))
print("\nproduction lines: build - main = %+d (limit +100)" % (tot[4] - tot[1]))
