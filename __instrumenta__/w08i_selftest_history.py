# Runs every `scripts/*.py --selftest` on a clean `git archive` of each commit that touched scripts/, hooks/ or bin/, to show which landed or merged states fail the scripts' own selftests; input: the lab's git history (read only; archives go to a scratch folder given as argument); output: a TSV on stdout (commit, date, subject, script, exit code, last line).
# usage: python3 -I __instrumenta__/w08i_selftest_history.py <scratch folder> [commit ...]   (default: every commit touching scripts hooks bin)
import sys, os, subprocess, tarfile, io, shutil, glob
scratch = os.path.abspath(sys.argv[1]); os.makedirs(scratch, exist_ok=True)
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
def git(*a): return subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True).stdout
commits = sys.argv[2:] or git("log", "--format=%h", "--", "scripts", "hooks", "bin").split()
print("commit\tdate\tsubject\tscript\texit\tlast_line")
for c in commits:
    meta = git("log", "-1", "--format=%cI\t%s", c).strip().split("\t")
    d = os.path.join(scratch, c); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    paths = [x for x in ("scripts", "hooks", "bin", "agents", "skills", ".claude-plugin") if git("ls-tree", c, x).strip()]
    p = subprocess.run(["git", "-C", root, "archive", c, "--"] + paths, capture_output=True)
    tarfile.open(fileobj=io.BytesIO(p.stdout)).extractall(d, filter="tar")
    for f in sorted(glob.glob(os.path.join(d, "scripts", "*.py"))):
        if "--selftest" not in open(f, errors="replace").read(): continue
        try:
            r = subprocess.run([sys.executable, "-I", f, "--selftest"], capture_output=True, text=True, timeout=150, cwd=d)
            code, last = r.returncode, ((r.stdout + r.stderr).strip().splitlines() or [""])[-1][:120]
        except subprocess.TimeoutExpired:
            code, last = "timeout", ""
        print("\t".join([c, meta[0][:16], meta[1][:60], os.path.basename(f), str(code), last.replace("\t", " ")]), flush=True)
    shutil.rmtree(d, ignore_errors=True)
