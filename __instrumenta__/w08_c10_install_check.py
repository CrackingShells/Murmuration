# w08-c10: clones a branch of a repo into a new folder (a clean tree: committed files only), runs scripts/install_binary.py there as the SessionStart hook does (CLAUDE_PLUGIN_ROOT = the clone, CLAUDE_PLUGIN_DATA = a new folder), and reports whether the binary or the launcher was installed; then feeds the hole-form payloads of scripts/guard_selftest_holes.json to the installed program.
# inputs: --repo DIR (the repo holding the branch), --branch NAME, --scratch DIR (must not exist); output: stdout lines (state, sha256 of the installed file against bin/<target>/murmuration, stamp, stderr of the installer, hole-form decisions of the installed program) and exit 0 only when the binary is installed and every hole-form decision is as the file says.
# usage: python3 -I w08_c10_install_check.py --repo DIR --branch NAME --scratch DIR
import argparse, hashlib, json, os, platform, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--branch", required=True)
ap.add_argument("--scratch", required=True)
a = ap.parse_args()
assert not os.path.exists(a.scratch), "scratch must be new"
os.makedirs(a.scratch)
root, data = os.path.join(a.scratch, "clone"), os.path.join(a.scratch, "data")
subprocess.run(["git", "clone", "-q", "--local", "--branch", a.branch, a.repo, root], check=True)
os.makedirs(data)
env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root, CLAUDE_PLUGIN_DATA=data)
p = subprocess.run([sys.executable, "-S", "-I", os.path.join(root, "scripts", "install_binary.py")], env=env, capture_output=True, text=True)
target = {"arm64": "aarch64-apple-darwin", "x86_64": "x86_64-apple-darwin"}[platform.machine()]
sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest()
dest = os.path.join(data, "bin", "murmuration")
src = os.path.join(root, "bin", target, "murmuration")
is_binary = os.path.isfile(dest) and sha(dest) == sha(src)
print("installer exit %d; stdout %r; stderr %r" % (p.returncode, p.stdout[:200], p.stderr[:300]))
print("installed file equals bin/%s/murmuration: %s; launcher script: %s; stamp present: %s" % (target, is_binary, open(dest, "rb").read(2) == b"#!", os.path.isfile(os.path.join(data, "bin", ".verified"))))
ok = is_binary and p.returncode == 0
bad = 0
for c in json.load(open(os.path.join(root, "scripts", "guard_selftest_holes.json"))):
    ev = json.dumps(dict(tool_name="Bash", tool_input={"command": c["command"]}, cwd="/h/proj"))
    q = subprocess.run([dest, "guard"], input=ev.encode(), capture_output=True)
    if bool(q.stdout) != c["deny"]:
        bad += 1
        print("  WRONG", c["id"])
print("hole-form cases decided as stated by the installed program: %d wrong" % bad)
sys.exit(0 if ok and not bad else 1)
