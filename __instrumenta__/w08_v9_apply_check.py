# Applies the proposed PI decision sections (markdown blocks) to a scratch copy of __pondus__ and reports which claim lines change, old vs new lab_status.py; inputs: lab root, new lab_status.py, proposed_decision_sections.md; output: stdout diff of claim lines.
import os, re, shutil, subprocess, sys, tempfile
lab, new_ls, props = sys.argv[1:4]
old_src = subprocess.run(["git", "-C", lab, "show", "abe428f:scripts/lab_status.py"], capture_output=True, text=True, check=True).stdout
tmp = tempfile.mkdtemp(dir="/private/tmp/murmuration-w08/reproducer-w08-9")
proj = os.path.join(tmp, "proj")
for d in ("__pondus__", "__statera__", "__scrupuli__"):
    shutil.copytree(os.path.join(lab, d), os.path.join(proj, d), ignore=shutil.ignore_patterns("handbacks", "harness.jsonl"))
open(os.path.join(tmp, "old.py"), "w").write(old_src)
env = dict(os.environ, CLAUDE_PROJECT_DIR=proj)
def run(script):
    r = subprocess.run([sys.executable, script, "--project", proj], capture_output=True, text=True, env=env, cwd=tmp)
    return r.stdout
def claims(out):
    return [l for l in out.splitlines() if re.match(r"- w\d\d-c\d+", l) or l.startswith("!")]
old0 = claims(run(os.path.join(tmp, "old.py")))
new0 = claims(run(new_ls))
print("old vs new, no sections: identical lines:", old0 == new0, len(old0))
txt = open(props).read()
blocks = re.findall(r"^## (w\d\d-c\d+)\s*\n+```markdown\n(.*?)```", txt, re.S | re.M)
print("blocks:", [b[0] for b in blocks])
for cid, body in blocks:
    with open(os.path.join(proj, "__pondus__", cid + ".md"), "a") as f:
        f.write("\n" + body)
new1 = claims(run(new_ls))
chg = [(a, b) for a, b in zip(new0, new1) if a != b]
print("lines", len(new0), len(new1), "changed", len(chg))
for a, b in chg:
    print("  -", a[:150]); print("  +", b[:150])
print("warnings before/after same:", [l for l in new0 if l.startswith("!")] == [l for l in new1 if l.startswith("!")])
changed_files = sorted(f for f in os.listdir(os.path.join(proj, "__pondus__")) if open(os.path.join(proj, "__pondus__", f)).read() != open(os.path.join(lab, "__pondus__", f)).read())
print("files changed:", changed_files)
print("scratch:", tmp)
