# Fires a SubagentStart through scripts/budget.py and through two `murmuration budget` binaries in labs of different shapes (git worktree, plain git checkout, path with spaces, symlinked path, cwd in a subfolder, cwd deeper than the search limit with CLAUDE_PROJECT_DIR, a path with a double quote) and prints the `paths:` argument the start note gives, against the lab's own absolute path.
# inputs: --repo (tree with scripts/), --bin (testclock build), --shipped (shipped binary), --scratch DIR; output: one line per lab and implementation, OK or the mismatch; exit 1 on any mismatch.
import argparse, json, os, re, shutil, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--bin", required=True)
ap.add_argument("--shipped", required=True)
ap.add_argument("--scratch", required=True)
ap.add_argument("--worktree", required=True, help="an existing git worktree that has __statera__/")
a = ap.parse_args()
shim = os.path.join(os.path.dirname(os.path.abspath(__file__)), "w08c1_pyshim.py")
S = os.path.realpath(a.scratch)
shutil.rmtree(S, ignore_errors=True)
os.makedirs(S)


def mk(path):
    os.makedirs(path + "/__statera__")
    return path


labs = {}
labs["plain git checkout"] = mk(S + "/main_like")
subprocess.run(["git", "init", "-q", labs["plain git checkout"]], check=True)
labs["spaces"] = mk(S + "/a lab with  spaces/x y")
os.symlink(labs["plain git checkout"], S + "/link_to_main_like")
labs["symlinked"] = S + "/link_to_main_like"
labs["double quote"] = mk(S + '/q"uote')
labs["worktree"] = os.path.abspath(a.worktree)
deep = mk(S + "/deep") + "/1/2/3/4/5/6/7"
os.makedirs(deep)
labs["cwd 7 levels below"] = S + "/deep"


def start(impl, lab, cwd, projdir=None):
    ev = dict(cwd=cwd, hook_event_name="SubagentStart", agent_id="a1", agent_type="murmuration:explorer", transcript_path=lab + "/s.jsonl", permission_mode="default")
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "MURMURATION_NOW")}
    env.update(LC_ALL="en_US.UTF-8", CLAUDE_PLUGIN_ROOT=a.repo, MURMURATION_NOW="1792700000.5")
    if projdir:
        env["CLAUDE_PROJECT_DIR"] = projdir
    cmd = {"py": ["python3", "-S", "-I", shim, a.repo + "/scripts", "budget"], "bin": [a.bin, "budget"], "shipped": [a.shipped, "budget"]}[impl]
    p = subprocess.run(cmd, input=json.dumps(ev).encode(), capture_output=True, env=env, cwd="/private/tmp", timeout=60)
    try:
        return json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return "<no context: rc %s %r %r>" % (p.returncode, p.stdout[:80], p.stderr[:80])


bad = 0
cases = [(k, v, v, None) for k, v in labs.items() if k != "cwd 7 levels below"]
cases += [("cwd subfolder (3 levels)", labs["plain git checkout"], None, None), ("cwd 7 levels below + CLAUDE_PROJECT_DIR", labs["cwd 7 levels below"], labs["cwd 7 levels below"] + "/1/2/3/4/5/6/7", labs["cwd 7 levels below"])]
for title, lab, cwd, projdir in cases:
    if title.startswith("cwd subfolder"):
        cwd = lab + "/sub1/sub2/sub3"
        os.makedirs(cwd, exist_ok=True)
    got = {}
    for impl in ("py", "bin", "shipped"):
        shutil.rmtree(lab + "/__statera__/.harness", ignore_errors=True)
        if os.path.exists(lab + "/__statera__/harness.jsonl"):
            os.unlink(lab + "/__statera__/harness.jsonl")
        got[impl] = start(impl, lab, cwd, projdir)
    for impl, ctx in got.items():
        m = re.search(r'`search` with `paths: (\[.*?\])` \(absolute', ctx)
        want = lab.rstrip("/") + "/__instrumenta__"
        ok = bool(m) and m.group(1) == json.dumps([want]) if '"' not in lab else bool(m)
        absolute = bool(m) and os.path.isabs(json.loads(m.group(1))[0]) if (m and '"' not in lab) else None
        print("%-40s %-8s %s  %s" % (title, impl, "OK" if ok else "MISMATCH", (m.group(1) if m else ctx[:200])))
        bad += (not ok)
    if len(set(got.values())) != 1:
        print("%-40s implementations differ in the whole note" % title)
        bad += 1
sys.exit(1 if bad else 0)
