# w06-c14: runs events through the guard row's registered `sh -c` command string of two trees (old = git revision, new = working tree), as the hook runs it (event on stdin, MURMURATION_GUARD_LOG set), and compares stdout, exit code and the log line per event; inputs: old revision (default 6c826d3), --sample N recorded lab Bash/Write/Edit calls (seed 0; every call the old guard denies is added); outputs: counts and every differing event on stdout; work folder under /private/tmp/murmuration-w06/author-w06-7/cmd_equal
import glob, json, os, random, shutil, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LISTS = REPO + "/__reports__/wave-06/author-w06-5"
old_rev = sys.argv[1] if len(sys.argv) > 1 else "6c826d3"
N = int(sys.argv[sys.argv.index("--sample") + 1]) if "--sample" in sys.argv else 400
W = "/private/tmp/murmuration-w06/author-w06-7/cmd_equal"
shutil.rmtree(W, ignore_errors=True)
roots = {}
for tag in ("old", "new"):
    r = roots[tag] = "%s/%s" % (W, tag)
    os.makedirs(r + "/hooks"); os.makedirs(r + "/scripts")
    for f in ("hooks/hooks.json", "scripts/permission_guard.py"):
        if tag == "old":
            open("%s/%s" % (r, f), "w").write(subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (old_rev, f)], capture_output=True, text=True, check=True).stdout)
        else:
            shutil.copy("%s/%s" % (REPO, f), "%s/%s" % (r, f))

def bash_cmd(root):
    d = json.load(open(root + "/hooks/hooks.json"))
    cs = [h["command"] for g in d["hooks"]["PreToolUse"] if g["matcher"] == "Bash" for h in g["hooks"]]
    assert len(cs) == 1 and "permission_guard" in cs[0]
    return cs[0]
cmds = {t: bash_cmd(r) for t, r in roots.items()}
print("old command:", cmds["old"]); print("new command:", cmds["new"])

T = W + "/arena"
for d in ("h6", "scripts", "out", "decoy/.claude"):
    os.makedirs(T + "/" + d)
sh = lambda rev, p: subprocess.run(["git", "-C", REPO, "show", rev + ":" + p], capture_output=True, text=True, check=True).stdout
src, incident = sh("071fc53", "scripts/handback.py"), sh("c4aaebb", "__instrumenta__/w06c3_run_all.py")
open(T + "/h6/handback.py", "w").write(src); open(T + "/h6/permission_guard.py", "w").write(sh("071fc53", "scripts/permission_guard.py")); open(T + "/scripts/hello.py", "w").write("print('hello')\n")
events = []
for name in ("e3_attacks", "e3_ordinary", "e3_mention", "e3_evasions", "e3v1_cases", "e3v2_cases", "e3v3_cases"):
    for c in json.loads(open("%s/%s.json" % (LISTS, name)).read().replace("{T}", T)):
        inp = c.get("input")
        if inp:
            inp = {k: (incident if v == "{INCIDENT}" else src if v == "{HANDBACK}" else v) for k, v in inp.items()}
        events.append((name + ":" + c["id"], dict(tool_name=c["tool"], tool_input=inp if inp else {"command": c["command"]}, cwd=T)))
n_reg = len(events)
for raw in ("", "not json", "[]", json.dumps({"tool_name": "Bash", "tool_input": None})):
    events.append(("malformed:%r" % raw[:12], raw))
# recorded lab calls
sys.path.insert(0, os.path.join(roots["old"], "scripts"))
import importlib.util
spec = importlib.util.spec_from_file_location("pg_old", roots["old"] + "/scripts/permission_guard.py"); G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
P = os.path.expanduser("~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration")
rec, seen = [], set()
for s in ("-blissful-villani-34edd8", "-lab-system-optimization-1aa673", "-murmuration-system-optimization-8cff9e", "-murmuration-wave-4-3417be"):
    for f in sorted(glob.glob(P + s + "/**/*.jsonl", recursive=True)):
        for line in open(f, errors="replace"):
            if '"tool_use"' not in line: continue
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("type") != "assistant": continue
            for b in (m.get("message", {}).get("content") or []):
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Bash", "Write", "Edit") and b["id"] not in seen:
                    seen.add(b["id"]); rec.append(dict(tool_name=b["name"], tool_input=b["input"], cwd=m.get("cwd") or ""))
den = [e for e in rec if G.decide(e)]
rest = [e for e in rec if not G.decide(e)]
random.Random(0).shuffle(rest)
pick = den + rest[:N]
events += [("recorded%d" % i, e) for i, e in enumerate(pick)]
print("registered %d, malformed 4, recorded calls %d (old guard denies %d; sampled %d allowed): %d events" % (n_reg, len(rec), len(den), min(N, len(rest)), len(events)))

def run(tag, ev):
    log = "%s/%s.log" % (W, tag)
    if os.path.exists(log): os.remove(log)
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=roots[tag], MURMURATION_GUARD_LOG=log)
    p = subprocess.run(["sh", "-c", cmds[tag]], input=ev if isinstance(ev, str) else json.dumps(ev), text=True, capture_output=True, env=env)
    return p.returncode, p.stdout, p.stderr, open(log).read() if os.path.exists(log) else None
diff, deny = [], 0
for cid, ev in events:
    a, b = run("old", ev), run("new", ev)
    deny += bool(b[1])
    if a != b:
        diff.append((cid, a, b))
print("events %d, denied by new %d, events whose (exit code, stdout, stderr, log line) differ: %d" % (len(events), deny, len(diff)))
for d in diff[:10]:
    print(" ", d[0], d[1][:3], d[2][:3])
