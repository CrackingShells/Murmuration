#!/usr/bin/env python3
"""Claim w01-c3, checks B1-B2: runtime and size of the two ways to find a lab's sessions, and of v6.
B1 median of 5 runs, live data, this machine (213 project folders, 1628 transcript files under ~/.claude/projects).
B2 lines of code that each way adds (non-blank, non-comment, docstrings excluded), by function.
Writes bench.txt. Run: python3 -I bench.py"""
import ast, os, statistics, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(REPO, "scripts"))
import lab_spend as L
import lab_status as V6
out = []
def say(s):
    out.append(s); print(s)
def med(f, n=5):
    t = []
    for _ in range(n):
        a = time.perf_counter(); f(); t.append(time.perf_counter() - a)
    return statistics.median(t)
COMB = "/Users/hacker/Documents/explore/combinatorics_on_binary"
MAIN = "/Users/hacker/Documents/src/CrackingShells/Murmuration"
say("B1 runtime, median of 5, seconds (live data)")
say("   find sessions only:   scan(this worktree) %.3f   scan(main checkout) %.3f   v6 folder lookup %.4f" % (
    med(lambda: L.find_scan(REPO)), med(lambda: L.find_scan(MAIN)), med(lambda: V6.transcript_dirs(REPO))))
say("   whole Spend section:  lab_spend(this worktree) %.2f   v6 report_spend(this worktree) %.2f" % (
    med(lambda: L.report(REPO), 3), med(lambda: V6.report_spend(REPO), 3)))
say("   whole Spend section:  lab_spend(combinatorics) %.2f   v6 report_spend(combinatorics) %.2f" % (
    med(lambda: L.report(COMB), 3), med(lambda: V6.report_spend(COMB), 3)))
def loc(path, names):
    src = open(path).read()
    tree = ast.parse(src)
    lines = src.splitlines()
    total = {}
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in names:
            body = n.body[1:] if (n.body and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant)) else n.body
            first, last = body[0].lineno, n.end_lineno
            total[n.name] = sum(1 for l in lines[first - 1:last] if l.strip() and not l.strip().startswith("#"))
    return total
scan = loc(os.path.join(HERE, "lab_spend.py"), {"git_worktrees", "git_roots", "first_cwd", "under", "main_files", "find_scan", "find_ids", "find_v6"})
idx = loc(os.path.join(HERE, "index_hook.py"), {"lab_above", "main"})
idx.update(loc(os.path.join(HERE, "lab_spend.py"), {"find_index"}))
v6 = loc(os.path.join(REPO, "scripts", "lab_status.py"), {"project_folder_names", "records_have_cwd", "transcript_dirs"})
say("B2 lines of code to find the sessions")
say("   v6 (one folder by path, long-path fallback): %d  %s" % (sum(v6.values()), v6))
say("   scan by cwd + git worktrees + ids:           %d  %s" % (sum(scan.values()), scan))
say("   run-index hook + reader (plus 3 hook entries in hooks.json, not counted): %d  %s" % (sum(idx.values()), idx))
open(os.path.join(HERE, "bench.txt"), "w").write("\n".join(out) + "\n")
