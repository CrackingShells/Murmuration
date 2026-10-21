"""Times the stages of lab_status.report_spend in-process (git call, find_sessions, cache load, load_sessions, rest) and an in-process replacement for the git call, from a lab root to a table on stdout; median of N repeats, warm cache and no cache.

usage: w07d_stages.py <lab root> [N]
Reuses lab_status.py by import. The git replacement reads <common git dir>/worktrees/*/gitdir (what `git worktree list --porcelain` reads) and is checked for the same set of paths.
"""
import sys, os, time, statistics, glob, subprocess
root = os.path.abspath(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 7
sys.path.insert(0, os.path.join(root, "scripts"))
t0 = time.perf_counter(); import lab_status as L; t_import = time.perf_counter() - t0
def med(fn):
    ts = []
    for _ in range(N):
        t = time.perf_counter(); r = fn(); ts.append(time.perf_counter() - t)
    return statistics.median(ts), min(ts), max(ts), r
def git_files(root):
    """Worktree paths without a process: the main checkout (parent of the common dir) plus each worktrees/*/gitdir (its path minus /.git)."""
    p = os.path.join(root, ".git")
    if os.path.isfile(p):
        gd = open(p).read().strip()[len("gitdir:"):].strip()      # <common>/worktrees/<name>
        common = os.path.dirname(os.path.dirname(gd))
    else:
        common = p
    out = [os.path.dirname(common)]
    for g in sorted(glob.glob(os.path.join(common, "worktrees", "*", "gitdir"))):
        out.append(os.path.dirname(open(g).read().strip()))
    return out
rows = []
m = med(lambda: L.git_worktrees(root)); rows.append(("git worktree list (subprocess)",) + m[:3]); trees = m[3]
m2 = med(lambda: git_files(root)); rows.append(("worktree list from .git files",) + m2[:3])
print("same set of paths:", sorted(os.path.realpath(x) for x in trees) == sorted(os.path.realpath(x) for x in m2[3]), len(trees), len(m2[3]))
roots = L.lab_roots(root, trees)
m = med(lambda: L.find_sessions(roots)); rows.append(("find_sessions",) + m[:3]); mains = m[3]
L.report_spend(root)  # make the cache warm
cp = L.cache_path(root)
m = med(lambda: L.Cache(cp)); rows.append(("Cache(): json.load of %.1f MB" % (os.path.getsize(cp) / 1e6),) + m[:3])
def load_warm():
    L._cache[:] = [L.Cache(cp)]
    try: return L.load_sessions(mains, [])
    finally: L._cache[:] = []
m = med(load_warm); rows.append(("load_sessions, warm cache (incl. Cache load)",) + m[:3])
os.environ["LAB_STATUS_CACHE"] = "off"
m = med(lambda: L.load_sessions(mains, [])); rows.append(("load_sessions, no cache (parse everything)",) + m[:3])
m = med(lambda: L.report_spend(root)); rows.append(("report_spend total, no cache",) + m[:3])
del os.environ["LAB_STATUS_CACHE"]
m = med(lambda: L.report_spend(root)); rows.append(("report_spend total, warm cache",) + m[:3])
print("import lab_status (first, in-process): %.4f s" % t_import)
for r in rows: print("%-48s med %.4f  min %.4f  max %.4f" % r)
