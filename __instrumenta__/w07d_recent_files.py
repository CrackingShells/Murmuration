"""Counts the transcript files lab_status.py reads that changed within the last 10 min, 1 h, 6 h and 24 h, with their bytes and the time the original parse_transcript takes on them, from a lab root to a table on stdout.

usage: w07d_recent_files.py <lab root>   (live tree: the numbers depend on when it runs)
"""
import sys, os, time, glob
sys.path.insert(0, os.path.join(os.path.abspath(sys.argv[1]), "scripts"))
import lab_status as L
root = os.path.abspath(sys.argv[1]); mains = L.find_sessions(L.lab_roots(root, L.git_worktrees(root)))
files = list(mains)
for m in mains: files += glob.glob(os.path.join(m[:-6], "subagents", "**", "agent-*.jsonl"), recursive=True)
now = time.time()
for win in (600, 3600, 6 * 3600, 24 * 3600):
    rec = [f for f in files if now - os.path.getmtime(f) < win]
    t = time.perf_counter(); w = []
    for f in rec: L.parse_transcript(f, w)
    print("modified in last %6d s: %3d files, %6.1f MB, orig parse %.3f s" % (win, len(rec), sum(os.path.getsize(f) for f in rec) / 1e6, time.perf_counter() - t))
print(len(files), "files total")
