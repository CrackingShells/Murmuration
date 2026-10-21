"""Checks that two copies of lab_status.py print byte-identical `--spend` and full reports, cold and warm, on a frozen APFS clone of the lab's transcripts, from the two script paths, the lab root and a scratch folder to a summary on stdout (o1 of protocol P4); exit 1 on a difference.

usage: w07c4_frozen_diff.py A.py B.py LAB_ROOT SCRATCH [--clone]
--clone first clones (cp -cR) the project folders that A's find_sessions opens from the real ~/.claude/projects into SCRATCH/cfg/projects (read only on the source; the clone is not committed and is deleted after the run).
No CLAUDE_CONFIG_DIR is set: each module's `config_dir` is replaced in process. Each variant gets its own cache file (LAB_STATUS_CACHE), so that their cache versions do not overwrite one another.
Also counts, in the frozen files, the records with usage.speed == "fast" and with a non-zero web_search_requests (o2: whether change 2 can alter the real tree's output).
"""
import difflib
import glob
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import time


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def main(a_path, b_path, root, scratch, *flags):
    A, B = load(a_path, "A"), load(b_path, "B")
    cfg = os.path.join(scratch, "cfg")
    if "--clone" in flags:
        shutil.rmtree(cfg, ignore_errors=True)
        os.makedirs(os.path.join(cfg, "projects"))
        real = os.path.join(os.path.expanduser("~"), ".claude")
        A.config_dir = lambda: real
        roots = A.lab_roots(root)
        folders = sorted({os.path.basename(os.path.dirname(f)) for f in A.find_sessions(roots)})
        for name in folders:
            subprocess.run(["cp", "-cR", os.path.join(real, "projects", name), os.path.join(cfg, "projects", name)], check=True)
        print("cloned %d project folders" % len(folders))
    for mod in (A, B):
        mod.config_dir = lambda: cfg
    files = glob.glob(os.path.join(cfg, "projects", "**", "*.jsonl"), recursive=True)
    nbytes = sum(os.path.getsize(f) for f in files)
    fast = web = 0
    for f in files:
        with open(f, "rb") as fh:
            for line in fh:
                if b'"speed":"fast"' in line or b'"speed": "fast"' in line:
                    fast += 1
                if re.search(rb'"web_search_requests": ?[1-9]', line):
                    web += 1
    print("frozen files: %d, %.1f MB; lines with speed fast: %d; lines with web_search_requests > 0: %d" % (len(files), nbytes / 1e6, fast, web))
    print("worktree lists equal: %s" % (A.git_worktrees(root) == B.git_worktrees(root)))

    out = {}
    for name, mod in (("A", A), ("B", B)):
        cache = os.path.join(scratch, "cache_%s.json" % name)
        if os.path.exists(cache):
            os.unlink(cache)
        os.environ["LAB_STATUS_CACHE"] = cache
        for mode in ("cold", "warm"):
            t = time.perf_counter()
            spend = "\n".join(mod.report_spend(root))
            t1 = time.perf_counter() - t
            out[(name, mode, "spend")] = spend
            print("%s %s --spend: %.3f s, %d bytes, sha %s" % (name, mode, t1, len(spend), digest(spend)))
        # the full report, off the cache's cold/warm axis (the cache is warm now); puzzles and claims are the live files
        os.environ["LAB_STATUS_CACHE"] = cache + ".full"
        if os.path.exists(cache + ".full"):
            os.unlink(cache + ".full")
        for mode in ("cold", "warm"):
            full = mod.report(root)
            out[(name, mode, "full")] = full
            print("%s %s full: %d bytes, sha %s" % (name, mode, len(full), digest(full)))
    # A again, to tell drift in the live puzzle and claim files from a difference between A and B
    os.environ["LAB_STATUS_CACHE"] = os.path.join(scratch, "cache_A.json.full")
    again = A.report(root)
    print("A full again: sha %s (equal to A's earlier full: %s)" % (digest(again), again == out[("A", "warm", "full")]))
    bad = 0
    for kind in ("spend", "full"):
        for mode in ("cold", "warm"):
            same = out[("A", mode, kind)] == out[("B", mode, kind)]
            print("%s %s: A == B byte for byte: %s" % (kind, mode, same))
            if not same:
                bad += 1
                for line in list(difflib.unified_diff(out[("A", mode, kind)].splitlines(), out[("B", mode, kind)].splitlines(), "A", "B", lineterm="", n=0))[:20]:
                    print("   " + line)
    for kind in ("spend", "full"):
        print("%s: A cold == A warm: %s; B cold == B warm: %s" % (kind, out[("A", "cold", kind)] == out[("A", "warm", kind)],
                                                              out[("B", "cold", kind)] == out[("B", "warm", kind)]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
