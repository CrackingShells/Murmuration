"""Runs two copies of lab_status.py as processes (`--spend --project DIR`) on the failure folders left by w07c4_worktree_cases.py, from the two script paths and that scratch folder to one line per case (o3 of protocol P4, end to end: same stdout, same exit code, no exception, no hang); exit 1 on a difference.

usage: w07c4_o3_cli.py A.py B.py CASES_DIR
Folders hold no transcripts of their own; the run reads the real transcript folder, so a lab outside them is found only through the repository's worktrees (none of these is a lab worktree).
"""
import os
import subprocess
import sys
import time


def run(script, d):
    t = time.perf_counter()
    try:
        p = subprocess.run([sys.executable, "-I", script, "--spend", "--project", d], capture_output=True, text=True, timeout=30)
        return (p.returncode, p.stdout, p.stderr), time.perf_counter() - t
    except subprocess.TimeoutExpired:
        return ("TIMEOUT", "", ""), 30.0


def main(a, b, cases):
    names = [("f-nogit-perm", ".git"), ("f-nowt-perm", ".git/worktrees"), ("f-gitdir-missing", None), ("f-gitdir-garbage", None),
             ("f-nohead", None), ("f-dotgit-garbage-wt", None), ("sep", None), ("bare.git", None), ("not-a-repo", None), ("nope", None), ("outer/plain/nope", None), ("outer/inner.git", None), ("outer/plain/sub", None)]
    bad = 0
    for name, chmod in names:
        d = os.path.join(cases, name)
        if name == "f-dotgit-garbage-wt":
            d = os.path.join(cases, "f-dotgit-garbage-wt")
        mode = None
        if chmod:
            target = os.path.join(d, chmod)
            mode = os.stat(target).st_mode
            os.chmod(target, 0)
        try:
            ra, ta = run(a, d)
            rb, tb = run(b, d)
        finally:
            if mode is not None:
                os.chmod(target, mode)
        same = ra == rb and ra[0] == 0 and "Traceback" not in ra[2] + rb[2]
        bad += not same
        print("%s: rc A %s B %s; stdout same %s; stderr empty A %s B %s; %.2f s / %.2f s -> %s" % (
            name, ra[0], rb[0], ra[1] == rb[1], not ra[2], not rb[2], ta, tb, "SAME" if same else "DIFFERENT"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
