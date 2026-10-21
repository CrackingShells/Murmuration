# w06-c14 verifier check: alternating bench of the Bash-row command string of two plugin trees through `sh -c` (one ordinary event on stdin), and an offline fail-closed probe (script unreadable, script crashing); inputs: old tree, new tree, number of pairs; output: medians and pair counts on stdout; independent of the author's w06c14_bench_guard.py
import json, os, shutil, statistics as st, subprocess, sys, tempfile, time

old, new, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
cmds = {}
for t in (old, new):
    h = json.load(open(t + "/hooks/hooks.json"))["hooks"]["PreToolUse"]
    cmds[t] = next(hk["command"] for g in h if g["matcher"] == "Bash" for hk in g["hooks"])
ev = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status --short"}})


def once(t):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=t)
    env.pop("MURMURATION_GUARD_LOG", None)
    t0 = time.perf_counter()
    subprocess.run(["sh", "-c", cmds[t]], input=ev, text=True, capture_output=True, env=env)
    return (time.perf_counter() - t0) * 1000


for t in (old, new):
    once(t); once(t)
d, a, b = [], [], []
for i in range(n):
    order = (old, new) if i % 2 == 0 else (new, old)
    r = {t: once(t) for t in order}
    a.append(r[old]); b.append(r[new]); d.append(r[old] - r[new])
print("pairs %d  old median %.1f ms  new median %.1f ms  old-new per pair median %.1f ms  new faster in %d of %d" % (n, st.median(a), st.median(b), st.median(d), sum(x > 0 for x in d), n))
print("load average", os.getloadavg())
# fail closed offline: the exit code the platform sees when the script cannot run (platform turns non-0/2 into non-blocking; 2 or onFailure block into block)
for t in (old, new):
    tmp = tempfile.mkdtemp()
    os.makedirs(tmp + "/scripts")
    for label, setup in (("unreadable", lambda p: (shutil.copy(t + "/scripts/permission_guard.py", p), os.chmod(p, 0))), ("crashing", lambda p: open(p, "w").write("raise SystemExit(1/0)\n")), ("missing", lambda p: None)):
        p = tmp + "/scripts/permission_guard.py"
        if os.path.exists(p):
            os.chmod(p, 0o644); os.remove(p)
        setup(p)
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=tmp)
        r = subprocess.run(["sh", "-c", cmds[t]], input=ev, text=True, capture_output=True, env=env)
        print("fail-closed probe (%s tree) %-10s exit %d stdout %r" % ("old" if t == old else "new", label, r.returncode, r.stdout))
    shutil.rmtree(tmp, ignore_errors=True)
