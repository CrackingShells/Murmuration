"""Mutants of the verdict rule: each must make `--selftest` fail."""
import os, subprocess, sys, tempfile
SCRIPT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "scripts", "lab_status.py"))
src = open(SCRIPT).read()
M = [("the first verdict line stands again", "value = hits[-1][1]", "value = hits[0][1]"),
     ("no warning when changed_by is missing", "if len(hits) > 1 and not any(", "if False and not any("),
     ("a changed_by anywhere excuses it (not only below the earlier verdict)", "lines[hits[-2][0] + 1:]", "lines")]
ok = True
for name, old, new in M:
    assert src.count(old) == 1, name
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "lab_status.py"); open(p, "w").write(src.replace(old, new))
        r = subprocess.run([sys.executable, "-I", p, "--selftest"], capture_output=True, text=True)
    ok &= r.returncode != 0
    print("%-7s %s" % ("caught" if r.returncode else "MISSED", name))
sys.exit(0 if ok else 1)
