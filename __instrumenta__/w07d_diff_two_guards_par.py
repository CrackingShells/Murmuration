# Parallel version of w06c13_v7_diff_two_guards.py: replays every recorded Bash/Write/Edit call through two guard files' decide() on W forked workers (one task per transcript file, largest first), then merges in the serial script's file order so that the printed lines and the json are the same; inputs: W, guard A, guard B, out json, project folders; output: counts and the differing calls, as the serial script prints them
import glob, importlib.util, json, os, sys, multiprocessing as mp
def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
W = int(sys.argv[1]); A, B = load(sys.argv[2], "ga"), load(sys.argv[3], "gb"); out = sys.argv[4]
def scan(f):
    """[(tool id, flip record or None)] for the first occurrence of each id within this file, in file order."""
    res, seen = [], set()
    with open(f, errors="replace") as fh:
        for line in fh:
            if '"tool_use"' not in line: continue
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("type") != "assistant": continue
            for b in (m.get("message", {}).get("content") or []):
                if not isinstance(b, dict) or b.get("type") != "tool_use" or b.get("name") not in ("Bash", "Write", "Edit"): continue
                if b["id"] in seen: continue
                seen.add(b["id"])
                ev = dict(tool_name=b["name"], tool_input=b["input"], cwd=m.get("cwd") or "")
                ra, rb = A.decide(ev), B.decide(ev)
                flip = None
                if bool(ra) != bool(rb) or (ra and rb and ra[0] != rb[0]):
                    flip = dict(id=b["id"], tool=b["name"], a=ra[0] if ra else None, b=rb[0] if rb else None, session=os.path.basename(f)[:8], ts=m.get("timestamp"), command=b["input"].get("command") or b["input"].get("file_path") or "")
                res.append((b["id"], flip))
    return f, res
files = []
for folder in sys.argv[5:]:
    files += sorted(glob.glob(folder + "/**/*.jsonl", recursive=True))
order = sorted(files, key=lambda f: -os.path.getsize(f))
if W <= 1:
    got = dict(scan(f) for f in order)
else:
    with mp.get_context("fork").Pool(W) as pool:
        got = dict(pool.imap_unordered(scan, order, chunksize=1))
seen, flips, n = set(), [], 0
for f in files:
    for tid, flip in got[f]:
        if tid in seen: continue
        seen.add(tid); n += 1
        if flip: flips.append(flip)
json.dump(flips, open(out, "w"), indent=1); print(n, "calls;", len(flips), "differ")
for x in flips: print(x["a"], "->", x["b"], x["session"], x["ts"][5:16], x["command"][:140].replace("\n", " ⏎ "))
