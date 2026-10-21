"""Profiles scripts/lab_status.py's transcript parsing from a frozen clone of the transcript tree to a phase table (files, bytes, lines, read, split, prefilter, json.loads, own logic) and a cProfile of report_spend on the live tree; writes the frozen file list to <scratch>/files.txt.

usage: w07d_profile.py <lab root> <scratch dir containing cfg/projects (APFS clone of the lab's project folders)>
Reuses lab_status.py by import (never edits it). The file list is what lab_status would read on the live tree (mains plus subagents), mapped onto the clone.
"""
import sys, os, time, json, glob, cProfile, pstats, io, collections
root, scratch = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
sys.path.insert(0, os.path.join(root, "scripts"))
import lab_status as L
live = os.path.join(L.config_dir(), "projects"); frozen = os.path.join(scratch, "cfg", "projects")

t = time.perf_counter(); trees = L.git_worktrees(root); t_git = time.perf_counter() - t
roots = L.lab_roots(root, trees)
t = time.perf_counter(); mains = L.find_sessions(roots); t_find = time.perf_counter() - t
files = list(mains)
for m in mains:
    files += sorted(glob.glob(os.path.join(m[:-6], "subagents", "**", "agent-*.jsonl"), recursive=True))
files = [f.replace(live, frozen, 1) for f in files]
files = [f for f in files if os.path.exists(f)]
open(os.path.join(scratch, "files.txt"), "w").write("\n".join(files) + "\n")
sizes = [os.path.getsize(f) for f in files]
print("git worktree list %.3f s; find_sessions (listdir+glob+first_cwd of %d candidate mains) %.3f s" % (t_git, len(mains), t_find))
print("files %d (mains %d), bytes %d (%.1f MB); median %d, max %d, files>1MB %d holding %.1f MB" % (len(files), len(mains), sum(sizes), sum(sizes)/1e6, sorted(sizes)[len(sizes)//2], max(sizes), sum(s > 1e6 for s in sizes), sum(s for s in sizes if s > 1e6)/1e6))

def timed(fn):
    best = 1e9
    for _ in range(3):
        t = time.perf_counter(); r = fn(); best = min(best, time.perf_counter() - t)
    return best, r
def read_all():
    n = 0
    for f in files:
        with open(f, "rb") as fh: n += len(fh.read())
    return n
def split_lines():
    n = 0
    for f in files:
        with open(f, "rb") as fh: n += len(fh.read().split(b"\n"))
    return n
def lines_iter():
    n = 0
    for f in files:
        with open(f, "rb") as fh:
            for line in fh: n += 1
    return n
KEYS = (b'"assistant"', b'"cost-state"', b'"agent-setting"')
def prefilter():
    n = nb = 0
    for f in files:
        with open(f, "rb") as fh:
            for line in fh:
                if KEYS[0] in line or KEYS[1] in line or KEYS[2] in line: n += 1; nb += len(line)
    return n, nb
passing = []
for f in files:
    with open(f, "rb") as fh:
        for line in fh:
            if KEYS[0] in line or KEYS[1] in line or KEYS[2] in line: passing.append(line)
def loads_only():
    for l in passing:
        try: json.loads(l)
        except ValueError: pass
def orig_parse():
    w = []
    for f in files: L.parse_transcript(f, w)
tr, nbytes = timed(read_all); print("read whole files into memory (rb):            %.3f s  (%.2f GB/s)" % (tr, nbytes/tr/1e9))
ts, nl = timed(split_lines); print("read + split on b'\\n' (%d lines):       %.3f s" % (nl, ts))
ti, _ = timed(lines_iter); print("iterate lines in rb mode:                      %.3f s" % ti)
tp, (np_, npb) = timed(prefilter); print("iterate + 3-substring prefilter:               %.3f s; %d lines pass (%.1f%% of lines), %.1f MB (%.1f%% of bytes)" % (tp, np_, 100*np_/nl, npb/1e6, 100*npb/nbytes))
tl, _ = timed(loads_only); print("json.loads of the passing lines only:          %.3f s" % tl)
to, _ = timed(orig_parse); print("original parse_transcript over all files:      %.3f s" % to)
print("=> original minus (iterate+prefilter+loads) = own logic + text decode: %.3f s" % (to - tp - tl))
# which top-level record types pass
c = collections.Counter()
for l in passing:
    r = json.loads(l); c[r.get("type")] += 1
print("types of passing lines:", dict(c))
# subset test: what is `"assistant"` doing in a non-assistant record
c2 = collections.Counter(); bytes_by = collections.Counter()
for l in passing:
    r = json.loads(l); k = r.get("type"); bytes_by[k] += len(l)
print("bytes by type among passing:", dict(bytes_by))
pr = cProfile.Profile(); pr.enable()
os.environ["LAB_STATUS_CACHE"] = "off"
L.report_spend(root); pr.disable()
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(14); print(s.getvalue()[:3500])
