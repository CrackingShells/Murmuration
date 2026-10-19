"""Each mutant of scripts/lab_status.py must make `--selftest` fail: the selftest can fail, so its pass means something.

    python3 -I mutants.py"""
import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "scripts", "lab_status.py"))
src = open(SCRIPT).read()
MUTANTS = [
    ("detector: any record with a stop_reason counts, not the last", 'msg["final"] = bool(m.get("stop_reason"))',
     'msg["final"] = msg.get("final", False) or bool(m.get("stop_reason"))'),
    ("owner: charge a copy to the file's session, not the record's sessionId", 'have = owned.get(key)\n',
     'have = owned.get(key)\n                msg["sid"] = sid\n'),
    ("discovery: ignore git worktrees", 'for path in git_worktrees(root):\n        roots', 'for path in []:\n        roots'),
    ("price: the 1 hour cache write is charged as 5 minutes", 'cw5 += max(0, cw - cw1 - cw5)', 'cw5 += cw; cw1 = 0'),
    ("no-git notice is never printed", 'if not git_worktrees(root):\n        out.append("!', 'if False:\n        out.append("!'),
    ("exact: ignore cost-state", 'ended = s["cost_state"] is not None', 'ended = False'),
    ("discovery: a folder with the right name prefix is the lab's whatever its records' cwd say",
     'if under(first_cwd(f), roots)]', 'if True]'),
]
ok = True
for name, old, new in MUTANTS:
    assert src.count(old) == 1, (name, src.count(old))
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "lab_status.py")
        open(path, "w").write(src.replace(old, new))
        r = subprocess.run([sys.executable, "-I", path, "--selftest"], capture_output=True, text=True)
    failed = r.returncode != 0
    ok &= failed
    print("%-8s %s" % ("caught" if failed else "MISSED", name))
sys.exit(0 if ok else 1)
