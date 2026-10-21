# w06-c13: runs every registered E3 case (v0 attacks, ordinary, mention-only and evasion lists; v1, v2 and v3 case files; the exact incident and handback texts) offline through decide() of two revisions of scripts/permission_guard.py and prints the cases whose outcome differs; inputs: two git revisions (old new), default 071fc53 and the working tree; outputs: counts and the differing cases on stdout. Usage: python3 -I __instrumenta__/w06c13_decide_diff.py [old_rev] [new_rev|WORKTREE]
import importlib.util, json, os, shutil, subprocess, sys, tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LISTS = os.path.join(REPO, "__reports__", "wave-06", "author-w06-5")
old_rev = sys.argv[1] if len(sys.argv) > 1 else "071fc53"
new_rev = sys.argv[2] if len(sys.argv) > 2 else "WORKTREE"
tmp = tempfile.mkdtemp()


def load(rev, name):
    path = os.path.join(REPO, "scripts", "permission_guard.py") if rev == "WORKTREE" else os.path.join(tmp, name + ".py")
    if rev != "WORKTREE":
        open(path, "w").write(subprocess.run(["git", "-C", REPO, "show", "%s:scripts/permission_guard.py" % rev], capture_output=True, text=True, check=True).stdout)
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


old, new = load(old_rev, "pg_old"), load(new_rev, "pg_new")
T = tmp + "/arena"
for d in ("h6", "scripts", "out", "decoy/.claude"):
    os.makedirs(T + "/" + d)
src = subprocess.run(["git", "-C", REPO, "show", "071fc53:scripts/handback.py"], capture_output=True, text=True, check=True).stdout
guard_src = subprocess.run(["git", "-C", REPO, "show", "071fc53:scripts/permission_guard.py"], capture_output=True, text=True, check=True).stdout
open(T + "/h6/handback.py", "w").write(src)
open(T + "/h6/permission_guard.py", "w").write(guard_src)
open(T + "/scripts/hello.py", "w").write("print('hello')\n")
incident = subprocess.run(["git", "-C", REPO, "show", "c4aaebb:__instrumenta__/w06c3_run_all.py"], capture_output=True, text=True, check=True).stdout
cases = []
for name in ("e3_attacks", "e3_ordinary", "e3_mention", "e3_evasions", "e3v1_cases", "e3v2_cases", "e3v3_cases"):
    for c in json.loads(open("%s/%s.json" % (LISTS, name)).read().replace("{T}", T)):
        inp = c.get("input")
        if inp:
            inp = {k: (incident if v == "{INCIDENT}" else src if v == "{HANDBACK}" else v) for k, v in inp.items()}
        cases.append((name + ":" + c["id"], dict(tool_name=c["tool"], tool_input=inp if inp else {"command": c["command"]}, cwd=T)))
diff, n_den = [], 0
for cid, ev in cases:
    a, b = bool(old.decide(ev)), bool(new.decide(ev))
    n_den += b
    if a != b:
        diff.append((cid, "old %s -> new %s" % ("deny" if a else "allow", "deny" if b else "allow")))
print("cases %d, denied by new %d, outcomes that differ from %s: %d" % (len(cases), n_den, old_rev, len(diff)))
for d in diff:
    print(" ", *d)
extra = [("grep -n it's f; claude -p hi --dangerously-skip-permissions", True), ("echo '{}'>.claude/settings.json", True), ("cp .claude/settings.local.json /tmp/bak", False)]
for c, want in extra:
    ev = dict(tool_name="Bash", tool_input={"command": c}, cwd="/h/proj")
    print("fixed case: old %s new %s (want %s) | %s" % (bool(old.decide(ev)), bool(new.decide(ev)), want, c))
shutil.rmtree(tmp)
