# w06-c14: start-time bench of the guard row's registered `sh -c` command, old revision against the working tree, alternating arms, with `sh -c :` and `python3 -S -I -c pass` as floors in the same loop; inputs: old revision (default 6c826d3), N (default 60), the same ordinary Bash event on stdin for every start; outputs: median, p10, p90 of each arm, median and p10/p90 of the pairwise (old - new) difference, the number of pairs where new is faster, and the load average before and after, on stdout
import json, os, shutil, statistics as st, subprocess, sys, time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
old_rev = sys.argv[1] if len(sys.argv) > 1 else "6c826d3"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 60
W = "/private/tmp/murmuration-w06/author-w06-7/bench"
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
def cmd(root):
    d = json.load(open(root + "/hooks/hooks.json"))
    return [h["command"] for g in d["hooks"]["PreToolUse"] if g["matcher"] == "Bash" for h in g["hooks"]][0]
ev = json.dumps(dict(tool_name="Bash", tool_input={"command": "git status --short && echo $(date +%s)"}, cwd="/tmp"))
arms = {t: ["sh", "-c", cmd(r)] for t, r in roots.items()}
arms["sh"] = ["sh", "-c", ":"]; arms["py"] = ["sh", "-c", "python3 -S -I -c pass"]
envs = {t: dict(os.environ, CLAUDE_PLUGIN_ROOT=roots.get(t, roots["new"])) for t in arms}
print("old:", arms["old"][2]); print("new:", arms["new"][2])
load0 = os.getloadavg()
ms = {t: [] for t in arms}
def once(t):
    t0 = time.perf_counter(); subprocess.run(arms[t], input=ev, text=True, capture_output=True, env=envs[t]); return (time.perf_counter() - t0) * 1000
for t in arms: once(t); once(t)       # warm
for i in range(N):
    order = ["old", "new", "sh", "py"] if i % 2 == 0 else ["py", "sh", "new", "old"]
    for t in order: ms[t].append(once(t))
load1 = os.getloadavg()
q = lambda v, p: sorted(v)[min(len(v) - 1, int(p * len(v)))]
for t in arms:
    print("%-4s n=%d median %.1f p10 %.1f p90 %.1f ms" % (t, N, st.median(ms[t]), q(ms[t], .1), q(ms[t], .9)))
d = [a - b for a, b in zip(ms["old"], ms["new"])]
print("old - new per pair: median %.1f p10 %.1f p90 %.1f ms; new faster in %d of %d pairs" % (st.median(d), q(d, .1), q(d, .9), sum(x > 0 for x in d), N))
print("load average (1, 5, 15 min) before %s, after %s; cores %d" % (tuple(round(x, 2) for x in load0), tuple(round(x, 2) for x in load1), os.cpu_count()))
